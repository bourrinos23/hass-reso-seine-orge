"""Client API pour RESO Seine & Orge."""
from __future__ import annotations

import uuid
from datetime import datetime, timezone, timedelta

import requests

from .const import BASE_URL, SITE_URL, ACCESS_KEY, CLIENT_ID


class ResoApiError(Exception):
    """Erreur générique de l'API RESO."""


class ResoAuthError(ResoApiError):
    """Erreur d'authentification."""


class ResoClient:
    """Client pour l'API RESO Seine & Orge."""

    def __init__(self, email: str, password: str, contrat: str) -> None:
        self._email = email
        self._password = password
        self._contrat = contrat
        self._session = requests.Session()
        self._auth_token: str | None = None
        self._conv_id: str | None = None

    def _base_headers(self) -> dict:
        return {
            "Accept": "application/json, text/plain, */*",
            "Content-Type": "application/json;charset=UTF-8",
            "ConversationId": self._conv_id or "",
            "Token": self._auth_token or ACCESS_KEY,
            "Origin": SITE_URL[:-1],
            "Referer": SITE_URL,
        }

    def authenticate(self) -> None:
        """Authentification en 3 étapes."""
        self._conv_id = "JS-WEB-Netscape-" + str(uuid.uuid4())

        # Étape 0 : cookie BIGip
        self._session.get(SITE_URL, timeout=15)

        # Étape 1 : openToken
        headers = self._base_headers()
        headers["Token"] = ACCESS_KEY
        r1 = self._session.post(
            BASE_URL + "/Acces/generateToken",
            json={
                "AccessKey": ACCESS_KEY,
                "ClientId": CLIENT_ID,
                "ConversationId": self._conv_id,
            },
            headers=headers,
            timeout=15,
        )
        if r1.status_code != 200:
            raise ResoAuthError(f"generateToken échoué ({r1.status_code})")
        open_token = r1.json().get("token")

        # Étape 2 : authentification
        headers["Token"] = open_token
        r2 = self._session.post(
            BASE_URL + "/Utilisateur/authentification",
            json={"identifiant": self._email, "motDePasse": self._password},
            headers=headers,
            timeout=15,
        )
        if r2.status_code != 200:
            raise ResoAuthError(f"Authentification échouée ({r2.status_code}) - vérifiez email/mot de passe")

        data = r2.json()
        self._auth_token = data.get("tokenAuthentique")
        if not self._auth_token:
            raise ResoAuthError("Token authentique non reçu")

        # Récupérer le numéro de contrat si non fourni
        if not self._contrat:
            try:
                self._contrat = data["utilisateurInfo"]["contrats"][0]["numeroContrat"]
            except (KeyError, IndexError):
                raise ResoAuthError("Impossible de récupérer le numéro de contrat")

    def get_daily_consumption(self, nb_jours: int = 30) -> list[dict]:
        """Récupère les consommations journalières."""
        if not self._auth_token:
            self.authenticate()

        now = datetime.now(timezone.utc)
        ts_fin = int(now.timestamp())
        ts_debut = int((now - timedelta(days=nb_jours)).timestamp())

        r = self._session.get(
            f"{BASE_URL}/Consommation/listeConsommationsInstanceAlerteChart"
            f"/{self._contrat}/{ts_debut}/{ts_fin}/JOURNEE/true",
            headers=self._base_headers(),
            timeout=15,
        )

        if r.status_code == 401:
            # Token expiré, on ré-authentifie
            self._auth_token = None
            self.authenticate()
            r = self._session.get(
                f"{BASE_URL}/Consommation/listeConsommationsInstanceAlerteChart"
                f"/{self._contrat}/{ts_debut}/{ts_fin}/JOURNEE/true",
                headers=self._base_headers(),
                timeout=15,
            )

        if r.status_code != 200:
            raise ResoApiError(f"Erreur consommations ({r.status_code}): {r.text[:200]}")

        consommations = r.json().get("consommations", [])
        if not consommations:
            raise ResoApiError("Aucune donnée de consommation disponible")

        return sorted(consommations, key=lambda x: x["dateReleve"], reverse=True)

    def test_connection(self) -> str:
        """Teste la connexion et retourne le numéro de contrat."""
        self.authenticate()
        return self._contrat
