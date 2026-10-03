# RFID Time Tracker

A local RFID-based work session tracking system built with **Arduino, RC522 RFID, Python, SQLite, FastAPI, HTML, CSS, and JavaScript**.

The system allows authorized RFID cards to start and stop work sessions, records session activity locally, tracks breaks, and provides a web-based dashboard for monitoring work time and generating reports.

## Features

* RFID-based sign-in and sign-out
* Multi-user RFID authorization
* Unauthorized card detection
* Audible RFID feedback using a buzzer
* Arduino Mega + RC522 RFID reader
* Python serial communication
* Local SQLite database
* FastAPI REST API
* Responsive web dashboard
* Live session timer
* Break tracking
* Daily, weekly, and monthly reporting
* Net work-time calculations
* Session history
* CSV data export
* Automatic application startup
* Local-only architecture

## Architecture

```text
+----------------------+
|      RFID Card       |
+----------+-----------+
           |
           v
+----------------------+
| Arduino Mega + RC522 |
|     RFID Reader      |
+----------+-----------+
           |
           | Serial USB
           v
+----------------------+
|   Python Listener    |
|  RFID Event Handler  |
+----------+-----------+
           |
           v
+----------------------+
|      SQLite DB       |
|   Session Records    |
+----------+-----------+
           |
           v
+----------------------+
|       FastAPI        |
|      REST API        |
+----------+-----------+
           |
           v
+----------------------+
|    Web Dashboard     |
|     HTML / CSS / JS  |
+----------------------+
```

## Hardware

* Arduino Mega
* MFRC522 / RC522 RFID reader
* RFID cards or tags
* Buzzer
* Breadboard
* USB connection

### Pin Configuration

| Component    | Arduino Mega |
| ------------ | -----------: |
| RC522 SS/SDA |           53 |
| RC522 RST    |            5 |
| Buzzer       |            8 |
| SPI          | Hardware SPI |

## Software Stack

| Technology         | Purpose                                  |
| ------------------ | ---------------------------------------- |
| C++ / Arduino      | RFID hardware control                    |
| Python             | Event processing and database management |
| SQLite             | Local session storage                    |
| FastAPI            | REST API and dashboard backend           |
| JavaScript         | Dashboard functionality                  |
| HTML               | Dashboard structure                      |
| CSS                | Dashboard styling                        |
| PowerShell / Batch | Local application startup                |

## RFID Workflow

1. User scans an authorized RFID card.
2. RC522 reads the card UID.
3. Arduino validates the UID against the configured authorization list.
4. Arduino sends the RFID event over serial USB.
5. Python receives and processes the event.
6. The session is stored in SQLite.
7. FastAPI exposes session information through REST endpoints.
8. The web dashboard displays current status and work-time information.

### RFID Events

The Arduino communicates events using serial messages such as:

```text
SIGN_IN,<uid>
SIGN_OUT,<uid>
ACCESS_DENIED,<uid>
```

## Dashboard

The dashboard provides:

* Current session status
* Sign-in time
* Live elapsed work time
* Break status
* Break duration
* Daily totals
* Weekly totals
* Monthly totals
* Net work time
* Session history
* CSV export

The dashboard runs locally at:

```text
http://127.0.0.1:8000
```

## API Endpoints

| Endpoint       | Purpose                     |
| -------------- | --------------------------- |
| `/`            | Dashboard                   |
| `/api/status`  | Current RFID/session status |
| `/api/history` | Session history             |
| `/api/summary` | Work and break summaries    |
| `/api/export`  | CSV session export          |

## Security Considerations

This project demonstrates several practical security concepts:

* RFID-based authorization
* UID allowlisting
* Unauthorized-card rejection
* Local data storage
* Audit-style session records
* Separation between hardware and application layers
* API-based application architecture

### Important Security Limitation

RFID UID-based authorization should **not** be treated as strong authentication.

Many RFID technologies use identifiers that can potentially be copied or cloned. This project uses RFID primarily as a practical hardware authentication demonstration and learning platform.

For higher-security applications, additional authentication factors and cryptographic card authentication would be appropriate.

## Privacy

This repository contains a **sanitized example configuration**.

Do not publish:

* Real employee names
* Employee or worker IDs
* Real RFID UIDs
* Personal session databases
* Credentials
* API keys
* Other sensitive information

The example Arduino configuration uses placeholder RFID values rather than real card identifiers.

## Project Structure

```text
rfid-time-tracker/
|
+-- arduino/
|   +-- rfid_hr_tracker.ino
|
+-- dashboard.py
+-- dashboard.html
+-- dashboard.css
+-- dashboard.js
+-- rfid_listener.py
+-- start_rfid_tracker.bat
+-- .gitignore
+-- README.md
```

## Running the Project

### 1. Connect the Hardware

Connect the Arduino Mega and RC522 RFID reader according to the pin configuration documented above.

### 2. Configure the Arduino

Open:

```text
arduino/rfid_hr_tracker.ino
```

Replace the example RFID UIDs with your own authorized test-card UIDs.

### 3. Configure the Python Listener

Configure the local RFID-to-user mapping in:

```text
rfid_listener.py
```

Keep personal identifiers and real RFID UIDs out of public repositories.

### 4. Start the Application

Run:

```powershell
.\start_rfid_tracker.bat
```

Then open:

```text
http://127.0.0.1:8000
```

## Development Notes

The project was developed incrementally from hardware testing through application integration:

1. RFID reader detection
2. RFID UID identification
3. Arduino sign-in/sign-out events
4. Buzzer feedback
5. Python serial listener
6. SQLite session storage
7. FastAPI backend
8. Web dashboard
9. Break tracking
10. Net work-time calculations
11. CSV reporting
12. Multi-user RFID authorization
13. Automated startup

## Future Improvements

Potential enhancements include:

* Encrypted RFID authentication
* Role-based access control
* User management interface
* Administrative dashboard
* Authentication for the web dashboard
* Remote database support
* Docker deployment
* Automated testing
* Structured application logging
* Configuration through environment variables
* Hardware health monitoring

## Disclaimer

This project is intended for educational, portfolio, and local productivity-tracking purposes.

Do not use RFID UID-only authentication as the sole security mechanism for systems requiring strong identity verification.

## Author

**Keyona Briggs**

Cybersecurity / IT Portfolio Project

GitHub: [Cipher-Key569](https://github.com/Cipher-Key569)
