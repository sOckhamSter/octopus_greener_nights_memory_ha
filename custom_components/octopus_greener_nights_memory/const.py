DOMAIN = "octopus_greener_nights_memory"
DEBUG_ACTIONS = False

STORE_KEY = f"{DOMAIN}_store"
STORE_VERSION = 1

API_URL = "https://api.backend.octopus.energy/v1/graphql/"
QUERY = {
    "query": "{ greenerNightsForecast { date greennessScore isGreenerNight greennessIndex } }"
}
