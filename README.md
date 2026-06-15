# Octopus Greener Nights Memory

Home Assistant custom integration and Lovelace card for the Octopus Energy Greener Nights forecast.

The integration fetches the Octopus Greener Nights GraphQL forecast, keeps a strict rolling 7-day window, stores only the current window with Home Assistant storage, and exposes one sensor:

```text
sensor.octopus_greener_nights_memory
```

## Features

- Fetches the Octopus Greener Nights forecast hourly.
- Updates immediately on Home Assistant startup.
- Keeps today plus the next 6 days only.
- Stores no historical data outside the active 7-day window.
- Exposes forecast and memory data as sensor attributes.
- Registers the bundled Lovelace card automatically.
- Provides a manual refresh service:

```text
octopus_greener_nights_memory.refresh
```

## Installation with HACS

1. In HACS, open the menu and choose **Custom repositories**.
2. Add this repository URL:

```text
https://github.com/sOckhamSter/octopus_greener_nights_memory_ha
```

3. Select **Integration** as the category.
4. Install **Octopus Greener Nights Memory**.
5. Restart Home Assistant.
6. Add the integration from **Settings > Devices & services**.

## Lovelace Card

The bundled card is registered automatically:

```text
octopus-greener-nights-memory-card
```

It reads from:

```text
sensor.octopus_greener_nights_memory
```

## State Model

The sensor state is the current green-night count.

Attributes include:

- `memory`
- `forecast`
- `greenness_score`
- `greenness_index`
- `last_update`
- `api_status`

## Version

Current version: `1.0.10`
