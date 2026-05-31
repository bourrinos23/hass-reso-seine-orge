"""Capteurs de consommation d'eau RESO Seine & Orge."""
from __future__ import annotations

from datetime import timedelta
import logging

from homeassistant.components.sensor import (
    SensorDeviceClass,
    SensorEntity,
    SensorStateClass,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import (
    CoordinatorEntity,
    DataUpdateCoordinator,
    UpdateFailed,
)

from .api import ResoClient, ResoApiError
from .const import DOMAIN, CONF_EMAIL, CONF_PASSWORD, CONF_CONTRAT, SCAN_INTERVAL_HOURS

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Mise en place des capteurs RESO."""
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
    ])


class ResoDataUpdateCoordinator(DataUpdateCoordinator):
    """Coordinateur de mise à jour des données RESO."""

    def __init__(self, hass: HomeAssistant, client: ResoClient) -> None:
        super().__init__(
            hass,
            _LOGGER,
            name="RESO Water",
            update_interval=timedelta(hours=SCAN_INTERVAL_HOURS),
        )
        self._client = client

    async def _async_update_data(self) -> list[dict]:
        """Récupère les données depuis l'API RESO."""
        try:
            return await self.hass.async_add_executor_job(
                self._client.get_daily_consumption, 30
            )
        except ResoApiError as err:
            raise UpdateFailed(f"Erreur API RESO: {err}") from err


class ResoBaseSensor(CoordinatorEntity, SensorEntity):
    """Classe de base pour les capteurs RESO."""

    def __init__(self, coordinator: ResoDataUpdateCoordinator, entry: ConfigEntry) -> None:
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
    def _dernier_releve(self) -> dict | None:
        if self.coordinator.data:
            return self.coordinator.data[0]
        return None


class ResoIndexSensor(ResoBaseSensor):
    """Capteur d'index du compteur (en m³)."""

    _attr_device_class = SensorDeviceClass.WATER
    _attr_state_class = SensorStateClass.TOTAL_INCREASING
    _attr_native_unit_of_measurement = "m³"
    _attr_icon = "mdi:water"

    def __init__(self, coordinator, entry):
        super().__init__(coordinator, entry)
        self._attr_unique_id = f"reso_{self._contrat}_index"
        self._attr_name = "RESO Eau Index"

    @property
    def native_value(self) -> float | None:
        d = self._dernier_releve
        if d:
            return round(d.get("valeurIndex", 0) / 1000, 3)
        return None

    @property
    def extra_state_attributes(self) -> dict:
        d = self._dernier_releve
        if not d:
            return {}
        return {
            "date_dernier_releve": d.get("dateReleve", "")[:10],
            "type_releve": d.get("typeAgregat", ""),
            "index_litres": d.get("valeurIndex", 0),
            "contrat": self._contrat,
        }


class ResoConsommationJourSensor(ResoBaseSensor):
    """Capteur de consommation du dernier jour relevé."""

    _attr_device_class = SensorDeviceClass.WATER
    _attr_state_class = SensorStateClass.MEASUREMENT
    _attr_native_unit_of_measurement = "m³"
    _attr_icon = "mdi:water-outline"

    def __init__(self, coordinator, entry):
        super().__init__(coordinator, entry)
        self._attr_unique_id = f"reso_{self._contrat}_conso_jour"
        self._attr_name = "RESO Eau Consommation Journalière"

    @property
    def native_value(self) -> float | None:
        d = self._dernier_releve
        if d:
            return round(d.get("volumeConsoEnM3", 0), 3)
        return None

    @property
    def extra_state_attributes(self) -> dict:
        d = self._dernier_releve
        if not d:
            return {}
        return {
            "date": d.get("dateReleve", "")[:10],
            "volume_litres": d.get("volumeConsoEnLitres", 0),
            "type_releve": d.get("typeAgregat", ""),
        }


class ResoConsommation7jSensor(ResoBaseSensor):
    """Capteur de consommation sur 7 jours."""

    _attr_device_class = SensorDeviceClass.WATER
    _attr_state_class = SensorStateClass.MEASUREMENT
    _attr_native_unit_of_measurement = "m³"
    _attr_icon = "mdi:calendar-week"

    def __init__(self, coordinator, entry):
        super().__init__(coordinator, entry)
        self._attr_unique_id = f"reso_{self._contrat}_conso_7j"
        self._attr_name = "RESO Eau Consommation 7 jours"

    @property
    def native_value(self) -> float | None:
        if self.coordinator.data:
            return round(
                sum(c.get("volumeConsoEnM3", 0) for c in self.coordinator.data[:7]), 3
            )
        return None


class ResoConsommation30jSensor(ResoBaseSensor):
    """Capteur de consommation sur 30 jours."""

    _attr_device_class = SensorDeviceClass.WATER
    _attr_state_class = SensorStateClass.MEASUREMENT
    _attr_native_unit_of_measurement = "m³"
    _attr_icon = "mdi:calendar-month"

    def __init__(self, coordinator, entry):
        super().__init__(coordinator, entry)
        self._attr_unique_id = f"reso_{self._contrat}_conso_30j"
        self._attr_name = "RESO Eau Consommation 30 jours"

    @property
    def native_value(self) -> float | None:
        if self.coordinator.data:
            return round(
                sum(c.get("volumeConsoEnM3", 0) for c in self.coordinator.data), 3
            )
        return None
