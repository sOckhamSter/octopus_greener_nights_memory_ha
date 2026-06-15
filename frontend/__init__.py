import logging
from pathlib import Path

from homeassistant.components import frontend
from homeassistant.components.http import StaticPathConfig
from homeassistant.components.lovelace.const import (
    CONF_RESOURCE_TYPE_WS,
    LOVELACE_DATA,
)
from homeassistant.const import CONF_ID, CONF_TYPE, CONF_URL
from homeassistant.core import HomeAssistant

from ..const import DOMAIN

_LOGGER = logging.getLogger(__name__)

DATA_FRONTEND_REGISTERED = f"{DOMAIN}_frontend_registered"
CARD_URL = "/octo_gnm_card.js?v=1.0.9"
CARD_URL_BASE = "/octo_gnm_card.js"


async def _async_register_lovelace_resource(hass: HomeAssistant) -> bool:
    lovelace_data = hass.data.get(LOVELACE_DATA)
    if lovelace_data is None:
        return False

    resources = lovelace_data.resources
    if not hasattr(resources, "async_create_item"):
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


async def async_setup_frontend(hass: HomeAssistant):
    if hass.data.get(DATA_FRONTEND_REGISTERED):
        return

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

    if not await _async_register_lovelace_resource(hass):
        _LOGGER.warning(
            "Could not register Lovelace resource; falling back to frontend module"
        )
        frontend.add_extra_js_url(hass, CARD_URL)

    hass.data[DATA_FRONTEND_REGISTERED] = True
