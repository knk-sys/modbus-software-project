from flask import Flask, render_template, request, jsonify
import minimalmodbus
import serial.tools.list_ports
import threading

app = Flask(__name__)
version = "Aung V1.00"
stop_scan_flag = False  # Global flag to stop the scanning process

def find_usb_modbus_port():
    """Find USB Modbus device from available COM ports."""
    ports = serial.tools.list_ports.comports()
    for port in ports:
        if "USB" in port.description or "Modbus" in port.description:
            return port.device
    return None


def detect_modbus_settings(port, start_id, stop_id, progress_callback):
    """Scan for working Modbus settings and detect devices automatically."""
    global stop_scan_flag
    baud_rates = [9600, 19200]
    parities = ['N', 'E', 'O']  # None, Even, Odd
    stop_bits = [1, 2]
    detected_devices = {}

    modbus_registers = [
        {"register": 0, "function_code": 3},    # Holding register 40001
        {"register": 9, "function_code": 3},    # Holding register 40010
        {"register": 2000, "function_code": 4}, # Input register 42001
        {"register": 2099, "function_code": 4}, # Input register 42100
    ]

    total_checks = (len(baud_rates) * len(parities) * len(stop_bits) *
                    (stop_id - start_id + 1) * len(modbus_registers))
    completed_checks = 0

    for baud_rate in baud_rates:
        for parity in parities:
            for stop_bit in stop_bits:
                for slave_id in range(start_id, stop_id + 1):
                    if stop_scan_flag:  # Stop if the flag is set
                        return detected_devices
                    if slave_id in detected_devices:
                        continue
                    for reg in modbus_registers:
                        try:
                            instrument = minimalmodbus.Instrument(port, slave_id)
                            instrument.serial.baudrate = baud_rate
                            instrument.serial.parity = parity
                            instrument.serial.stopbits = stop_bit
                            instrument.serial.timeout = 0.5

                            value = instrument.read_register(
                                reg["register"], functioncode=reg["function_code"]
                            )
                            detected_devices[slave_id] = {
                                'baud_rate': baud_rate,
                                'parity': parity,
                                'stop_bits': stop_bit,
                                'register': reg["register"],
                                'function_code': reg["function_code"],
                                'value': value
                            }
                            break  # Stop checking registers if one works
                        except Exception:
                            pass
                        finally:
                            # Update progress
                            completed_checks += 1
                            progress_percentage = int((completed_checks / total_checks) * 100)
                            progress_callback(progress_percentage)

    return detected_devices

@app.route('/')
def home():
    return render_template('index.html', version=version)

@app.route('/start_scan', methods=['POST'])
def start_scan():
    global stop_scan_flag
    stop_scan_flag = False
    port = find_usb_modbus_port()
    if not port:
        return jsonify({"error": "No Modbus device found!"})

    try:
        start_id = int(request.form['start_id'])
        stop_id = int(request.form['stop_id'])

        if start_id > stop_id:
            return jsonify({"error": "Start ID must be less than or equal to Stop ID!"})

        result = {"status": "Scanning started..."}
        def scan_thread():
            def update_progress(progress):
                result["status"] = f"Scanning... {progress}% completed"
                if progress == 100:
                    result["status"] = "Scanning completed!"
                app.logger.info(result["status"])

            results = detect_modbus_settings(port, start_id, stop_id, update_progress)

            # Prepare results
            if results:
                result["devices"] = [
                    {"slave_id": slave_id, "baud_rate": device['baud_rate'], "parity": device['parity'],
                     "stop_bits": device['stop_bits']} for slave_id, device in results.items()
                ]
            else:
                result["status"] = "No devices detected."
                result["devices"] = []

        threading.Thread(target=scan_thread).start()

        return jsonify(result)

    except ValueError:
        return jsonify({"error": "Please enter valid numeric values for Start and Stop IDs!"})

@app.route('/stop_scan', methods=['POST'])
def stop_scan():
    global stop_scan_flag
    stop_scan_flag = True
    return jsonify({"status": "Scanning stopped."})

if __name__ == "__main__":
    app.run(debug=True)
