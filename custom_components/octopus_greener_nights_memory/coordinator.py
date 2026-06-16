import asyncio
import random
import logging
import aiohttp
from datetime import datetime, timedelta, date

from homeassistant.helpers.update_coordinator import DataUpdateCoordinator
from homeassistant.core import HomeAssistant
from homeassistant.helpers.storage import Store
from homeassistant.helpers.aiohttp_client import async_get_clientsession

from .const import STORE_KEY, STORE_VERSION, API_URL, QUERY


class OctopusGreenerCoordinator(DataUpdateCoordinator):
    def __init__(self, hass: HomeAssistant):
        self.hass = hass
        self.store = Store(hass, STORE_VERSION, STORE_KEY)
        self._has_completed_first_refresh = False

        super().__init__(
            hass,
            logger=logging.getLogger(__name__),
            name="octopus_greener_nights_memory",
            update_interval=timedelta(hours=1),
        )

    async def _async_update_data(self):
        if self._has_completed_first_refresh:
            # Stagger scheduled refreshes to avoid synchronized hourly API bursts.
            await asyncio.sleep(random.randint(0, 300))
        else:
            self._has_completed_first_refresh = True

        try:
            session = async_get_clientsession(self.hass)

            async with session.post(
                API_URL,
                json=QUERY,
                headers={"Content-Type": "application/json"},
                timeout=aiohttp.ClientTimeout(total=5),
            ) as resp:
                result = await resp.json()

            forecast = result["data"]["greenerNightsForecast"]

            stored = await self.store.async_load()
            stored = stored or {}
            old_memory = stored.get("memory", {})

            today = date.today()

            # strict rolling 7-day window (today + 6)
            new_memory = {}
            forecast_map = {}
            green_count = 0

            for i in range(7):
                d = (today + timedelta(days=i)).isoformat()
                new_memory[d] = "red"

            # inject API results
            for item in forecast:
                d = item["date"]

                if d not in new_memory:
                    continue

                forecast_map[d] = {
                    "is_greener_night": item["isGreenerNight"],
                    "greenness_score": item["greennessScore"],
                    "greenness_index": item["greennessIndex"],
                }

                if item["isGreenerNight"]:
                    new_memory[d] = "green"
                    green_count += 1

            # convert previously-green → orange if it disappeared
            for d, state in old_memory.items():
                if d in new_memory:
                    if state == "green" and new_memory[d] != "green":
                        new_memory[d] = "orange"

            data = {
                "memory": new_memory,
                "forecast": forecast_map,
                "green_count": green_count,
                "greenness_score": forecast[0]["greennessScore"] if forecast else None,
                "greenness_index": forecast[0]["greennessIndex"] if forecast else None,
                "last_update": datetime.utcnow().isoformat(),
                "api_status": "ok",
            }

            await self.store.async_save(data)
            return data

        except Exception as e:
            # fail safe: do not break entity completely
            stored = await self.store.async_load()
            stored = stored or {}

            return {
                "memory": stored.get("memory", {}),
                "forecast": stored.get("forecast", {}),
                "green_count": stored.get("green_count", 0),
                "greenness_score": stored.get("greenness_score"),
                "greenness_index": stored.get("greenness_index"),
                "api_status": "error",
                "last_update": datetime.utcnow().isoformat(),
            }
