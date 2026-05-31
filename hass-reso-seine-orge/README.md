# RESO Seine & Orge - Intégration Home Assistant

[![hacs_badge](https://img.shields.io/badge/HACS-Custom-orange.svg)](https://github.com/hacs/integration)

Intégration Home Assistant pour suivre votre consommation d'eau **RESO Seine & Orge** (anciennement Eau de Paris / Veolia sur ce territoire), disponible sur le portail [ael.eauxseinebievreorge.fr](https://ael.eauxseinebievreorge.fr).

> ⚠️ Cette intégration nécessite un compteur avec **télérelevé** activé par RESO.

---

## Capteurs disponibles

| Capteur | Description | Unité |
|---------|-------------|-------|
| `sensor.reso_eau_index` | Index du compteur | m³ |
| `sensor.reso_eau_consommation_journaliere` | Consommation du dernier jour relevé | m³ |
| `sensor.reso_eau_consommation_7_jours` | Consommation sur 7 jours glissants | m³ |
| `sensor.reso_eau_consommation_30_jours` | Consommation sur 30 jours glissants | m³ |

Les données sont rafraîchies toutes les **3 heures** (les relevés RESO sont disponibles avec un décalage de ~24h).

---

## Installation via HACS

1. Dans Home Assistant, allez dans **HACS → Intégrations**
2. Cliquez sur le menu ⋮ → **Dépôts personnalisés**
3. Ajoutez l'URL : `https://github.com/loic-desaintetienne/hass-reso-seine-orge`
4. Catégorie : **Intégration**
5. Cliquez sur **RESO Seine & Orge** puis **Télécharger**
6. Redémarrez Home Assistant

## Configuration

1. Allez dans **Paramètres → Appareils et services → Ajouter une intégration**
2. Recherchez **RESO Seine & Orge**
3. Entrez votre email et mot de passe du portail RESO
4. Le numéro de contrat est détecté automatiquement

---

## Ajout au dashboard Énergie

Pour suivre votre consommation d'eau dans le dashboard Énergie de Home Assistant :

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

Intégration développée par reverse-engineering de l'API du portail client RESO.  
Inspiré des intégrations [Veolia](https://github.com/home-assistant-custom-components/veolia-custom-component) et [Suez](https://www.home-assistant.io/integrations/suez_water/).
