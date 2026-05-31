"""Config flow pour RESO Seine & Orge."""
from __future__ import annotations
from typing import Any
import voluptuous as vol
from homeassistant import config_entries
from homeassistant.core import HomeAssistant, callback
from homeassistant.data_entry_flow import FlowResult
from homeassistant.exceptions import HomeAssistantError
from .api import ResoClient, ResoAuthError, ResoApiError
from .const import (
    DOMAIN, CONF_EMAIL, CONF_PASSWORD, CONF_CONTRAT,
    CONF_EP_ABONNEMENT, CONF_EP_CONSO, CONF_EP_TVA,
    CONF_AS_TERRITORIALE, CONF_AS_SYNDICALE, CONF_AS_INTERDEP,
    CONF_OP_VNF, CONF_OP_EPTB, CONF_OP_PREL_RESSOURCE,
    CONF_OP_AESN_CONSO, CONF_OP_AESN_PERF_EP, CONF_OP_AESN_PERF_AS,
    DEFAULT_EP_ABONNEMENT, DEFAULT_EP_CONSO, DEFAULT_EP_TVA,
    DEFAULT_AS_TERRITORIALE, DEFAULT_AS_SYNDICALE, DEFAULT_AS_INTERDEP,
    DEFAULT_OP_VNF, DEFAULT_OP_EPTB, DEFAULT_OP_PREL_RESSOURCE,
    DEFAULT_OP_AESN_CONSO, DEFAULT_OP_AESN_PERF_EP, DEFAULT_OP_AESN_PERF_AS,
)

STEP_USER_DATA_SCHEMA = vol.Schema({
    vol.Required(CONF_EMAIL): str,
    vol.Required(CONF_PASSWORD): str,
    vol.Optional(CONF_CONTRAT, default=""): str,
})


async def validate_input(hass: HomeAssistant, data: dict[str, Any]) -> dict[str, Any]:
    client = ResoClient(
        email=data[CONF_EMAIL],
        password=data[CONF_PASSWORD],
        contrat=data.get(CONF_CONTRAT, ""),
    )
    try:
        contrat = await hass.async_add_executor_job(client.test_connection)
    except ResoAuthError as e:
        raise InvalidAuth(str(e)) from e
    except ResoApiError as e:
        raise CannotConnect(str(e)) from e
    return {"contrat": contrat, "title": f"RESO Eau ({contrat})"}


class ConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    VERSION = 1

    async def async_step_user(self, user_input=None):
        errors = {}
        if user_input is not None:
            try:
                info = await validate_input(self.hass, user_input)
            except InvalidAuth:
                errors["base"] = "invalid_auth"
            except CannotConnect:
                errors["base"] = "cannot_connect"
            except Exception:
                errors["base"] = "unknown"
            else:
                user_input[CONF_CONTRAT] = info["contrat"]
                return self.async_create_entry(title=info["title"], data=user_input)

        return self.async_show_form(
            step_id="user", data_schema=STEP_USER_DATA_SCHEMA, errors=errors
        )

    @staticmethod
    @callback
    def async_get_options_flow(config_entry):
        return ResoOptionsFlow(config_entry)


class ResoOptionsFlow(config_entries.OptionsFlow):
    """Options flow avec tous les postes tarifaires."""

    def __init__(self, config_entry):
        self._config_entry = config_entry

    def _get(self, key, default):
        return self._config_entry.options.get(key, default)

    async def async_step_init(self, user_input=None):
        """Étape 1 : Eau potable."""
        if user_input is not None:
            self._eau_potable = user_input
            return await self.async_step_assainissement()

        return self.async_show_form(
            step_id="init",
            data_schema=vol.Schema({
                vol.Required(CONF_EP_ABONNEMENT, default=self._get(CONF_EP_ABONNEMENT, DEFAULT_EP_ABONNEMENT)): vol.Coerce(float),
                vol.Required(CONF_EP_CONSO,      default=self._get(CONF_EP_CONSO,      DEFAULT_EP_CONSO)):      vol.Coerce(float),
                vol.Required(CONF_EP_TVA,        default=self._get(CONF_EP_TVA,        DEFAULT_EP_TVA)):        vol.Coerce(float),
            }),
        )

    async def async_step_assainissement(self, user_input=None):
        """Étape 2 : Assainissement."""
        if user_input is not None:
            self._assainissement = user_input
            return await self.async_step_organismes()

        return self.async_show_form(
            step_id="assainissement",
            data_schema=vol.Schema({
                vol.Required(CONF_AS_TERRITORIALE, default=self._get(CONF_AS_TERRITORIALE, DEFAULT_AS_TERRITORIALE)): vol.Coerce(float),
                vol.Required(CONF_AS_SYNDICALE,    default=self._get(CONF_AS_SYNDICALE,    DEFAULT_AS_SYNDICALE)):    vol.Coerce(float),
                vol.Required(CONF_AS_INTERDEP,     default=self._get(CONF_AS_INTERDEP,     DEFAULT_AS_INTERDEP)):     vol.Coerce(float),
            }),
        )

    async def async_step_organismes(self, user_input=None):
        """Étape 3 : Organismes publics."""
        if user_input is not None:
            # Fusionner toutes les étapes et sauvegarder
            all_options = {**self._eau_potable, **self._assainissement, **user_input}
            return self.async_create_entry(title="", data=all_options)

        return self.async_show_form(
            step_id="organismes",
            data_schema=vol.Schema({
                vol.Required(CONF_OP_VNF,            default=self._get(CONF_OP_VNF,            DEFAULT_OP_VNF)):            vol.Coerce(float),
                vol.Required(CONF_OP_EPTB,           default=self._get(CONF_OP_EPTB,           DEFAULT_OP_EPTB)):           vol.Coerce(float),
                vol.Required(CONF_OP_PREL_RESSOURCE, default=self._get(CONF_OP_PREL_RESSOURCE, DEFAULT_OP_PREL_RESSOURCE)): vol.Coerce(float),
                vol.Required(CONF_OP_AESN_CONSO,     default=self._get(CONF_OP_AESN_CONSO,     DEFAULT_OP_AESN_CONSO)):     vol.Coerce(float),
                vol.Required(CONF_OP_AESN_PERF_EP,   default=self._get(CONF_OP_AESN_PERF_EP,   DEFAULT_OP_AESN_PERF_EP)):   vol.Coerce(float),
                vol.Required(CONF_OP_AESN_PERF_AS,   default=self._get(CONF_OP_AESN_PERF_AS,   DEFAULT_OP_AESN_PERF_AS)):   vol.Coerce(float),
            }),
        )


class CannotConnect(HomeAssistantError):
    pass

class InvalidAuth(HomeAssistantError):
    pass
