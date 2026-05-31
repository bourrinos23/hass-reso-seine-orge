# RESO Seine & Orge - Intégration Home Assistant

[![hacs_badge](https://img.shields.io/badge/HACS-Custom-orange.svg)](https://github.com/hacs/integration)

Intégration Home Assistant pour suivre votre consommation d'eau **RESO Seine & Orge** (régie publique qui dessert une partie de l'Essonne et du Val-de-Marne depuis janvier 2024/2025), disponible sur le portail [ael.eauxseinebievreorge.fr](https://ael.eauxseinebievreorge.fr).

> ⚠️ Cette intégration nécessite un compteur avec **télérelevé** activé par RESO.

---

## Capteurs disponibles

### 💧 Consommation

| Capteur | Description | Unité |
|---------|-------------|-------|
| `sensor.reso_eau_index` | Index du compteur | m³ |
| `sensor.reso_eau_consommation_journaliere` | Consommation du dernier jour relevé | m³ |
| `sensor.reso_eau_consommation_7_jours` | Consommation sur 7 jours glissants | m³ |
| `sensor.reso_eau_consommation_30_jours` | Consommation sur 30 jours glissants | m³ |

### 💶 Coûts estimés (TTC)

| Capteur | Description | Unité |
|---------|-------------|-------|
| `sensor.reso_eau_potable_cout_journalier` | Coût eau potable du jour (abonnement + conso) | € |
| `sensor.reso_assainissement_cout_journalier` | Coût assainissement du jour | € |
| `sensor.reso_organismes_publics_cout_journalier` | Coût organismes publics du jour | € |
| `sensor.reso_eau_cout_total_journalier` | Coût total TTC du jour | € |
| `sensor.reso_eau_cout_total_30_jours` | Coût total TTC sur 30 jours | € |

Les données sont rafraîchies toutes les **3 heures** (les relevés RESO sont disponibles avec ~24h de décalage).

---

## Prérequis

- Un abonnement RESO Seine & Orge actif
- Un compteur avec **télérelevé** activé
- HACS installé sur Home Assistant

---

## Installation via HACS

1. Dans Home Assistant, allez dans **HACS → Intégrations**
2. Cliquez sur le menu ⋮ → **Dépôts personnalisés**
3. Ajoutez l'URL : `https://github.com/bourrinos23/hass-reso-seine-orge`
4. Catégorie : **Intégration**
5. Cliquez sur **RESO Seine & Orge** puis **Télécharger**
6. Redémarrez Home Assistant

## Configuration

1. Allez dans **Paramètres → Appareils et services → Ajouter une intégration**
2. Recherchez **RESO Seine & Orge**
3. Entrez votre email et mot de passe du portail RESO
4. Le numéro de contrat est détecté automatiquement

---

## Configuration des tarifs

Les tarifs sont configurables à tout moment sans réinstallation :

**Paramètres → Appareils et services → RESO Seine & Orge → Configurer**

La configuration se fait en **3 écrans** :

1. **Eau Potable** — abonnement annuel HT, prix du m³ HT, TVA
2. **Assainissement** — redevances territoriale, syndicale et interdépartementale
3. **Organismes Publics** — VNF, EPTB, prélèvement ressource, AESN (3 postes)

> 💡 Toutes ces valeurs sont disponibles sur votre facture RESO dans le tableau "Votre facture détaillée". Les valeurs par défaut correspondent aux tarifs 2025.

### Tarifs par défaut (2025)

| Poste | Prix HT | TVA |
|-------|---------|-----|
| Abonnement eau potable | 39,60 €/an | 5,5% |
| Consommation eau potable | 1,80 €/m³ | 5,5% |
| Redevance territoriale assainissement | 0,7370 €/m³ | 0% |
| Redevance syndicale assainissement | 0,3700 €/m³ | 10% |
| Redevance interdépartementale assainissement | 0,9950 €/m³ | 10% |
| VNF | 0,0110 €/m³ | 5,5% |
| EPTB Seine Grands Lacs | 0,0091 €/m³ | 5,5% |
| Prélèvement sur la ressource | 0,0600 €/m³ | 5,5% |
| AESN Redevance consommation | 0,4600 €/m³ | 5,5% |
| AESN Performance réseaux eau potable | 0,0170 €/m³ | 5,5% |
| AESN Performance réseaux assainissement | 0,0267 €/m³ | 10% |

Prix TTC tout compris : **~4,76 €/m³**

---

## Ajout au dashboard Énergie

Pour intégrer dans le dashboard Énergie de Home Assistant :

1. **Paramètres → Tableau de bord Énergie**
2. Section **Eau** → **Ajouter une consommation d'eau**
3. Sélectionnez `sensor.reso_eau_index`

---

## Compatibilité

- Communes desservies par **RESO Seine & Orge** (Essonne, Val-de-Marne)
- Nécessite un abonnement actif avec compteur télérelevé
- Home Assistant 2023.1.0 minimum

---

## Contribution

Les issues et pull requests sont les bienvenus !  
Partagé sur [HACF - Home Assistant Communauté Francophone](https://hacf.fr)

---

## Remerciements

Intégration développée par reverse-engineering de l'API REST du portail client RESO.  
Inspiré des intégrations [Veolia](https://github.com/home-assistant-custom-components/veolia-custom-component) et [Suez](https://www.home-assistant.io/integrations/suez_water/).
