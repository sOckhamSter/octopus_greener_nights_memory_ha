from homeassistant.helpers.entity import Entity

from .const import DOMAIN


async def async_setup_entry(hass, entry, async_add_entities):
    coordinator = hass.data[DOMAIN][entry.entry_id]
    async_add_entities([OctopusGreenerSensor(coordinator)])


class OctopusGreenerSensor(Entity):
    def __init__(self, coordinator):
        self.coordinator = coordinator

    @property
    def name(self):
        return "Octopus Greener Nights Memory"

    @property
    def unique_id(self):
        return "octopus_greener_nights_memory"

    @property
    def state(self):
        return self.coordinator.data.get("green_count", 0)

    @property
    def extra_state_attributes(self):
        return {
            "memory": self.coordinator.data.get("memory", {}),
            "forecast": self.coordinator.data.get("forecast", {}),
            "greenness_score": self.coordinator.data.get("greenness_score"),
            "greenness_index": self.coordinator.data.get("greenness_index"),
            "last_update": self.coordinator.data.get("last_update"),
            "api_status": self.coordinator.data.get("api_status"),
        }

    @property
    def available(self):
        return self.coordinator.data is not None
