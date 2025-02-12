from flask import Flask, request, jsonify
import minimalmodbus
import serial.tools.list_ports

app = Flask(__name__)

def find_usb_modbus_port():
    """Find USB Modbus device from available COM ports."""
    ports = serial.tools.list_ports.comports()
    for port in ports:
        if "USB" in port.description or "Modbus" in port.description:
            return port.device
    return None

@app.route('/scan', methods=['GET'])
def scan_modbus():
    """Scan for Modbus devices and return JSON response."""
    port = find_usb_modbus_port()
    if not port:
        return jsonify({"error": "No Modbus device found!"}), 400

    start_id = int(request.args.get("start_id", 1))
    stop_id = int(request.args.get("stop_id", 2))

    detected_devices = {}
    for slave_id in range(start_id, stop_id + 1):
        try:
            instrument = minimalmodbus.Instrument(port, slave_id)
            instrument.serial.baudrate = 9600
            instrument.serial.parity = 'N'
            instrument.serial.stopbits = 1
            instrument.serial.timeout = 0.5
            value = instrument.read_register(0, functioncode=3)
            detected_devices[slave_id] = {"value": value}
        except Exception:
            pass  # Ignore failures

    return jsonify(detected_devices)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
