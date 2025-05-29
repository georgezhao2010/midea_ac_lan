const utils = require('@iobroker/adapter-core');
const MideaDevice = require('./lib/midea-device');

class Midea extends utils.Adapter {
    constructor(options = {}) {
        super({
            ...options,
            name: 'midea',
        });
        this.on('ready', this.onReady.bind(this));
        this.on('stateChange', this.onStateChange.bind(this));
        this.on('unload', this.onUnload.bind(this));
    }

    async onReady() {
        this.log.info('Midea Adapter gestartet');
        // Beispiel: Gerät initialisieren
        this.device = new MideaDevice({
            ip: this.config.deviceIp,
            token: this.config.deviceToken,
            key: this.config.deviceKey
        });
        await this.device.connect();
        this.log.info('Midea Gerät verbunden');
        // Beispiel: Status abfragen
        const status = await this.device.getStatus();
        this.setState('info.status', status, true);
    }

    async onStateChange(id, state) {
        if (!state || state.ack) return;
        // Beispiel: Temperatur setzen
        if (id.endsWith('setTemperature')) {
            await this.device.setTemperature(state.val);
            this.setState(id, state.val, true);
        }
    }

    onUnload(callback) {
        try {
            if (this.device) this.device.disconnect();
            callback();
        } catch (e) {
            callback();
        }
    }
}

if (module.parent) {
    module.exports = (options) => new Midea(options);
} else {
    new Midea();
}
