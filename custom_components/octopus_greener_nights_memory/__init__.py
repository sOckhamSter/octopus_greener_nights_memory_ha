import random
from datetime import date, timedelta

from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant

from .coordinator import OctopusGreenerCoordinator
from .const import DEBUG_ACTIONS, DOMAIN
from .frontend import async_setup_frontend

PLATFORMS = ["sensor"]


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    coordinator = OctopusGreenerCoordinator(hass)

    hass.data.setdefault(DOMAIN, {})
    hass.data[DOMAIN][entry.entry_id] = coordinator

    # register frontend card + JS
    await async_setup_frontend(hass)

    # required for DataUpdateCoordinator
    await coordinator.async_config_entry_first_refresh()

    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)
    return True


async def async_setup(hass, config):
    async def set_memory(coordinator, memory):
        green_count = sum(1 for colour in memory.values() if colour == "green")

        data = {
            **(coordinator.data or {}),
            "memory": memory,
            "green_count": green_count,
        }

        await coordinator.store.async_save(data)
        coordinator.async_set_updated_data(data)

    async def handle_refresh(call):
        for coordinator in hass.data.get(DOMAIN, {}).values():
            await coordinator.async_request_refresh()

    async def handle_randomize_memory(call):
        for coordinator in hass.data.get(DOMAIN, {}).values():
            today = date.today()
            colours = ("red", "green", "orange")
            memory = {
                (today + timedelta(days=i)).isoformat(): random.choice(colours)
                for i in range(7)
            }
            await set_memory(coordinator, memory)

    async def handle_reset_memory(call):
        for coordinator in hass.data.get(DOMAIN, {}).values():
            today = date.today()
            memory = {
                (today + timedelta(days=i)).isoformat(): "red"
                for i in range(7)
            }
            await set_memory(coordinator, memory)

    hass.services.async_register(
        DOMAIN,
        "refresh",
        handle_refresh,
    )
    if DEBUG_ACTIONS:
        hass.services.async_register(
            DOMAIN,
            "randomize_memory",
            handle_randomize_memory,
        )
        hass.services.async_register(
            DOMAIN,
            "reset_memory",
            handle_reset_memory,
        )

    return True


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    return await hass.config_entries.async_unload_platforms(entry, PLATFORMS)
