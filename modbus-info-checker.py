import tkinter as tk
from tkinter import messagebox
import minimalmodbus
import serial.tools.list_ports
import threading
version="Aung V1.00"

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


def start_scan():
    global stop_scan_flag
    stop_scan_flag = False
    port = find_usb_modbus_port()
    if not port:
        messagebox.showerror("Error", "No Modbus device found!")
        return

    try:
        start_id = int(start_id_entry.get())
        stop_id = int(stop_id_entry.get())

        if start_id > stop_id:
            messagebox.showerror("Error", "Start ID must be less than or equal to Stop ID!")
            return

        # Clear previous results and show "Please wait" message in the display box
        result_text.delete(1.0, tk.END)
        result_text.insert(tk.END, "⏳ Scanning started...\n")
        root.update()  # Update UI to show the message before scanning

        # Run the detection in a separate thread to keep the UI responsive
        def scan_thread():
            def update_progress(progress):
                result_text.delete("end-2l", tk.END)  # Remove the last line
                result_text.insert(tk.END, f"⏳ Scanning... {progress}% completed\n")

            results = detect_modbus_settings(port, start_id, stop_id, update_progress)

            # Display results
            result_text.delete("end-2l", tk.END)  # Clear "Scanning..." message
            if results:
                result_text.insert(tk.END, f"📋 Detected Modbus Devices at {port}:\n")
                for slave_id, device in results.items():
                    result_text.insert(
                        tk.END,
                        f"🔹 Slave ID={slave_id} | Baud={device['baud_rate']} | "
                        f"Parity={device['parity']} | Stop Bits={device['stop_bits']}\n"
                        # f"Register={device['register']} | Function Code={device['function_code']}\n"
                    )
            else:
                result_text.insert(tk.END, "❌ No devices detected.")

        threading.Thread(target=scan_thread).start()
    except ValueError:
        messagebox.showerror("Error", "Please enter valid numeric values for Start and Stop IDs!")


def stop_scan():
    global stop_scan_flag
    stop_scan_flag = True
    result_text.delete(1.0, tk.END)
    result_text.insert(tk.END, "❌ Scanning stopped. Ready for rescan.\n")


# UI Setup
root = tk.Tk()
root.title(f"Modbus Device Info Scanner_ {version}")
root.geometry("500x400")

tk.Label(root, text="Start Slave ID:").pack()
start_id_entry = tk.Entry(root)
start_id_entry.pack()
start_id_entry.insert(0, "1")  # Set default value to 1

tk.Label(root, text="Stop Slave ID:").pack()
stop_id_entry = tk.Entry(root)
stop_id_entry.pack()
stop_id_entry.insert(0, "2")  # Set default value to 2

button_frame = tk.Frame(root)
button_frame.pack()

start_button = tk.Button(button_frame, text="Start Scan", command=start_scan)
start_button.pack(side=tk.LEFT, padx=5)

stop_button = tk.Button(button_frame, text="Stop Scan", command=stop_scan)
stop_button.pack(side=tk.LEFT, padx=5)

result_text = tk.Text(root, height=10, width=60)
result_text.pack()

root.mainloop()
