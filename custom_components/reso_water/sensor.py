"""Capteurs de consommation d'eau RESO Seine & Orge."""
from __future__ import annotations
from datetime import timedelta
import logging

from homeassistant.components.sensor import SensorDeviceClass, SensorEntity, SensorStateClass
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity, DataUpdateCoordinator, UpdateFailed

from .api import ResoClient, ResoApiError
from .const import (
    DOMAIN, CONF_EMAIL, CONF_PASSWORD, CONF_CONTRAT, SCAN_INTERVAL_HOURS,
    CONF_EP_ABONNEMENT, CONF_EP_CONSO, CONF_EP_TVA,
    CONF_AS_TERRITORIALE, CONF_AS_SYNDICALE, CONF_AS_INTERDEP,
    CONF_OP_VNF, CONF_OP_EPTB, CONF_OP_PREL_RESSOURCE,
    CONF_OP_AESN_CONSO, CONF_OP_AESN_PERF_EP, CONF_OP_AESN_PERF_AS,
    DEFAULT_EP_ABONNEMENT, DEFAULT_EP_CONSO, DEFAULT_EP_TVA,
    DEFAULT_AS_TERRITORIALE, DEFAULT_AS_SYNDICALE, DEFAULT_AS_INTERDEP,
    DEFAULT_OP_VNF, DEFAULT_OP_EPTB, DEFAULT_OP_PREL_RESSOURCE,
    DEFAULT_OP_AESN_CONSO, DEFAULT_OP_AESN_PERF_EP, DEFAULT_OP_AESN_PERF_AS,
    TVA_0, TVA_55, TVA_10,
)

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry, async_add_entities: AddEntitiesCallback) -> None:
    client = ResoClient(
        email=entry.data[CONF_EMAIL],
        password=entry.data[CONF_PASSWORD],
        contrat=entry.data[CONF_CONTRAT],
    )
    coordinator = ResoDataUpdateCoordinator(hass, client)
    await coordinator.async_config_entry_first_refresh()
    hass.data[DOMAIN][entry.entry_id] = coordinator

    async_add_entities([
        ResoIndexSensor(coordinator, entry),
        ResoConsommationJourSensor(coordinator, entry),
        ResoConsommation7jSensor(coordinator, entry),
        ResoConsommation30jSensor(coordinator, entry),
        ResoCoutEauPotableJourSensor(coordinator, entry),
        ResoCoutAssainissementJourSensor(coordinator, entry),
        ResoCoutOrganismesJourSensor(coordinator, entry),
        ResoCoutTotalJourSensor(coordinator, entry),
        ResoCoutTotal30jSensor(coordinator, entry),
    ])


class ResoDataUpdateCoordinator(DataUpdateCoordinator):
    def __init__(self, hass, client):
        super().__init__(hass, _LOGGER, name="RESO Water", update_interval=timedelta(hours=SCAN_INTERVAL_HOURS))
        self._client = client

    async def _async_update_data(self):
        try:
            return await self.hass.async_add_executor_job(self._client.get_daily_consumption, 30)
        except ResoApiError as err:
            raise UpdateFailed(f"Erreur API RESO: {err}") from err


class ResoBaseSensor(CoordinatorEntity, SensorEntity):
    def __init__(self, coordinator, entry):
        super().__init__(coordinator)
        self._entry = entry
        self._contrat = entry.data[CONF_CONTRAT]

    @property
    def device_info(self):
        return {
            "identifiers": {(DOMAIN, self._contrat)},
            "name": f"Compteur eau RESO ({self._contrat})",
            "manufacturer": "RESO Seine & Orge",
            "model": "Télérelevé",
        }

    @property
    def _dernier(self):
        return self.coordinator.data[0] if self.coordinator.data else None

    def _opt(self, key, default):
        return self._entry.options.get(key, default)

    def _volume_jour(self):
        d = self._dernier
        return d.get("volumeConsoEnM3", 0) if d else 0

    def _volume_30j(self):
        if not self.coordinator.data:
            return 0
        return sum(c.get("volumeConsoEnM3", 0) for c in self.coordinator.data)

    def _cout_ep(self, volume):
        """Coût Eau Potable TTC."""
        abonnement_jour = self._opt(CONF_EP_ABONNEMENT, DEFAULT_EP_ABONNEMENT) / 365
        conso = volume * self._opt(CONF_EP_CONSO, DEFAULT_EP_CONSO)
        tva = 1 + self._opt(CONF_EP_TVA, DEFAULT_EP_TVA) / 100
        return (abonnement_jour + conso) * tva

    def _cout_as(self, volume):
        """Coût Assainissement TTC."""
        terr  = volume * self._opt(CONF_AS_TERRITORIALE, DEFAULT_AS_TERRITORIALE) * (1 + TVA_0  / 100)
        synd  = volume * self._opt(CONF_AS_SYNDICALE,    DEFAULT_AS_SYNDICALE)    * (1 + TVA_10 / 100)
        inter = volume * self._opt(CONF_AS_INTERDEP,     DEFAULT_AS_INTERDEP)     * (1 + TVA_10 / 100)
        return terr + synd + inter

    def _cout_op(self, volume):
        """Coût Organismes Publics TTC."""
        tva55 = 1 + TVA_55 / 100
        tva10 = 1 + TVA_10 / 100
        return (
            volume * self._opt(CONF_OP_VNF,            DEFAULT_OP_VNF)            * tva55 +
            volume * self._opt(CONF_OP_EPTB,           DEFAULT_OP_EPTB)           * tva55 +
            volume * self._opt(CONF_OP_PREL_RESSOURCE, DEFAULT_OP_PREL_RESSOURCE) * tva55 +
            volume * self._opt(CONF_OP_AESN_CONSO,     DEFAULT_OP_AESN_CONSO)     * tva55 +
            volume * self._opt(CONF_OP_AESN_PERF_EP,   DEFAULT_OP_AESN_PERF_EP)   * tva55 +
            volume * self._opt(CONF_OP_AESN_PERF_AS,   DEFAULT_OP_AESN_PERF_AS)   * tva10
        )


# ── Capteurs de consommation ─────────────────────────────────

class ResoIndexSensor(ResoBaseSensor):
    _attr_device_class = SensorDeviceClass.WATER
    _attr_state_class = SensorStateClass.TOTAL_INCREASING
    _attr_native_unit_of_measurement = "m³"
    _attr_icon = "mdi:water"

    def __init__(self, coordinator, entry):
        super().__init__(coordinator, entry)
        self._attr_unique_id = f"reso_{self._contrat}_index"
        self._attr_name = "RESO Eau Index"

    @property
    def native_value(self):
        d = self._dernier
        return round(d.get("valeurIndex", 0) / 1000, 3) if d else None

    @property
    def extra_state_attributes(self):
        d = self._dernier
        if not d:
            return {}
        return {
            "date_dernier_releve": d.get("dateReleve", "")[:10],
            "type_releve": d.get("typeAgregat", ""),
            "index_litres": d.get("valeurIndex", 0),
            "contrat": self._contrat,
        }


class ResoConsommationJourSensor(ResoBaseSensor):
    _attr_device_class = SensorDeviceClass.WATER
    _attr_state_class = SensorStateClass.MEASUREMENT
    _attr_native_unit_of_measurement = "m³"
    _attr_icon = "mdi:water-outline"

    def __init__(self, coordinator, entry):
        super().__init__(coordinator, entry)
        self._attr_unique_id = f"reso_{self._contrat}_conso_jour"
        self._attr_name = "RESO Eau Consommation Journalière"

    @property
    def native_value(self):
        return round(self._volume_jour(), 3)

    @property
    def extra_state_attributes(self):
        d = self._dernier
        if not d:
            return {}
        return {"date": d.get("dateReleve", "")[:10], "volume_litres": d.get("volumeConsoEnLitres", 0), "type_releve": d.get("typeAgregat", "")}


class ResoConsommation7jSensor(ResoBaseSensor):
    _attr_device_class = SensorDeviceClass.WATER
    _attr_state_class = SensorStateClass.MEASUREMENT
    _attr_native_unit_of_measurement = "m³"
    _attr_icon = "mdi:calendar-week"

    def __init__(self, coordinator, entry):
        super().__init__(coordinator, entry)
        self._attr_unique_id = f"reso_{self._contrat}_conso_7j"
        self._attr_name = "RESO Eau Consommation 7 jours"

    @property
    def native_value(self):
        if not self.coordinator.data:
            return None
        return round(sum(c.get("volumeConsoEnM3", 0) for c in self.coordinator.data[:7]), 3)


class ResoConsommation30jSensor(ResoBaseSensor):
    _attr_device_class = SensorDeviceClass.WATER
    _attr_state_class = SensorStateClass.MEASUREMENT
    _attr_native_unit_of_measurement = "m³"
    _attr_icon = "mdi:calendar-month"

    def __init__(self, coordinator, entry):
        super().__init__(coordinator, entry)
        self._attr_unique_id = f"reso_{self._contrat}_conso_30j"
        self._attr_name = "RESO Eau Consommation 30 jours"

    @property
    def native_value(self):
        return round(self._volume_30j(), 3) if self.coordinator.data else None


# ── Capteurs de coût ─────────────────────────────────────────

class ResoCoutEauPotableJourSensor(ResoBaseSensor):
    _attr_device_class = SensorDeviceClass.MONETARY
    _attr_state_class = SensorStateClass.MEASUREMENT
    _attr_native_unit_of_measurement = "EUR"
    _attr_icon = "mdi:water-pump"

    def __init__(self, coordinator, entry):
        super().__init__(coordinator, entry)
        self._attr_unique_id = f"reso_{self._contrat}_cout_ep_jour"
        self._attr_name = "RESO Eau Potable Coût Journalier"

    @property
    def native_value(self):
        return round(self._cout_ep(self._volume_jour()), 4)

    @property
    def extra_state_attributes(self):
        return {
            "abonnement_annuel_ht": self._opt(CONF_EP_ABONNEMENT, DEFAULT_EP_ABONNEMENT),
            "prix_m3_ht": self._opt(CONF_EP_CONSO, DEFAULT_EP_CONSO),
            "tva_pct": self._opt(CONF_EP_TVA, DEFAULT_EP_TVA),
        }


class ResoCoutAssainissementJourSensor(ResoBaseSensor):
    _attr_device_class = SensorDeviceClass.MONETARY
    _attr_state_class = SensorStateClass.MEASUREMENT
    _attr_native_unit_of_measurement = "EUR"
    _attr_icon = "mdi:pipe"

    def __init__(self, coordinator, entry):
        super().__init__(coordinator, entry)
        self._attr_unique_id = f"reso_{self._contrat}_cout_as_jour"
        self._attr_name = "RESO Assainissement Coût Journalier"

    @property
    def native_value(self):
        return round(self._cout_as(self._volume_jour()), 4)

    @property
    def extra_state_attributes(self):
        return {
            "territoriale_ht": self._opt(CONF_AS_TERRITORIALE, DEFAULT_AS_TERRITORIALE),
            "syndicale_ht": self._opt(CONF_AS_SYNDICALE, DEFAULT_AS_SYNDICALE),
            "interdep_ht": self._opt(CONF_AS_INTERDEP, DEFAULT_AS_INTERDEP),
        }


class ResoCoutOrganismesJourSensor(ResoBaseSensor):
    _attr_device_class = SensorDeviceClass.MONETARY
    _attr_state_class = SensorStateClass.MEASUREMENT
    _attr_native_unit_of_measurement = "EUR"
    _attr_icon = "mdi:bank"

    def __init__(self, coordinator, entry):
        super().__init__(coordinator, entry)
        self._attr_unique_id = f"reso_{self._contrat}_cout_op_jour"
        self._attr_name = "RESO Organismes Publics Coût Journalier"

    @property
    def native_value(self):
        return round(self._cout_op(self._volume_jour()), 4)

    @property
    def extra_state_attributes(self):
        return {
            "vnf_ht": self._opt(CONF_OP_VNF, DEFAULT_OP_VNF),
            "eptb_ht": self._opt(CONF_OP_EPTB, DEFAULT_OP_EPTB),
            "prel_ressource_ht": self._opt(CONF_OP_PREL_RESSOURCE, DEFAULT_OP_PREL_RESSOURCE),
            "aesn_conso_ht": self._opt(CONF_OP_AESN_CONSO, DEFAULT_OP_AESN_CONSO),
            "aesn_perf_ep_ht": self._opt(CONF_OP_AESN_PERF_EP, DEFAULT_OP_AESN_PERF_EP),
            "aesn_perf_as_ht": self._opt(CONF_OP_AESN_PERF_AS, DEFAULT_OP_AESN_PERF_AS),
        }


class ResoCoutTotalJourSensor(ResoBaseSensor):
    _attr_device_class = SensorDeviceClass.MONETARY
    _attr_state_class = SensorStateClass.MEASUREMENT
    _attr_native_unit_of_measurement = "EUR"
    _attr_icon = "mdi:currency-eur"

    def __init__(self, coordinator, entry):
        super().__init__(coordinator, entry)
        self._attr_unique_id = f"reso_{self._contrat}_cout_total_jour"
        self._attr_name = "RESO Eau Coût Total Journalier"

    @property
    def native_value(self):
        v = self._volume_jour()
        return round(self._cout_ep(v) + self._cout_as(v) + self._cout_op(v), 4)

    @property
    def extra_state_attributes(self):
        v = self._volume_jour()
        return {
            "cout_eau_potable_ttc": round(self._cout_ep(v), 4),
            "cout_assainissement_ttc": round(self._cout_as(v), 4),
            "cout_organismes_ttc": round(self._cout_op(v), 4),
            "volume_m3": round(v, 3),
        }


class ResoCoutTotal30jSensor(ResoBaseSensor):
    _attr_device_class = SensorDeviceClass.MONETARY
    _attr_state_class = SensorStateClass.MEASUREMENT
    _attr_native_unit_of_measurement = "EUR"
    _attr_icon = "mdi:currency-eur"

    def __init__(self, coordinator, entry):
        super().__init__(coordinator, entry)
        self._attr_unique_id = f"reso_{self._contrat}_cout_total_30j"
        self._attr_name = "RESO Eau Coût Total 30 jours"

    @property
    def native_value(self):
        v = self._volume_30j()
        ep = self._cout_ep(0) * 29 + self._cout_ep(v)  # abonnement sur 30j + conso
        # Plus simple : on recalcule directement sur 30j
        abonnement_30j = self._opt(CONF_EP_ABONNEMENT, DEFAULT_EP_ABONNEMENT) / 365 * 30
        conso_ep  = v * self._opt(CONF_EP_CONSO, DEFAULT_EP_CONSO)
        ep_ttc    = (abonnement_30j + conso_ep) * (1 + self._opt(CONF_EP_TVA, DEFAULT_EP_TVA) / 100)
        as_ttc    = self._cout_as(v)
        op_ttc    = self._cout_op(v)
        return round(ep_ttc + as_ttc + op_ttc, 2)

    @property
    def extra_state_attributes(self):
        v = self._volume_30j()
        abonnement_30j = self._opt(CONF_EP_ABONNEMENT, DEFAULT_EP_ABONNEMENT) / 365 * 30
        conso_ep = v * self._opt(CONF_EP_CONSO, DEFAULT_EP_CONSO)
        ep_ttc = (abonnement_30j + conso_ep) * (1 + self._opt(CONF_EP_TVA, DEFAULT_EP_TVA) / 100)
        return {
            "cout_eau_potable_ttc": round(ep_ttc, 2),
            "cout_assainissement_ttc": round(self._cout_as(v), 2),
            "cout_organismes_ttc": round(self._cout_op(v), 2),
            "volume_total_m3": round(v, 3),
        }
