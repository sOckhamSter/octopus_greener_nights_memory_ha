import logging
from pathlib import Path

from homeassistant.components import frontend
from homeassistant.components.http import StaticPathConfig
from homeassistant.components.lovelace.const import (
    CONF_RESOURCE_TYPE_WS,
    LOVELACE_DATA,
    MODE_STORAGE,
)
from homeassistant.const import CONF_ID, CONF_TYPE, CONF_URL
from homeassistant.core import HomeAssistant, callback
from homeassistant.helpers.event import async_call_later

from ..const import DOMAIN

_LOGGER = logging.getLogger(__name__)

DATA_STATIC_REGISTERED = f"{DOMAIN}_static_registered"
DATA_RESOURCE_REGISTERED = f"{DOMAIN}_resource_registered"
DATA_EXTRA_JS_REGISTERED = f"{DOMAIN}_extra_js_registered"
CARD_URL = "/octo_gnm_card.js?v=1.0.19"
CARD_URL_BASE = "/octo_gnm_card.js"


async def _async_register_lovelace_resource(hass: HomeAssistant) -> bool:
    lovelace_data = hass.data.get(LOVELACE_DATA)
    if lovelace_data is None:
        _LOGGER.debug("Lovelace data is not ready yet")
        return False

    if lovelace_data.resource_mode != MODE_STORAGE:
        _LOGGER.warning(
            "Lovelace resources are in YAML mode; add %s manually as a module",
            CARD_URL,
        )
        return False

    resources = lovelace_data.resources
    if not hasattr(resources, "async_create_item"):
        _LOGGER.debug("Lovelace resource storage is not writable")
        return False

    await resources.async_get_info()

    for item in resources.async_items():
        url = item.get(CONF_URL, "")
        if url.split("?", 1)[0] != CARD_URL_BASE:
            continue

        if item.get(CONF_TYPE) != "module" or url != CARD_URL:
            await resources.async_update_item(
                item[CONF_ID],
                {
                    CONF_RESOURCE_TYPE_WS: "module",
                    CONF_URL: CARD_URL,
                },
            )

        return True

    await resources.async_create_item(
        {
            CONF_RESOURCE_TYPE_WS: "module",
            CONF_URL: CARD_URL,
        }
    )
    return True


async def _async_register_resource_or_fallback(hass: HomeAssistant) -> None:
    if hass.data.get(DATA_RESOURCE_REGISTERED):
        return

    if await _async_register_lovelace_resource(hass):
        hass.data[DATA_RESOURCE_REGISTERED] = True
        _LOGGER.debug("Registered Lovelace resource for %s", CARD_URL)
        return

    if not hass.data.get(DATA_EXTRA_JS_REGISTERED):
        frontend.add_extra_js_url(hass, CARD_URL)
        hass.data[DATA_EXTRA_JS_REGISTERED] = True


async def async_setup_frontend(hass: HomeAssistant):
    if not hass.data.get(DATA_STATIC_REGISTERED):
        file_path = Path(__file__).parent / "greener-nights-card.js"

        await hass.http.async_register_static_paths(
            [
                StaticPathConfig(
                    CARD_URL_BASE,
                    str(file_path),
                    cache_headers=False,
                )
            ]
        )

        hass.data[DATA_STATIC_REGISTERED] = True

    await _async_register_resource_or_fallback(hass)

    @callback
    def _retry_lovelace_resource(_now):
        hass.async_create_task(_async_register_resource_or_fallback(hass))

    async_call_later(hass, 30, _retry_lovelace_resource)
