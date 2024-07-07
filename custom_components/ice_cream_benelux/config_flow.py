"""Config flow for ice_cream_benelux."""

import voluptuous as vol

from homeassistant import config_entries
from homeassistant.const import CONF_LATITUDE
import homeassistant.helpers.config_validation as cv
from homeassistant.helpers.selector import (
    SelectSelector,
    SelectSelectorConfig,
    SelectSelectorMode,
)

from .const import APP_NAME, COMPANIES, CONF_COMPANIES, CONF_LONGITUDE, DOMAIN

company_list = [{"label": value, "value": key} for key, value in COMPANIES.items()]

data_schema = vol.Schema(
    {
        vol.Required(CONF_LATITUDE): cv.positive_float,
        vol.Required(CONF_LONGITUDE): cv.positive_float,
        vol.Required(CONF_COMPANIES, default=[]): SelectSelector(
            SelectSelectorConfig(
                options=list(company_list),
                mode=SelectSelectorMode.DROPDOWN,
                multiple=True,
                custom_value=True,
                translation_key="companies",
            )
        ),
    }
)


def validate_user_input(user_input, errors):
    """Validate user input."""
    if len(user_input[CONF_COMPANIES]) == 0:
        errors["base"] = "no_companies"


class ConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Config flow."""

    VERSION = 1

    async def async_step_user(self, user_input=None):
        """Handle a flow initialized by the user."""
        if user_input is None:
            return self._show_form(user_input)

        errors = {}
        validated_input = self._validate_user_input(user_input, errors)

        if errors:
            return self._show_form(user_input, errors)

        unique_id = self._generate_unique_id(validated_input)
        self._abort_if_unique_id_configured(unique_id)

        return self.async_create_entry(title=APP_NAME, data=validated_input)

    def _show_form(self, user_input=None, errors=None):
        """Show the form to the user."""
        return self.async_show_form(
            step_id="user", data_schema=data_schema, errors=errors or {}
        )

    def _validate_user_input(self, user_input, errors):
        """Validate user input."""
        if not user_input[CONF_COMPANIES]:
            errors["base"] = "no_companies"
        return user_input

    def _generate_unique_id(self, validated_input):
        """Generate a unique ID based on validated input."""
        selected_companies = "-".join(validated_input[CONF_COMPANIES])
        return f"{validated_input[CONF_LATITUDE]}_{validated_input[CONF_LONGITUDE]}_{selected_companies}"
