from homeassistant.const import (
    TIME_DAYS,
    TIME_HOURS,
    TIME_MINUTES,
    TIME_SECONDS,
    TEMP_CELSIUS,
    POWER_WATT,
    PERCENTAGE,
    VOLUME_LITERS,
    ENERGY_KILO_WATT_HOUR,
    CONCENTRATION_MICROGRAMS_PER_CUBIC_METER,
    CONCENTRATION_PARTS_PER_MILLION,
    CONCENTRATION_MILLIGRAMS_PER_CUBIC_METER
)
from homeassistant.components.binary_sensor import BinarySensorDeviceClass
from homeassistant.components.sensor import SensorStateClass, SensorDeviceClass
from .midea.devices.a1.device import DeviceAttributes as A1Attributes
from .midea.devices.ac.device import DeviceAttributes as ACAttributes
from .midea.devices.b0.device import DeviceAttributes as B0Attributes
from .midea.devices.b1.device import DeviceAttributes as B1Attributes
from .midea.devices.b6.device import DeviceAttributes as B6Attributes
from .midea.devices.c3.device import DeviceAttributes as C3Attributes
from .midea.devices.ca.device import DeviceAttributes as CAAttributes
from .midea.devices.cc.device import DeviceAttributes as CCAttributes
from .midea.devices.ce.device import DeviceAttributes as CEAttributes
from .midea.devices.cf.device import DeviceAttributes as CFAttributes
from .midea.devices.da.device import DeviceAttributes as DAAttributes
from .midea.devices.db.device import DeviceAttributes as DBAttributes
from .midea.devices.dc.device import DeviceAttributes as DCAttributes
from .midea.devices.ea.device import DeviceAttributes as EAAttributes
from .midea.devices.ec.device import DeviceAttributes as ECAttributes
from .midea.devices.ed.device import DeviceAttributes as EDAttributes
from .midea.devices.e1.device import DeviceAttributes as E1Attributes
from .midea.devices.e2.device import DeviceAttributes as E2Attributes
from .midea.devices.e3.device import DeviceAttributes as E3Attributes
from .midea.devices.fa.device import DeviceAttributes as FAAttributes
from .midea.devices.fb.device import DeviceAttributes as FBAttributes
from .midea.devices.fc.device import DeviceAttributes as FCAttributes
from .midea.devices.fd.device import DeviceAttributes as FDAttributes


MIDEA_DEVICES = {
    0xA1: {
        "name": "Dehumidifier",
        "entities": {
            "humidifier": {
                "type": "humidifier",
                "icon": "mdi:air-humidifier",
                "default": True
            },
            A1Attributes.child_lock: {
                "type": "lock",
                "name": "Child Lock",
            },
            A1Attributes.anion: {
                "type": "switch",
                "name": "Anion",
                "icon": "mdi:vanish"
            },
            A1Attributes.prompt_tone: {
                "type": "switch",
                "name": "Prompt Tone",
                "icon": "mdi:bell"
            },
            A1Attributes.power: {
                "type": "switch",
                "name": "Power",
                "icon": "mdi:power"
            },
            A1Attributes.swing: {
                "type": "switch",
                "name": "swing",
                "icon": "mdi:pan-horizontal"
            },
            A1Attributes.fan_speed: {
                "type": "select",
                "name": "Fan Speed",
                "options": "fan_speeds",
                "icon": "mdi:fan"
            },
            A1Attributes.water_level_set: {
                "type": "select",
                "name": "Water Level Setting",
                "options": "water_level_sets",
                "icon": "mdi:cup-water"
            },
            A1Attributes.current_humidity: {
                "type": "sensor",
                "name": "Current Humidity",
                "device_class": SensorDeviceClass.HUMIDITY,
                "unit": PERCENTAGE,
                "state_class": SensorStateClass.MEASUREMENT
            }
        }
    },
    0xAC: {
        "name": "Air Conditioner",
        "entities": {
            "climate": {
                "type": "climate",
                "icon": "mdi:air-conditioner",
                "default": True
            },
            "fresh_air": {
                "type": "fan",
                "icon": "mdi:fan",
                "name": "Fresh Air"
            },
            ACAttributes.aux_heat: {
                "type": "switch",
                "name": "Aux Heating",
                "icon": "mdi:heat-wave"
            },
            ACAttributes.boost_mode: {
                "type": "switch",
                "name": "Boost Mode",
                "icon": "mdi:turbine"
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
                "icon": "mdi:leaf-circle"
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
                "device_class": SensorDeviceClass.HUMIDITY,
                "unit": PERCENTAGE,
                "state_class": SensorStateClass.MEASUREMENT
            },
            ACAttributes.indoor_temperature: {
                "type": "sensor",
                "name": "Indoor Temperature",
                "device_class": SensorDeviceClass.TEMPERATURE,
                "unit": TEMP_CELSIUS,
                "state_class": SensorStateClass.MEASUREMENT
            },
            ACAttributes.outdoor_temperature: {
                "type": "sensor",
                "name": "Outdoor Temperature",
                "device_class": SensorDeviceClass.TEMPERATURE,
                "unit": TEMP_CELSIUS,
                "state_class": SensorStateClass.MEASUREMENT
            },
            ACAttributes.total_energy_consumption: {
                "type": "sensor",
                "name": "Total Energy Consumption",
                "device_class": SensorDeviceClass.ENERGY,
                "unit": ENERGY_KILO_WATT_HOUR,
                "state_class": SensorStateClass.TOTAL_INCREASING
            },
            ACAttributes.current_energy_consumption: {
                "type": "sensor",
                "name": "Current Energy Consumption",
                "device_class": SensorDeviceClass.ENERGY,
                "unit": ENERGY_KILO_WATT_HOUR,
                "state_class": SensorStateClass.MEASUREMENT
            },
            ACAttributes.realtime_power: {
                "type": "sensor",
                "name": "Realtime Power",
                "device_class": SensorDeviceClass.POWER,
                "unit": POWER_WATT,
                "state_class": SensorStateClass.MEASUREMENT
            }
        }
    },
    0xB0: {
        "name": "Microwave Oven",
        "entities": {
            B0Attributes.door: {
                "type": "binary_sensor",
                "name": "Door",
                "icon": "mdi:box-shadow",
                "device_class": BinarySensorDeviceClass.DOOR
            },
            B0Attributes.tank_ejected: {
                "type": "binary_sensor",
                "name": "Tank ejected",
                "icon": "mdi:cup-water",
                "device_class": BinarySensorDeviceClass.PROBLEM
            },
            B0Attributes.water_change_reminder: {
                "type": "binary_sensor",
                "name": "Water Change Reminder",
                "icon": "mdi:cup-water",
                "device_class": BinarySensorDeviceClass.PROBLEM
            },
            B0Attributes.water_shortage: {
                "type": "binary_sensor",
                "name": "Water Shortage",
                "icon": "mdi:cup-water",
                "device_class": BinarySensorDeviceClass.PROBLEM
            },
            B0Attributes.current_temperature: {
                "type": "sensor",
                "name": "Current Temperature",
                "device_class": SensorDeviceClass.TEMPERATURE,
                "unit": TEMP_CELSIUS,
                "state_class": SensorStateClass.MEASUREMENT
            },
            B0Attributes.status: {
                "type": "sensor",
                "name": "Status",
                "icon": "mdi:information",
            },
            B0Attributes.time_remaining: {
                "type": "sensor",
                "name": "Time Remaining",
                "icon": "mdi:progress-clock",
                "unit": TIME_SECONDS,
                "state_class": SensorStateClass.MEASUREMENT
            }
        }
    },
    0xB1: {
        "name": "Oven",
        "entities": {
            B1Attributes.door: {
                "type": "binary_sensor",
                "name": "Door",
                "icon": "mdi:box-shadow",
                "device_class": BinarySensorDeviceClass.DOOR
            },
            B1Attributes.tank_ejected: {
                "type": "binary_sensor",
                "name": "Tank ejected",
                "icon": "mdi:cup-water",
                "device_class": BinarySensorDeviceClass.PROBLEM
            },
            B1Attributes.water_change_reminder: {
                "type": "binary_sensor",
                "name": "Water Change Reminder",
                "icon": "mdi:cup-water",
                "device_class": BinarySensorDeviceClass.PROBLEM
            },
            B1Attributes.water_shortage: {
                "type": "binary_sensor",
                "name": "Water Shortage",
                "icon": "mdi:cup-water",
                "device_class": BinarySensorDeviceClass.PROBLEM
            },
            B1Attributes.current_temperature: {
                "type": "sensor",
                "name": "Current Temperature",
                "device_class": SensorDeviceClass.TEMPERATURE,
                "unit": TEMP_CELSIUS,
                "state_class": SensorStateClass.MEASUREMENT
            },
            B1Attributes.status: {
                "type": "sensor",
                "name": "Status",
                "icon": "mdi:information",
            },
            B1Attributes.time_remaining: {
                "type": "sensor",
                "name": "Time Remaining",
                "icon": "mdi:progress-clock",
                "unit": TIME_SECONDS,
                "state_class": SensorStateClass.MEASUREMENT
            }
        }
    },
    0xB6: {
        "name": "Range Hood",
        "entities": {
            "fan": {
                "type": "fan",
                "icon": "mdi:fan",
                "default": True
            },
            B6Attributes.light: {
                "type": "switch",
                "name": "Light",
                "icon": "mdi:lightbulb"
            },
            B6Attributes.power: {
                "type": "switch",
                "name": "Power",
                "icon": "mdi:power"
            },
            B6Attributes.cleaning_reminder: {
                "type": "binary_sensor",
                "name": "Cleaning Reminder",
                "icon": "mdi:alert-circle",
                "device_class": BinarySensorDeviceClass.PROBLEM
            },
            B6Attributes.oilcup_full: {
                "type": "binary_sensor",
                "name": "Oil-cup Full",
                "icon": "mdi:cup",
                "device_class": BinarySensorDeviceClass.PROBLEM
            },
            B6Attributes.fan_level: {
                "type": "sensor",
                "name": "Fan level",
                "icon": "mdi:fan",
                "state_class": SensorStateClass.MEASUREMENT
            },
        }
    },
    0xC3: {
        "name": "Heat Pump Wi-Fi Controller",
        "entities": {
            "climate_zone1": {
                "type": "climate",
                "icon": "mdi:air-conditioner",
                "name": "Zone1 Thermostat",
                "zone": 0,
                "default": True
            },
            "climate_zone2": {
                "type": "climate",
                "icon": "mdi:air-conditioner",
                "name": "Zone2 Thermostat",
                "zone": 1,
                "default": True
            },
            "water-heater": {
                "type": "water_heater",
                "icon": "mdi:heat-pump",
                "name": "Domestic hot water",
                "default": True
            },
            C3Attributes.disinfect: {
                "type": "switch",
                "name": "Disinfect",
                "icon": "mdi:water-plus-outline"
            },
            C3Attributes.dhw_power: {
                "type": "switch",
                "name": "DHW Power",
                "icon": "mdi:power"
            },
            C3Attributes.fast_dhw: {
                "type": "switch",
                "name": "Fast DHW",
                "icon": "mdi:rotate-orbit"
            },
            C3Attributes.zone1_curve: {
                "type": "switch",
                "name": "Zone1 Curve",
                "icon": "mdi:chart-bell-curve-cumulative"
            },
            C3Attributes.zone2_curve: {
                "type": "switch",
                "name": "Zone2 Curve",
                "icon": "mdi:chart-bell-curve-cumulative"
            },
            C3Attributes.zone1_power: {
                "type": "switch",
                "name": "Zone1 Power",
                "icon": "mdi:power"
            },
            C3Attributes.zone2_power: {
                "type": "switch",
                "name": "Zone2 Power",
                "icon": "mdi:power"
            },
            C3Attributes.zone1_water_temp_mode: {
                "type": "binary_sensor",
                "name": "Zone1 Water-temperature Mode",
                "icon": "mdi:coolant-temperature",
                "device_class": BinarySensorDeviceClass.RUNNING,
            },
            C3Attributes.zone2_water_temp_mode: {
                "type": "binary_sensor",
                "name": "Zone2 Water-temperature Mode",
                "icon": "mdi:coolant-temperature",
                "device_class": BinarySensorDeviceClass.RUNNING,
            },
            C3Attributes.zone1_room_temp_mode: {
                "type": "binary_sensor",
                "name": "Zone1 Room-temperature Mode",
                "icon": "mdi:home-thermometer-outline",
                "device_class": BinarySensorDeviceClass.RUNNING,
            },
            C3Attributes.zone2_room_temp_mode: {
                "type": "binary_sensor",
                "name": "Zone2 Room-temperature Mode",
                "icon": "mdi:home-thermometer-outline",
                "device_class": BinarySensorDeviceClass.RUNNING,
            },
            C3Attributes.tank_actual_temperature: {
                "type": "sensor",
                "name": "Tank Actual Temperature",
                "device_class": SensorDeviceClass.TEMPERATURE,
                "unit": TEMP_CELSIUS,
                "state_class": SensorStateClass.MEASUREMENT
            },
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
                "device_class": SensorDeviceClass.TEMPERATURE,
                "unit": TEMP_CELSIUS,
                "state_class": SensorStateClass.MEASUREMENT
            },
            CAAttributes.flex_zone_setting_temp: {
                "type": "sensor",
                "name": "Flex Zone Setting Temperature",
                "device_class": SensorDeviceClass.TEMPERATURE,
                "unit": TEMP_CELSIUS,
                "state_class": SensorStateClass.MEASUREMENT
            },
            CAAttributes.freezer_actual_temp: {
                "type": "sensor",
                "name": "Freezer Actual Temperature",
                "device_class": SensorDeviceClass.TEMPERATURE,
                "unit": TEMP_CELSIUS,
                "state_class": SensorStateClass.MEASUREMENT
            },
            CAAttributes.freezer_setting_temp: {
                "type": "sensor",
                "name": "Freezer Setting Temperature",
                "device_class": SensorDeviceClass.TEMPERATURE,
                "unit": TEMP_CELSIUS,
                "state_class": SensorStateClass.MEASUREMENT
            },
            CAAttributes.energy_consumption: {
                "type": "sensor",
                "name": "Energy Consumption",
                "device_class": SensorDeviceClass.ENERGY,
                "unit": ENERGY_KILO_WATT_HOUR,
                "state_class": SensorStateClass.TOTAL_INCREASING
            },
            CAAttributes.refrigerator_actual_temp: {
                "type": "sensor",
                "name": "Refrigerator Actual Temperature",
                "device_class": SensorDeviceClass.TEMPERATURE,
                "unit": TEMP_CELSIUS,
                "state_class": SensorStateClass.MEASUREMENT
            },
            CAAttributes.refrigerator_setting_temp: {
                "type": "sensor",
                "name": "Refrigerator Setting Temperature",
                "device_class": SensorDeviceClass.TEMPERATURE,
                "unit": TEMP_CELSIUS,
                "state_class": SensorStateClass.MEASUREMENT
            },
            CAAttributes.right_flex_zone_actual_temp: {
                "type": "sensor",
                "name": "Right Flex Zone Actual Temperature",
                "device_class": SensorDeviceClass.TEMPERATURE,
                "unit": TEMP_CELSIUS,
                "state_class": SensorStateClass.MEASUREMENT
            },
            CAAttributes.right_flex_zone_setting_temp: {
                "type": "sensor",
                "name": "Right Flex Zone Setting Temperature",
                "device_class": SensorDeviceClass.TEMPERATURE,
                "unit": TEMP_CELSIUS,
                "state_class": SensorStateClass.MEASUREMENT
            },
        },
    },
    0xCC: {
        "name": "MDV Wi-Fi Controller",
        "entities": {
            "climate": {
                "type": "climate",
                "icon": "hass:air-conditioner",
                "default": True
            },
            CCAttributes.aux_heat: {
                "type": "switch",
                "name": "Aux Heating",
                "icon": "mdi:heat-wave"
            },
            CCAttributes.eco_mode: {
                "type": "switch",
                "name": "ECO Mode",
                "icon": "mdi:leaf-circle"
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
                "device_class": SensorDeviceClass.TEMPERATURE,
                "unit": TEMP_CELSIUS,
                "state_class": SensorStateClass.MEASUREMENT
            },
        }
    },
    0xCE: {
        "name": "Fresh Air Appliance",
        "entities": {
            "fan": {
                "type": "fan",
                "icon": "mdi:fan",
                "default": True
            },
            CEAttributes.filter_cleaning_reminder: {
                "type": "binary_sensor",
                "name": "Filter Cleaning Reminder",
                "icon": "mdi:alert-circle",
                "device_class": BinarySensorDeviceClass.PROBLEM
            },
            CEAttributes.filter_change_reminder: {
                "type": "binary_sensor",
                "name": "Filter Change Reminder",
                "icon": "mdi:alert-circle",
                "device_class": BinarySensorDeviceClass.PROBLEM
            },
            CEAttributes.current_humidity: {
                "type": "sensor",
                "name": "Current Humidity",
                "device_class": SensorDeviceClass.HUMIDITY,
                "unit": PERCENTAGE,
                "state_class": SensorStateClass.MEASUREMENT
            },
            CEAttributes.current_temperature: {
                "type": "sensor",
                "name": "Current Temperature",
                "device_class": SensorDeviceClass.TEMPERATURE,
                "unit": TEMP_CELSIUS,
                "state_class": SensorStateClass.MEASUREMENT
            },
            CEAttributes.co2: {
                "type": "sensor",
                "name": "Carbon Dioxide",
                "device_class": SensorDeviceClass.CO2,
                "unit": CONCENTRATION_PARTS_PER_MILLION,
                "state_class": SensorStateClass.MEASUREMENT
            },
            CEAttributes.hcho: {
                "type": "sensor",
                "name": "Methanal",
                "icon": "mdi:molecule",
                "unit": CONCENTRATION_MICROGRAMS_PER_CUBIC_METER,
                "state_class": SensorStateClass.MEASUREMENT
            },
            CEAttributes.pm25: {
                "type": "sensor",
                "name": "PM 2.5",
                "device_class": SensorDeviceClass.PM25,
                "unit": CONCENTRATION_MICROGRAMS_PER_CUBIC_METER,
                "state_class": SensorStateClass.MEASUREMENT
            },
            CEAttributes.child_lock: {
                "type": "lock",
                "name": "Child Lock"
            },
            CEAttributes.aux_heat: {
                "type": "switch",
                "name": "Aux Heating",
                "icon": "mdi:heat-wave"
            },
            CEAttributes.eco_mode: {
                "type": "switch",
                "name": "ECO Mode",
                "icon": "mdi:leaf-circle"
            },
            CEAttributes.link_to_ac: {
                "type": "switch",
                "name": "Link to AC",
                "icon": "mdi:link"
            },
            CEAttributes.power: {
                "type": "switch",
                "name": "Power",
                "icon": "mdi:power"
            },
            CEAttributes.powerful_purify: {
                "type": "switch",
                "name": "Powerful Purification",
                "icon": "mdi:turbine"
            },
            CEAttributes.sleep_mode: {
                "type": "switch",
                "name": "Sleep Mode",
                "icon": "mdi:power-sleep"
            },
        }
    },
    0xCF: {
        "name": "Heat Pump",
        "entities": {
            "climate": {
                "type": "climate",
                "icon": "hass:air-conditioner",
                "default": True
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
                "device_class": SensorDeviceClass.TEMPERATURE,
                "unit": TEMP_CELSIUS,
                "state_class": SensorStateClass.MEASUREMENT
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
                "state_class": SensorStateClass.MEASUREMENT
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
                "state_class": SensorStateClass.MEASUREMENT
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
                "state_class": SensorStateClass.MEASUREMENT
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
                "state_class": SensorStateClass.MEASUREMENT
            },
            E1Attributes.time_remaining: {
                "type": "sensor",
                "name": "Time Remaining",
                "icon": "mdi:progress-clock",
                "unit": TIME_MINUTES,
                "state_class": SensorStateClass.MEASUREMENT
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
                "icon": "mdi:meter-electric-outline",
                "default": True
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
                "device_class": SensorDeviceClass.TEMPERATURE,
                "unit": TEMP_CELSIUS,
                "state_class": SensorStateClass.MEASUREMENT
            },
            E2Attributes.heating_time_remaining: {
                "type": "sensor",
                "name": "Heating Time Remaining",
                "icon": "mdi:progress-clock",
                "unit": TIME_MINUTES,
                "state_class": SensorStateClass.MEASUREMENT
            },
            E2Attributes.heating_power: {
                "type": "sensor",
                "name": "Heating Power",
                "device_class": SensorDeviceClass.POWER,
                "unit": POWER_WATT,
                "state_class": SensorStateClass.MEASUREMENT
            },
            E2Attributes.water_consumption:{
                "type": "sensor",
                "name": "Water Consumption",
                "icon": "mdi:water",
                "unit": VOLUME_LITERS,
                "state_class": SensorStateClass.TOTAL_INCREASING
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
                "icon": "mdi:meter-gas",
                "default": True
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
                "device_class": SensorDeviceClass.TEMPERATURE,
                "unit": TEMP_CELSIUS,
                "state_class": SensorStateClass.MEASUREMENT
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
                "device_class": SensorDeviceClass.TEMPERATURE,
                "unit": TEMP_CELSIUS,
                "state_class": SensorStateClass.MEASUREMENT
            },
            EAAttributes.keep_warm_time: {
                "type": "sensor",
                "name": "Keep Warm Time",
                "icon": "mdi:progress-clock",
                "unit": TIME_MINUTES,
                "state_class": SensorStateClass.MEASUREMENT
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
                "state_class": SensorStateClass.MEASUREMENT
            },
            EAAttributes.top_temperature: {
                "type": "sensor",
                "name": "Top Temperature",
                "device_class": SensorDeviceClass.TEMPERATURE,
                "unit": TEMP_CELSIUS,
                "state_class": SensorStateClass.MEASUREMENT
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
                "device_class": SensorDeviceClass.TEMPERATURE,
                "unit": TEMP_CELSIUS,
                "state_class": SensorStateClass.MEASUREMENT
            },
            ECAttributes.keep_warm_time: {
                "type": "sensor",
                "name": "Keep Warm Time",
                "icon": "mdi:progress-clock",
                "unit": TIME_MINUTES,
                "state_class": SensorStateClass.MEASUREMENT
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
                "state_class": SensorStateClass.MEASUREMENT
            },
            ECAttributes.top_temperature: {
                "type": "sensor",
                "name": "Top Temperature",
                "device_class": SensorDeviceClass.TEMPERATURE,
                "unit": TEMP_CELSIUS,
                "state_class": SensorStateClass.MEASUREMENT
            },
        }
    },
    0xED: {
        "name": "Water Drinking Appliance",
        "entities": {
            EDAttributes.child_lock: {
                "type": "lock",
                "name": "Child Lock"
            },
            EDAttributes.power: {
                "type": "switch",
                "name": "Power",
                "icon": "mdi:power"
            },
            EDAttributes.filter1: {
                "type": "sensor",
                "name": "Filter1 Available Days",
                "icon": "mdi:air-filter",
                "unit": TIME_DAYS,
                "state_class": SensorStateClass.MEASUREMENT
            },
            EDAttributes.filter2: {
                "type": "sensor",
                "name": "Filter2 Available Days",
                "icon": "mdi:air-filter",
                "unit": TIME_DAYS,
                "state_class": SensorStateClass.MEASUREMENT
            },
            EDAttributes.filter3: {
                "type": "sensor",
                "name": "Filter3 Available Days",
                "icon": "mdi:air-filter",
                "unit": TIME_DAYS,
                "state_class": SensorStateClass.MEASUREMENT
            },
            EDAttributes.life1: {
                "type": "sensor",
                "name": "Filter1 Life Level",
                "icon": "mdi:percent",
                "unit": PERCENTAGE,
                "state_class": SensorStateClass.MEASUREMENT
            },
            EDAttributes.life2: {
                "type": "sensor",
                "name": "Filter2 Life Level",
                "icon": "mdi:percent",
                "unit": PERCENTAGE,
                "state_class": SensorStateClass.MEASUREMENT
            },
            EDAttributes.life3: {
                "type": "sensor",
                "name": "Filter3 Life Level",
                "icon": "mdi:percent",
                "unit": PERCENTAGE,
                "state_class": SensorStateClass.MEASUREMENT
            },
            EDAttributes.in_tds: {
                "type": "sensor",
                "name": "In TDS",
                "icon": "mdi:water",
                "unit": CONCENTRATION_PARTS_PER_MILLION,
                "state_class": SensorStateClass.MEASUREMENT
            },
            EDAttributes.out_tds: {
                "type": "sensor",
                "name": "Out TDS",
                "icon": "mdi:water-plus",
                "unit": CONCENTRATION_PARTS_PER_MILLION,
                "state_class": SensorStateClass.MEASUREMENT
            },
            EDAttributes.water_yield: {
                "type": "sensor",
                "name": "Water Yield",
                "icon": "mdi:water-pump",
                "unit": VOLUME_LITERS,
                "state_class": SensorStateClass.TOTAL_INCREASING
            }
        }
    },
    0xFA: {
        "name": "Fan",
        "entities": {
            "fan": {
                "type": "fan",
                "icon": "mdi:fan",
                "default": True
            },
            FAAttributes.oscillation_mode: {
                "type": "select",
                "name": "Oscillation Mode",
                "options": "oscillation_modes",
                "icon": "mdi:swap-horizontal-variant"
            },
            FAAttributes.oscillation_angle: {
                "type": "select",
                "name": "Oscillation Angle",
                "options": "oscillation_angles",
                "icon": "mdi:pan-horizontal"
            },
            FAAttributes.tilting_angle: {
                "type": "select",
                "name": "Tilting Angle",
                "options": "tilting_angles",
                "icon": "mdi:pan-vertical"
            },
            FAAttributes.child_lock: {
                "type": "lock",
                "name": "Child Lock"
            },
            FAAttributes.oscillate: {
                "type": "switch",
                "name": "Oscillate",
                "icon": "mdi:swap-horizontal-bold"
            },
            FAAttributes.power: {
                "type": "switch",
                "name": "Power",
                "icon": "mdi:power"
            },
        }
    },
    0xFB: {
        "name": "Electric Heater",
        "entities": {
            "climate": {
                "type": "climate",
                "icon": "mdi:air-conditioner",
                "default": True
            },
            FBAttributes.child_lock: {
                "type": "lock",
                "name": "Child Lock",
            },
            FBAttributes.heating_level: {
                "type": "number",
                "name": "Heating Level",
                "icon": "mdi:fire",
                "max": 10,
                "min": 1,
                "step": 1
            },
            FBAttributes.power: {
                "type": "switch",
                "name": "Power",
                "icon": "mdi:power"
            },
            FBAttributes.current_temperature: {
                "type": "sensor",
                "name": "Current Temperature",
                "device_class": SensorDeviceClass.TEMPERATURE,
                "unit": TEMP_CELSIUS,
                "state_class": SensorStateClass.MEASUREMENT
            },
        }
    },
    0xFC: {
        "name": "Air Purifier",
        "entities": {
            FCAttributes.child_lock: {
                "type": "lock",
                "name": "Child Lock",
            },
            FCAttributes.anion: {
                "type": "switch",
                "name": "Anion",
                "icon": "mdi:vanish"
            },
            FCAttributes.prompt_tone: {
                "type": "switch",
                "name": "Prompt Tone",
                "icon": "mdi:bell"
            },
            FCAttributes.power: {
                "type": "switch",
                "name": "Power",
                "icon": "mdi:power"
            },
            FCAttributes.standby: {
                "type": "switch",
                "name": "Standby",
                "icon": "mdi:smoke-detector-variant"
            },
            FCAttributes.detect_mode: {
                "type": "select",
                "name": "Detect Mode",
                "options": "detect_modes",
                "icon": "mdi:smoke-detector-variant"
            },
            FCAttributes.mode: {
                "type": "select",
                "name": "Mode",
                "options": "modes",
                "icon": "mdi:rotate-360"
            },
            FCAttributes.fan_speed: {
                "type": "select",
                "name": "Fan Speed",
                "options": "fan_speeds",
                "icon": "mdi:fan"
            },
            FCAttributes.screen_display: {
                "type": "select",
                "name": "Screen Display",
                "options": "screen_displays",
                "icon": "mdi:television-ambient-light"
            },
            FCAttributes.pm25: {
                "type": "sensor",
                "name": "PM 2.5",
                "device_class": SensorDeviceClass.PM25,
                "unit": CONCENTRATION_MICROGRAMS_PER_CUBIC_METER,
                "state_class": SensorStateClass.MEASUREMENT
            },
            FCAttributes.tvoc: {
                "type": "sensor",
                "name": "TVOC",
                "icon": "mdi:heat-wave",
                "unit": CONCENTRATION_PARTS_PER_MILLION,
                "state_class": SensorStateClass.MEASUREMENT
            },
            FCAttributes.hcho: {
                "type": "sensor",
                "name": "Methanal",
                "icon": "mdi:molecule",
                "unit": CONCENTRATION_MICROGRAMS_PER_CUBIC_METER,
                "state_class": SensorStateClass.MEASUREMENT
            },
            FCAttributes.filter1_life: {
                "type": "sensor",
                "name": "Filter1 Life Level",
                "icon": "mdi:air-filter",
                "unit": PERCENTAGE,
                "state_class": SensorStateClass.MEASUREMENT
            },
            FCAttributes.filter2_life: {
                "type": "sensor",
                "name": "Filter2 Life Level",
                "icon": "mdi:air-filter",
                "unit": PERCENTAGE,
                "state_class": SensorStateClass.MEASUREMENT
            }
        }
    },
    0xFD: {
        "name": "Humidifier",
        "entities": {
            "humidifier": {
                "type": "humidifier",
                "icon": "mdi:air-humidifier",
                "default": True
            },
            FDAttributes.disinfect: {
                "type": "switch",
                "name": "Disinfect",
                "icon": "mdi:water-plus-outline"
            },
            FDAttributes.prompt_tone: {
                "type": "switch",
                "name": "Prompt Tone",
                "icon": "mdi:bell"
            },
            FDAttributes.power: {
                "type": "switch",
                "name": "Power",
                "icon": "mdi:power"
            },
            FDAttributes.fan_speed: {
                "type": "select",
                "name": "Fan Speed",
                "options": "fan_speeds",
                "icon": "mdi:fan"
            },
            FDAttributes.screen_display: {
                "type": "select",
                "name": "Screen Display",
                "options": "screen_displays",
                "icon": "mdi:television-ambient-light"
            },
            FDAttributes.current_humidity: {
                "type": "sensor",
                "name": "Current Humidity",
                "device_class": SensorDeviceClass.HUMIDITY,
                "unit": PERCENTAGE,
                "state_class": SensorStateClass.MEASUREMENT
            },
            FDAttributes.current_temperature: {
                "type": "sensor",
                "name": "Current Temperature",
                "device_class": SensorDeviceClass.TEMPERATURE,
                "unit": TEMP_CELSIUS,
                "state_class": SensorStateClass.MEASUREMENT
            }
        }
    },
}
