"""Config flow pour RESO Seine & Orge."""
from __future__ import annotations

from typing import Any

import voluptuous as vol

from homeassistant import config_entries
from homeassistant.core import HomeAssistant
from homeassistant.data_entry_flow import FlowResult
from homeassistant.exceptions import HomeAssistantError

from .api import ResoClient, ResoAuthError, ResoApiError
from .const import DOMAIN, CONF_EMAIL, CONF_PASSWORD, CONF_CONTRAT

STEP_USER_DATA_SCHEMA = vol.Schema(
    {
        vol.Required(CONF_EMAIL): str,
        vol.Required(CONF_PASSWORD): str,
        vol.Optional(CONF_CONTRAT, default=""): str,
    }
)


async def validate_input(hass: HomeAssistant, data: dict[str, Any]) -> dict[str, Any]:
    """Valide les identifiants et retourne le numéro de contrat."""
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
    """Gestion du config flow pour RESO Seine & Orge."""

    VERSION = 1

    async def async_step_user(
        self, user_input: dict[str, Any] | None = None
    ) -> FlowResult:
        """Étape initiale : saisie des identifiants."""
        errors: dict[str, str] = {}

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
                # Stocker le numéro de contrat récupéré
                user_input[CONF_CONTRAT] = info["contrat"]
                return self.async_create_entry(
                    title=info["title"],
                    data=user_input,
                )

        return self.async_show_form(
            step_id="user",
            data_schema=STEP_USER_DATA_SCHEMA,
            errors=errors,
        )


class CannotConnect(HomeAssistantError):
    """Impossible de se connecter à l'API."""


class InvalidAuth(HomeAssistantError):
    """Identifiants invalides."""
