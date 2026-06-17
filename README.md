# Octopus Greener Nights Memory

A combined integration and dashboard card for Home Assistant to track and display upcoming "Greener Nights" from Octopus Energy on your Home Assistant dashboard. Because the weather changes and forecasted greener nights can disappear from the upcoming schedule, this integration will also keep track of disappearing greener nights and highlight them too. 

[![Open your Home Assistant instance and open a repository inside the Home Assistant Community Store.](https://my.home-assistant.io/badges/hacs_repository.svg)](https://my.home-assistant.io/redirect/hacs_repository/?owner=+sOckhamSter&repository=octopus_greener_nights_memory&category=Integration)

![A screenshot showing the dashboard card rendered in Home Assistant in two different sizes](https://raw.githubusercontent.com/sOckhamSter/octopus_greener_nights_memory_ha/refs/heads/main/screenshots/screenshot-dashboardcards.png)

## What are Octopus Energy Greener Nights?
"Greener Nights" is an incentive service from Octopus Energy designed to reward you financially for charging your EV (electric vehicle) on nights when the electricity grid is cleanest. It is a bolt-on feature to their "Intelligent Octopus Go" EV-specific electricity tariff. If you manage to achieve a certain percentage of your EV charging in any given month on greener nights then you are rewarded with "Octopoints" which can be converted into account credit.

Sometimes the forecast changes and upcoming greener nights disappear. Those now-missing greener nights will still count towards your monthly greener nights charging target if you plug in that day, but remembering that a day was previously green is tricky. This integration and card is designed to help you remember which nights count. It's still best to plug in on a 'green' night, but if you really need to then an 'orange' night will work too.

Find out more about Octopus Greener Nights here: https://octopus.energy/smart/greener-nights

## Features

- Fetches the Octopus Greener Nights forecast directly from the Octopus Energy API
- Updates the forecast hourly (with a random delay)
- Stores all Greener Nights forecast data from the API including the greenness score and index in a sensor
- Remembers which days were previously 'green' and marks them as 'orange'
- A customisable dashboard card with GUI configuration
- A manual refresh service



## Installation with HACS
Make sure that you have HACS installed in Home Assistant before you begin - see https://hacs.xyz for more information.

1. In HACS, open the menu and choose **Custom repositories**.
2. Add this repository URL:

```text
https://github.com/sOckhamSter/octopus_greener_nights_memory_ha
```

3. Select **Integration** as the "Type".
4. Search for and download **Octopus Greener Nights Memory** from the list of available items in HACS.
5. Restart Home Assistant.
6. Add the integration from **Settings > Devices & services**.
7. Refresh your browser cache
	- *Safari*: option + command + R
	- *Chrome (macOS)*: shift + command + R
	- *Chrome (Windows)*: ctrl + shift + R
	- *Companion App*: (in app) Settings > Companion app > Debugging > Reset frontend cache
8. Edit your dashboard and add the card named **Octopus Greener Nights Memory Card**

***Note***: After installation, all tiles on the card will show as either red or green initially. Previously green nights will only be tracked as orange once the integration has seen them disappeared. The integration has no knowledge of former greener nights before the time at which it was installed so please be patient for a few days while it learns.

## Sensors

This integration provides you with a single sensor:
```text
sensor.octopus_greener_nights_memory
```

Data retrieved from the Octopus Energy API is stored within the state attributes of the sensor in the following format:

>     memory:
>       "yyyy-mm-dd": red | orange | green
>       "yyyy-mm-dd+1": red | orange | green
>       "yyyy-mm-dd+2": red | orange | green
>       "yyyy-mm-dd+3": red | orange | green
>       "yyyy-mm-dd+4": red | orange | green
>       "yyyy-mm-dd+5": red | orange | green
>       "yyyy-mm-dd+6": red | orange | green
>     forecast:
>       "yyyy-mm-dd":
>         is_greener_night: true | false
>         greenness_score: <int>
>         greenness_index: LOW | MEDIUM | HIGH
>       "yyyy-mm-dd+1":
>         is_greener_night: true | false
>         greenness_score: <int>
>         greenness_index: LOW | MEDIUM | HIGH
>       "yyyy-mm-dd+2":
>         is_greener_night: true | false
>         greenness_score: <int>
>         greenness_index: LOW | MEDIUM | HIGH
>       "yyyy-mm-dd+3":
>         is_greener_night: true | false
>         greenness_score: <int>
>         greenness_index: LOW | MEDIUM | HIGH
>       "yyyy-mm-dd+4":
>         is_greener_night: true | false
>         greenness_score: <int>
>         greenness_index: LOW | MEDIUM | HIGH
>       "yyyy-mm-dd+5":
>         is_greener_night: true | false
>         greenness_score: <int>
>         greenness_index: LOW | MEDIUM | HIGH
>       "yyyy-mm-dd+6":
>         is_greener_night: true | false
>         greenness_score: <int>
>         greenness_index: LOW | MEDIUM | HIGH


## Dashboard (Lovelace) Card

The bundled card is registered automatically and reads data from the provided sensor.
It is fully customisable via the GUI, however if you wish to configure it manually via YAML then create a new custom card with the following YAML configuration:

```text
type: custom:octopus-greener-nights-memory-card
entity: sensor.octopus_greener_nights_memory
title: Octopus Greener Nights
title_mode: large
tile_height: 56
today_font_size: 14
date_font_size: 14
color_green: "#5d9e52"
color_orange: "#f2aa3c"
color_red: "#ca5040"
text_color_green: "#ffffff"
text_color_orange: "#ffffff"
text_color_red: "#ffffff"
```

### Card options

| Name | Type | Default | Description |
|--|--|--|--|
| type | string | required | `custom:octopus-greener-nights-memory-card` |
| entity | object | required | `sensor.octopus_greener_nights_memory` unless you've changed it |
| title | string |   | A text string title for your card |
| title_mode | string | large | `large | compact | none` |
| tile_height | number | 56 | The height in pixels of the rows of tiles on the card |
| today_font_size | number | 14 | The size of the font on the 'today' tile |
| date_font_size | number | 14 | The size of the font on the upcoming days tiles |
| color_green | string | "#5d9e52" | The hex colour of the tile background for a 'green' night |
| color_orange | string | "#f2aa3c" | The hex colour of the tile background for a night than was but is now no longer 'green' |
| color_red | string | "#ca5040" | The hex colour of the tile background for a night that has never been 'green' |
| text_color_green | string | "#ffffff" | The hex colour of the text on a tile with a 'green' background |
| text_color_orange | string | "#ffffff" | The hex colour of the text on a tile with an 'orange' background |
| text_color_red | string | "#ffffff" | The hex colour of the text on a tile with a 'red' background |

## Manual Update

The integration provides an action which performs a manual refresh of the data from the Octopus API. This should not be used as part of an automation in order to ensure the integration imposes minimal impact on Octopus Energy's cloud services. It is provided for troubleshooting purposes only and under normal operation the integration will automatically poll the API for updates.
```text
octopus_greener_nights_memory.refresh
```

