# ioBroker Adapter für Midea Klimageräte (LAN)

Dies ist ein ioBroker-Adapter, der als Basis für die Integration von Midea-Klimageräten dient. Die Gerätekommunikation muss noch aus dem Python-Code (Home Assistant) nach JavaScript portiert werden.

## Struktur
- `main.js`: Adapter-Logik
- `lib/midea-device.js`: Platzhalter für die Gerätekommunikation
- `package.json`, `io-package.json`: Metadaten

## TODO
- Protokoll-Logik aus `custom_components/midea_ac_lan/midea/core/device.py` und verwandten Dateien nach JavaScript portieren
- Admin-UI für Konfiguration
- Erweiterung für weitere Gerätetypen

## Entwicklung
1. Adapter in ioBroker installieren (als benutzerdefinierten Adapter)
2. Konfiguration (IP, Token, Key) im Admin-UI ergänzen
3. Protokoll-Logik implementieren

## Lizenz
MIT
