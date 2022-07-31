from homeassistant.const import (
    DEVICE_CLASS_TEMPERATURE,
    DEVICE_CLASS_HUMIDITY,
    TEMP_CELSIUS,
    PERCENTAGE
)

MIDEA_DEVICES = {
    0xac: {
        "name": "Air Conditioner",
        "entities": {
            "climate": {
                "type": "climate",
                "icon": "mdi:air-conditioner"
            },
            "aux_heat": {
                "type": "switch",
                "name": "Aux Heating",
                "icon": "mdi:heat-wave"
            },
            "breezyless":{
                "type": "switch",
                "name": "Breezyless",
                "icon": "mdi:tailwind"
            },
            "comfort_mode": {
                "type": "switch",
                "name": "Comfort Mode",
                "icon": "mdi:alpha-c-circle"
            },
            "dry": {
                "type": "switch",
                "name": "Dry",
                "icon": "mdi:air-filter"
            },
            "eco_mode": {
                "type": "switch",
                "name": "ECO Mode",
                "icon": "mdi:alpha-e-circle"
            },
            "indirect_wind": {
                "type": "switch",
                "name": "Indirect Wind",
                "icon": "mdi:tailwind"
            },
            "natural_wind": {
                "type": "switch",
                "name": "Natural Wind",
                "icon": "mdi:tailwind"
            },
            "night_light": {
                "type": "switch",
                "name": "Night Light",
                "icon": "mdi:lightbulb"
            },
            "prompt_tone": {
                "type": "switch",
                "name": "Prompt Tone",
                "icon": "mdi:bell"
            },
            "screen_display": {
                "type": "switch",
                "name": "Screen Display",
                "icon": "mdi:television-ambient-light"
            },
            # "sleep_mode": {
            #    "type": "switch",
            #    "name": "Sleep Mode",
            #    "icon": "mdi:power-sleep"
            # },
            "smart_eye": {
                "type": "switch",
                "name": "Smart eye",
                "icon": "mdi:eye"
            },
            "swing_horizontal": {
                "type": "switch",
                "name": "Swing Horizontal",
                "icon": "mdi:arrow-split-vertical"
            },
            "swing_vertical": {
                "type": "switch",
                "name": "Swing Vertical",
                "icon": "mdi:arrow-split-horizontal"
            },
            "turbo_mode": {
                "type": "switch",
                "name": "Turbo Mode",
                "icon": "mdi:alpha-t-circle"
            },
            "indoor_humidity": {
                "type": "sensor",
                "name": "Indoor Humidity",
                "device_class": DEVICE_CLASS_HUMIDITY,
                "unit": PERCENTAGE
            },
            "indoor_temperature": {
                "type": "sensor",
                "name": "Indoor Temperature",
                "device_class": DEVICE_CLASS_TEMPERATURE,
                "unit": TEMP_CELSIUS
            },
            "outdoor_temperature": {
                "type": "sensor",
                "name": "Outdoor Temperature",
                "device_class": DEVICE_CLASS_TEMPERATURE,
                "unit": TEMP_CELSIUS
            }
        }
    },
    0xcc: {
        "name": "AC Control Panel",
        "entities": {
            "climate": {
                "type": "climate",
                "icon": "hass:air-conditioner"
            },
            "aux_heat": {
                "type": "switch",
                "name": "Aux Heating",
                "icon": "mdi:heat-wave"
            },
            "eco_mode": {
                "type": "switch",
                "name": "ECO Mode",
                "icon": "mdi:alpha-e-circle"
            },
            "night_light": {
                "type": "switch",
                "name": "Night Light",
                "icon": "mdi:lightbulb"
            },
            "sleep_mode": {
               "type": "switch",
               "name": "Sleep Mode",
               "icon": "mdi:power-sleep"
            },
            # "ventilation": {
            #    "type": "switch",
            #    "name": "Ventilation",
            #    "icon": "mdi:tailwind"
            # },
            "swing": {
                "type": "switch",
                "name": "Swing",
                "icon": "mdi:arrow-split-horizontal"
            },
            "indoor_temperature": {
                "type": "sensor",
                "name": "Indoor Temperature",
                "device_class": DEVICE_CLASS_TEMPERATURE,
                "unit": TEMP_CELSIUS
            },
        }
    }
}
