import voluptuous as vol
from homeassistant import config_entries
from homeassistant.config_entries import ConfigFlowResult

from .const import DOMAIN


class FaceRecognizerConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Handle a config flow for Face Recognizer."""

    async def async_step_user(self, user_input: dict | None = None) -> ConfigFlowResult:
        """Handle the initial step of the config flow."""
        if user_input is not None:
            return self.async_create_entry(title="Face Recognizer", data={})

        return self.async_show_form(step_id="user", data_schema=vol.Schema({}))
