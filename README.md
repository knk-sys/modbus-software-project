# Modbus Software Project
This project is a Modbus scanner application that uses Flask for the web interface and Python's minimalmodbus and pyserial libraries to interact with Modbus devices over USB. It allows you to scan for Modbus-compatible devices connected to your computer, detect their communication settings (baud rate, parity, stop bits), and display the results in a web interface.

# Features
i. Scan for USB Modbus devices connected to your system.

ii. Automatically detect Modbus settings like baud rate, parity, and stop bits.

iii. Display results of the scan via a web interface built with Flask.

iv. Start and stop the scanning process via the web interface.

# Prerequisites
## Software Requirements

1. Python 3.x

2. Flask

3. minimalmodbus

4. pyserial

5. Git

6. pip

# Setup
1. Clone the Repository

``` bash
git clone https://github.com/yourusername/modbus-software-project.git

cd modbus-software-project
```

2. Set up the Python Virtual Environment

```bash 
python3 -m venv venv

source venv/bin/activate
```

3. Install Required Dependencies

```bash
pip install -r requirements.txt
```

4. Run the Application Locally

```bash
python app.py
```