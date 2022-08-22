from homeassistant.const import (
    DEVICE_CLASS_TEMPERATURE,
    DEVICE_CLASS_HUMIDITY,
    DEVICE_CLASS_POWER,
    DEVICE_CLASS_ENERGY,
    TIME_MINUTES,
    TEMP_CELSIUS,
    POWER_WATT,
    PERCENTAGE,
    ENERGY_KILO_WATT_HOUR
)
from homeassistant.components.binary_sensor import BinarySensorDeviceClass
from .midea.devices.ac.device import DeviceAttributes as ACAttributes
from .midea.devices.cc.device import DeviceAttributes as CCAttributes
from .midea.devices.da.device import DeviceAttributes as DAAttributes
from .midea.devices.db.device import DeviceAttributes as DBAttributes
from .midea.devices.dc.device import DeviceAttributes as DCAttributes
from .midea.devices.e2.device import DeviceAttributes as E2Attributes
from .midea.devices.e3.device import DeviceAttributes as E3Attributes

MIDEA_DEVICES = {
    0xAC: {
        "name": "Air Conditioner",
        "entities": {
            "climate": {
                "type": "climate",
                "icon": "mdi:air-conditioner"
            },
            ACAttributes.aux_heat: {
                "type": "switch",
                "name": "Aux Heating",
                "icon": "mdi:heat-wave"
            },
            ACAttributes.boost_mode: {
                "type": "switch",
                "name": "Boost Mode",
                "icon": "mdi:alpha-b-circle"
            },
            ACAttributes.breezeless: {
                "type": "switch",
                "name": "Breezeless",
                "icon": "mdi:tailwind"
            },
            ACAttributes.comfort_mode: {
                "type": "switch",
                "name": "Comfort Mode",
                "icon": "mdi:alpha-c-circle"
            },
            ACAttributes.dry: {
                "type": "switch",
                "name": "Dry",
                "icon": "mdi:air-filter"
            },
            ACAttributes.eco_mode: {
                "type": "switch",
                "name": "ECO Mode",
                "icon": "mdi:alpha-e-circle"
            },
            ACAttributes.indirect_wind: {
                "type": "switch",
                "name": "Indirect Wind",
                "icon": "mdi:tailwind"
            },
            ACAttributes.natural_wind: {
                "type": "switch",
                "name": "Natural Wind",
                "icon": "mdi:tailwind"
            },
            ACAttributes.night_light: {
                "type": "switch",
                "name": "Night Light",
                "icon": "mdi:lightbulb"
            },
            ACAttributes.prompt_tone: {
                "type": "switch",
                "name": "Prompt Tone",
                "icon": "mdi:bell"
            },
            ACAttributes.power: {
                "type": "switch",
                "name": "Power",
                "icon": "mdi:power"
            },
            ACAttributes.screen_display: {
                "type": "switch",
                "name": "Screen Display",
                "icon": "mdi:television-ambient-light"
            },
            # ACAttributes.sleep_mode: {
            #     "type": "switch",
            #     "name": "Sleep Mode",
            #     "icon": "mdi:power-sleep"
            # },
            ACAttributes.smart_eye: {
                "type": "switch",
                "name": "Smart Eye",
                "icon": "mdi:eye"
            },
            ACAttributes.swing_horizontal: {
                "type": "switch",
                "name": "Swing Horizontal",
                "icon": "mdi:arrow-split-vertical"
            },
            ACAttributes.swing_vertical: {
                "type": "switch",
                "name": "Swing Vertical",
                "icon": "mdi:arrow-split-horizontal"
            },
            ACAttributes.indoor_humidity: {
                "type": "sensor",
                "name": "Indoor Humidity",
                "state_class": "measurement",
                "device_class": DEVICE_CLASS_HUMIDITY,
                "unit": PERCENTAGE
            },
            ACAttributes.indoor_temperature: {
                "type": "sensor",
                "name": "Indoor Temperature",
                "state_class": "measurement",
                "device_class": DEVICE_CLASS_TEMPERATURE,
                "unit": TEMP_CELSIUS
            },
            ACAttributes.outdoor_temperature: {
                "type": "sensor",
                "name": "Outdoor Temperature",
                "state_class": "measurement",
                "device_class": DEVICE_CLASS_TEMPERATURE,
                "unit": TEMP_CELSIUS
            },
            ACAttributes.total_energy_consumption: {
                "type": "sensor",
                "name": "Total Energy Consumption",
                "state_class": "total_increasing",
                "device_class": DEVICE_CLASS_ENERGY,
                "unit": ENERGY_KILO_WATT_HOUR
            },
            ACAttributes.current_energy_consumption: {
                "type": "sensor",
                "name": "Current Energy Consumption",
                "state_class": "measurement",
                "device_class": DEVICE_CLASS_ENERGY,
                "unit": ENERGY_KILO_WATT_HOUR
            },
            ACAttributes.realtime_power: {
                "type": "sensor",
                "name": "Realtime Power",
                "state_class": "measurement",
                "device_class": DEVICE_CLASS_POWER,
                "unit": POWER_WATT
            }
        }
    },
    0xCC: {
        "name": "AC Control Panel",
        "entities": {
            "climate": {
                "type": "climate",
                "icon": "hass:air-conditioner"
            },
            CCAttributes.aux_heat: {
                "type": "switch",
                "name": "Aux Heating",
                "icon": "mdi:heat-wave"
            },
            CCAttributes.eco_mode: {
                "type": "switch",
                "name": "ECO Mode",
                "icon": "mdi:alpha-e-circle"
            },
            CCAttributes.night_light: {
                "type": "switch",
                "name": "Night Light",
                "icon": "mdi:lightbulb"
            },
            CCAttributes.power: {
                "type": "switch",
                "name": "Power",
                "icon": "mdi:power"
            },
            CCAttributes.sleep_mode: {
                "type": "switch",
                "name": "Sleep Mode",
                "icon": "mdi:power-sleep"
            },
            CCAttributes.swing: {
                "type": "switch",
                "name": "Swing",
                "icon": "mdi:arrow-split-horizontal"
            },
            CCAttributes.indoor_temperature: {
                "type": "sensor",
                "name": "Indoor Temperature",
                "state_class": "measurement",
                "device_class": DEVICE_CLASS_TEMPERATURE,
                "unit": TEMP_CELSIUS
            },
        }
    },
    0xDA: {
        "name": "Top Load Washer",
        "entities": {
            DAAttributes.time_remaining: {
                "type": "sensor",
                "name": "Time Remaining",
                "icon": "mdi:progress-clock",
                "unit": TIME_MINUTES
            },
            DAAttributes.progress: {
                "type": "sensor",
                "name": "Progress",
                "icon": "mdi:rotate-360"
            },
            DAAttributes.power: {
                "type": "switch",
                "name": "Power",
                "icon": "mdi:power"
            },
            DAAttributes.start: {
                "type": "switch",
                "name": "Start",
                "icon": "mdi:motion-play-outline"
            },
        }
    },
    0xDB: {
        "name": "Front Load Washer",
        "entities": {
            DBAttributes.time_remaining: {
                "type": "sensor",
                "name": "Time Remaining",
                "icon": "mdi:progress-clock",
                "unit": TIME_MINUTES
            },
            DBAttributes.progress: {
                "type": "sensor",
                "name": "Progress",
                "icon": "mdi:rotate-360"
            },
            DBAttributes.power: {
                "type": "switch",
                "name": "Power",
                "icon": "mdi:power"
            },
            DBAttributes.start: {
                "type": "switch",
                "name": "Start",
                "icon": "mdi:motion-play-outline"
            },
        }
    },
    0xDC: {
        "name": "Clothes Dryer",
        "entities": {
            DCAttributes.time_remaining: {
                "type": "sensor",
                "name": "Time Remaining",
                "icon": "mdi:progress-clock",
                "unit": TIME_MINUTES
            },
            DCAttributes.progress: {
                "type": "sensor",
                "name": "Progress",
                "icon": "mdi:rotate-360"
            },
            DCAttributes.power: {
                "type": "switch",
                "name": "Power",
                "icon": "mdi:power"
            },
            DCAttributes.start: {
                "type": "switch",
                "name": "Start",
                "icon": "mdi:motion-play-outline"
            },
        }
    },
    0xE2: {
        "name": "Electric Water Heater",
        "entities": {
            "water_heater": {
                "type": "water_heater",
                "icon": "mdi:meter-electric-outline"
            },
            E2Attributes.heating: {
                "type": "binary_sensor",
                "name": "Heating",
                "icon": "mdi:heat-wave",
                "device_class": BinarySensorDeviceClass.RUNNING
            },
            E2Attributes.heat_insulating: {
                "type": "binary_sensor",
                "name": "Heat Insulating",
                "icon": "mdi:menu",
                "device_class": BinarySensorDeviceClass.RUNNING
            },
            E2Attributes.protection: {
                "type": "binary_sensor",
                "name": "Protection",
                "icon": "mdi:shield-check",
                "device_class": BinarySensorDeviceClass.RUNNING
            },
            E2Attributes.heating_power: {
                "type": "sensor",
                "name": "Heating Power",
                "state_class": "measurement",
                "device_class": DEVICE_CLASS_POWER,
                "unit": POWER_WATT
            },
            E2Attributes.temperature: {
                "type": "sensor",
                "name": "Temperature",
                "state_class": "measurement",
                "device_class": DEVICE_CLASS_TEMPERATURE,
                "unit": TEMP_CELSIUS
            },
            E2Attributes.auto_cut_out: {
                "type": "switch",
                "name": "Auto cut out",
                "icon": "mdi:power-plug-off"
            },
            E2Attributes.power: {
                "type": "switch",
                "name": "Power",
                "icon": "mdi:power"
            },
            E2Attributes.variable_heating: {
                "type": "switch",
                "name": "Variable Heating",
                "icon": "mdi:waves"
            },
            E2Attributes.whole_tank_heating: {
                "type": "switch",
                "name": "Whole Tank Heating",
                "icon": "mdi:restore"
            }
        }
    },
    0xE3: {
        "name": "Gas Water Heater",
        "entities": {
            "water_heater": {
                "type": "water_heater",
                "icon": "mdi:meter-gas"
            },
            E3Attributes.burning_state: {
                "type": "binary_sensor",
                "name": "Burning State",
                "icon": "mdi:fire",
                "device_class": BinarySensorDeviceClass.RUNNING
            },
            E3Attributes.protection: {
                "type": "binary_sensor",
                "name": "Protection",
                "icon": "mdi:shield-check",
                "device_class": BinarySensorDeviceClass.RUNNING
            },
            E3Attributes.temperature: {
                "type": "sensor",
                "name": "Temperature",
                "state_class": "measurement",
                "device_class": DEVICE_CLASS_TEMPERATURE,
                "unit": TEMP_CELSIUS
            },
            E3Attributes.power: {
                "type": "switch",
                "name": "Power",
                "icon": "mdi:power"
            },
            E3Attributes.smart_volume: {
                "type": "switch",
                "name": "Smart Volume",
                "icon": "mdi:recycle"
            },
            E3Attributes.zero_cold_water: {
                "type": "switch",
                "name": "Zero Cold Water",
                "icon": "mdi:restore"
            },
            E3Attributes.zero_cold_pulse: {
                "type": "switch",
                "name": "Zero Cold Water (Pulse)",
                "icon": "mdi:restore-alert"
            },
        }
    }
}
