from homeassistant.const import Platform
DOMAIN = "midea_ac_lan"
COMPONENT = "component"
DEVICES = "devices"
CONF_KEY = "key"
CONF_MODEL = "model"
EXTRA_SENSOR = [Platform.SENSOR, Platform.BINARY_SENSOR]
EXTRA_SWITCH = [Platform.SWITCH, Platform.LOCK, Platform.SELECT, Platform.NUMBER]
EXTRA_CONTROL = [Platform.CLIMATE, Platform.WATER_HEATER, Platform.FAN, Platform.HUMIDIFIER, Platform.LIGHT] + \
                EXTRA_SWITCH
ALL_PLATFORM = EXTRA_SENSOR + EXTRA_CONTROL
MIDEA_DEFAULT_ACCOUNT = 'b99226f1659e9308@hotmail.com'
MIDEA_DEFAULT_PASSWORD = '_d0e4e9546a738d_'
MIDEA_DEFAULT_SERVER = "MSmartHome" # MSmartHome/美居/SmartLife
