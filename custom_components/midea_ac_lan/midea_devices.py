from homeassistant.const import (
    DEVICE_CLASS_TEMPERATURE,
    DEVICE_CLASS_HUMIDITY,
    DEVICE_CLASS_POWER,
    DEVICE_CLASS_ENERGY,
    TIME_HOURS,
    TIME_MINUTES,
    TEMP_CELSIUS,
    POWER_WATT,
    PERCENTAGE,
    DEGREE,
    ENERGY_KILO_WATT_HOUR
)
from homeassistant.components.binary_sensor import BinarySensorDeviceClass
from .midea.devices.ac.device import DeviceAttributes as ACAttributes
from .midea.devices.ca.device import DeviceAttributes as CAAttributes
from .midea.devices.cc.device import DeviceAttributes as CCAttributes
from .midea.devices.cf.device import DeviceAttributes as CFAttributes
from .midea.devices.da.device import DeviceAttributes as DAAttributes
from .midea.devices.db.device import DeviceAttributes as DBAttributes
from .midea.devices.dc.device import DeviceAttributes as DCAttributes
from .midea.devices.ea.device import DeviceAttributes as EAAttributes
from .midea.devices.ec.device import DeviceAttributes as ECAttributes
from .midea.devices.e1.device import DeviceAttributes as E1Attributes
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
            ACAttributes.screen_display_2: {
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
            ACAttributes.full_dust: {
                "type": "binary_sensor",
                "name": "Full of Dust",
                "icon": "mdi:alert-circle",
                "device_class": BinarySensorDeviceClass.PROBLEM
            },
            ACAttributes.indoor_humidity: {
                "type": "sensor",
                "name": "Indoor Humidity",
                "device_class": DEVICE_CLASS_HUMIDITY,
                "unit": PERCENTAGE,
                "state_class": "measurement"
            },
            ACAttributes.indoor_temperature: {
                "type": "sensor",
                "name": "Indoor Temperature",
                "device_class": DEVICE_CLASS_TEMPERATURE,
                "unit": TEMP_CELSIUS,
                "state_class": "measurement"
            },
            ACAttributes.outdoor_temperature: {
                "type": "sensor",
                "name": "Outdoor Temperature",
                "device_class": DEVICE_CLASS_TEMPERATURE,
                "unit": TEMP_CELSIUS,
                "state_class": "measurement"
            },
            ACAttributes.total_energy_consumption: {
                "type": "sensor",
                "name": "Total Energy Consumption",
                "device_class": DEVICE_CLASS_ENERGY,
                "unit": ENERGY_KILO_WATT_HOUR,
                "state_class": "total_increasing"
            },
            ACAttributes.current_energy_consumption: {
                "type": "sensor",
                "name": "Current Energy Consumption",
                "device_class": DEVICE_CLASS_ENERGY,
                "unit": ENERGY_KILO_WATT_HOUR,
                "state_class": "measurement"
            },
            ACAttributes.realtime_power: {
                "type": "sensor",
                "name": "Realtime Power",
                "device_class": DEVICE_CLASS_POWER,
                "unit": POWER_WATT,
                "state_class": "measurement"
            }
        }
    },
    0xCA: {
        "name": "Refrigerator",
        "entities": {
            CAAttributes.bar_door: {
                "type": "binary_sensor",
                "name": "Bar Door",
                "icon": "mdi:box-shadow",
                "device_class": BinarySensorDeviceClass.DOOR
            },
            CAAttributes.bar_door_overtime: {
                "type": "binary_sensor",
                "name": "Bar Door Overtime",
                "icon": "mdi:alert-circle",
                "device_class": BinarySensorDeviceClass.PROBLEM
            },
            CAAttributes.flex_zone_door: {
                "type": "binary_sensor",
                "name": "Flex Door",
                "icon": "mdi:box-shadow",
                "device_class": BinarySensorDeviceClass.DOOR
            },
            CAAttributes.flex_zone_door_overtime: {
                "type": "binary_sensor",
                "name": "Flex Zone Door",
                "icon": "mdi:alert-circle",
                "device_class": BinarySensorDeviceClass.PROBLEM
            },
            CAAttributes.freezer_door: {
                "type": "binary_sensor",
                "name": "Freezer Door",
                "icon": "mdi:box-shadow",
                "device_class": BinarySensorDeviceClass.DOOR
            },
            CAAttributes.freezer_door_overtime: {
                "type": "binary_sensor",
                "name": "Freezer Door Overtime",
                "icon": "mdi:alert-circle",
                "device_class": BinarySensorDeviceClass.PROBLEM
            },
            CAAttributes.refrigerator_door: {
                "type": "binary_sensor",
                "name": "Refrigerator Door",
                "icon": "mdi:alert-circle",
                "device_class": BinarySensorDeviceClass.PROBLEM
            },
            CAAttributes.refrigerator_door_overtime: {
                "type": "binary_sensor",
                "name": "Refrigerator Door Overtime",
                "icon": "mdi:alert-circle",
                "device_class": BinarySensorDeviceClass.PROBLEM
            },
            CAAttributes.flex_zone_actual_temp: {
                "type": "sensor",
                "name": "Flex Zone Actual Temperature",
                "device_class": DEVICE_CLASS_TEMPERATURE,
                "unit": TEMP_CELSIUS,
                "state_class": "measurement"
            },
            CAAttributes.flex_zone_setting_temp: {
                "type": "sensor",
                "name": "Flex Zone Setting Temperature",
                "device_class": DEVICE_CLASS_TEMPERATURE,
                "unit": TEMP_CELSIUS,
                "state_class": "measurement"
            },
            CAAttributes.freezer_actual_temp: {
                "type": "sensor",
                "name": "Freezer Actual temperature",
                "device_class": DEVICE_CLASS_TEMPERATURE,
                "unit": TEMP_CELSIUS,
                "state_class": "measurement"
            },
            CAAttributes.freezer_setting_temp: {
                "type": "sensor",
                "name": "Freezer Setting temperature",
                "device_class": DEVICE_CLASS_TEMPERATURE,
                "unit": TEMP_CELSIUS,
                "state_class": "measurement"
            },
            CAAttributes.power_consumption: {
                "type": "sensor",
                "name": "Power Consumption",
                "device_class": DEVICE_CLASS_ENERGY,
                "unit": ENERGY_KILO_WATT_HOUR,
                "state_class": "total_increasing"
            },
            CAAttributes.refrigerator_actual_temp: {
                "type": "sensor",
                "name": "Refrigerator Actual Temperature",
                "device_class": DEVICE_CLASS_TEMPERATURE,
                "unit": TEMP_CELSIUS,
                "state_class": "measurement"
            },
            CAAttributes.refrigerator_setting_temp: {
                "type": "sensor",
                "name": "Refrigerator Setting Temperature",
                "device_class": DEVICE_CLASS_TEMPERATURE,
                "unit": TEMP_CELSIUS,
                "state_class": "measurement"
            },
            CAAttributes.right_flex_zone_actual_temp: {
                "type": "sensor",
                "name": "Right Flex Zone Actual Temperature",
                "device_class": DEVICE_CLASS_TEMPERATURE,
                "unit": TEMP_CELSIUS,
                "state_class": "measurement"
            },
            CAAttributes.right_flex_zone_setting_temp: {
                "type": "sensor",
                "name": "Right Flex Zone Setting Temperature",
                "device_class": DEVICE_CLASS_TEMPERATURE,
                "unit": TEMP_CELSIUS,
                "state_class": "measurement"
            },
        },
    },
    0xCC: {
        "name": "MDV Wi-Fi Controller",
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
                "device_class": DEVICE_CLASS_TEMPERATURE,
                "unit": TEMP_CELSIUS,
                "state_class": "measurement"
            },
        }
    },
    0xCF: {
        "name": "Heat Pump",
        "entities": {
            "climate": {
                "type": "climate",
                "icon": "hass:air-conditioner"
            },
            CFAttributes.aux_heat: {
                "type": "switch",
                "name": "Aux Heating",
                "icon": "mdi:heat-wave"
            },
            CFAttributes.power: {
                "type": "switch",
                "name": "Power",
                "icon": "mdi:power"
            },
            CFAttributes.current_temperature: {
                "type": "sensor",
                "name": "Current Temperature",
                "device_class": DEVICE_CLASS_TEMPERATURE,
                "unit": TEMP_CELSIUS,
                "state_class": "measurement"
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
                "unit": TIME_MINUTES,
                "state_class": "measurement"
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
                "unit": TIME_MINUTES,
                "state_class": "measurement"
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
                "unit": TIME_MINUTES,
                "state_class": "measurement"
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
    0xE1: {
        "name": "Dishwasher",
        "entities": {
            E1Attributes.door: {
                "type": "binary_sensor",
                "name": "Door",
                "icon": "mdi:box-shadow",
                "device_class": BinarySensorDeviceClass.DOOR
            },
            E1Attributes.rinse_aid: {
                "type": "binary_sensor",
                "name": "Rinse Aid Shortage",
                "icon": "mdi:bottle-tonic",
                "device_class": BinarySensorDeviceClass.PROBLEM
            },
            E1Attributes.salt: {
                "type": "binary_sensor",
                "name": "Salt Shortage",
                "icon": "mdi:drag",
                "device_class": BinarySensorDeviceClass.PROBLEM
            },
            E1Attributes.progress: {
                "type": "sensor",
                "name": "Progress",
                "icon": "mdi:rotate-360"
            },
            E1Attributes.status: {
                "type": "sensor",
                "name": "Status",
                "icon": "mdi:information"
            },
            E1Attributes.storage_remaining: {
                "type": "sensor",
                "name": "Storage Remaining",
                "icon": "mdi:progress-clock",
                "unit": TIME_HOURS,
                "state_class": "measurement"
            },
            E1Attributes.time_remaining: {
                "type": "sensor",
                "name": "Time Remaining",
                "icon": "mdi:progress-clock",
                "unit": TIME_MINUTES,
                "state_class": "measurement"
            },
            E1Attributes.child_lock: {
                "type": "lock",
                "name": "Child Lock"
            },
            E1Attributes.power: {
                "type": "switch",
                "name": "Power",
                "icon": "mdi:power"
            },
            E1Attributes.storage: {
                "type": "switch",
                "name": "Storage",
                "icon": "mdi:repeat-variant"
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
            E2Attributes.keep_warm: {
                "type": "binary_sensor",
                "name": "Keep Warm",
                "icon": "mdi:menu",
                "device_class": BinarySensorDeviceClass.RUNNING
            },
            E2Attributes.protection: {
                "type": "binary_sensor",
                "name": "Protection",
                "icon": "mdi:shield-check",
                "device_class": BinarySensorDeviceClass.RUNNING
            },
            E2Attributes.current_temperature: {
                "type": "sensor",
                "name": "Current Temperature",
                "device_class": DEVICE_CLASS_TEMPERATURE,
                "unit": TEMP_CELSIUS,
                "state_class": "measurement"
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
            E3Attributes.current_temperature: {
                "type": "sensor",
                "name": "Current Temperature",
                "device_class": DEVICE_CLASS_TEMPERATURE,
                "unit": TEMP_CELSIUS,
                "state_class": "measurement"
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
    },
    0xEA: {
        "name": "Electric Rice Cooker",
        "entities": {
            EAAttributes.cooking: {
                "type": "binary_sensor",
                "name": "Cooking",
                "icon": "mdi:fire",
                "device_class": BinarySensorDeviceClass.RUNNING
            },
            EAAttributes.keep_warm: {
                "type": "binary_sensor",
                "name": "Keep Warm",
                "icon": "mdi:menu",
                "device_class": BinarySensorDeviceClass.RUNNING
            },
            EAAttributes.bottom_temperature: {
                "type": "sensor",
                "name": "Bottom Temperature",
                "device_class": DEVICE_CLASS_TEMPERATURE,
                "unit": TEMP_CELSIUS,
                "state_class": "measurement"
            },
            EAAttributes.keep_warm_time: {
                "type": "sensor",
                "name": "Keep Warm Time",
                "icon": "mdi:progress-clock",
                "unit": TIME_MINUTES,
                "state_class": "measurement"
            },
            EAAttributes.mode: {
                "type": "sensor",
                "name": "Mode",
                "icon": "mdi:orbit"
            },
            EAAttributes.progress: {
                "type": "sensor",
                "name": "Progress",
                "icon": "mdi:rotate-360"
            },
            EAAttributes.time_remaining: {
                "type": "sensor",
                "name": "Time Remaining",
                "icon": "mdi:progress-clock",
                "unit": TIME_MINUTES,
                "state_class": "measurement"
            },
            EAAttributes.top_temperature: {
                "type": "sensor",
                "name": "Top Temperature",
                "device_class": DEVICE_CLASS_TEMPERATURE,
                "unit": TEMP_CELSIUS,
                "state_class": "measurement"
            },
        }
    },
    0xEC: {
        "name": "Electric Pressure Cooker",
        "entities": {
            ECAttributes.cooking: {
                "type": "binary_sensor",
                "name": "Cooking",
                "icon": "mdi:fire",
                "device_class": BinarySensorDeviceClass.RUNNING
            },
            ECAttributes.with_pressure: {
                "type": "binary_sensor",
                "name": "With Pressure",
                "icon": "mdi:information",
                "device_class": BinarySensorDeviceClass.RUNNING
            },
            ECAttributes.bottom_temperature: {
                "type": "sensor",
                "name": "Bottom Temperature",
                "device_class": DEVICE_CLASS_TEMPERATURE,
                "unit": TEMP_CELSIUS,
                "state_class": "measurement"
            },
            ECAttributes.keep_warm_time: {
                "type": "sensor",
                "name": "Keep Warm Time",
                "icon": "mdi:progress-clock",
                "unit": TIME_MINUTES,
                "state_class": "measurement"
            },
            ECAttributes.mode: {
                "type": "sensor",
                "name": "Mode",
                "icon": "mdi:orbit"
            },
            ECAttributes.progress: {
                "type": "sensor",
                "name": "Progress",
                "icon": "mdi:rotate-360"
            },
            ECAttributes.time_remaining: {
                "type": "sensor",
                "name": "Time Remaining",
                "icon": "mdi:progress-clock",
                "unit": TIME_MINUTES,
                "state_class": "measurement"
            },
            ECAttributes.top_temperature: {
                "type": "sensor",
                "name": "Top Temperature",
                "device_class": DEVICE_CLASS_TEMPERATURE,
                "unit": TEMP_CELSIUS,
                "state_class": "measurement"
            },
        }
    }
}
