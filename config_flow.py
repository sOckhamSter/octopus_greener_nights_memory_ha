import voluptuous as vol

from homeassistant import config_entries

from .const import DOMAIN


class ConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    VERSION = 1

    async def async_step_user(self, user_input=None):
        return self.async_create_entry(
            title="Octopus Greener Nights Memory",
            data={}
        )
