import serial
import sqlite3
from datetime import datetime

# =========================
# CONFIGURATION
# =========================

PORT = "COM4"
BAUD_RATE = 9600

USERS = {
    "22:BC:BF:22": {
        "name": "Keyona Briggs",
        "worker_id": "2886776"
    },
    "83:BB:AF:A0": {
        "name": "Amy Wilde",
        "worker_id": "2887757"
    }
}


DATABASE = "time_tracker.db"


# =========================
# DATABASE
# =========================

def initialize_database():

    connection = sqlite3.connect(DATABASE)

    cursor = connection.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS work_sessions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            worker_name TEXT NOT NULL,
            worker_id TEXT NOT NULL,
            rfid_uid TEXT NOT NULL,
            sign_in TEXT NOT NULL,
            sign_out TEXT,
            duration_seconds INTEGER,
            status TEXT NOT NULL
        )
    """)

    connection.commit()
    connection.close()


# =========================
# SIGN IN
# =========================

def record_sign_in(uid, timestamp):

    connection = sqlite3.connect(DATABASE)

    cursor = connection.cursor()

    # Prevent duplicate active sessions for the same RFID card.
    cursor.execute("""
        SELECT id, sign_in
        FROM work_sessions
        WHERE rfid_uid = ?
        AND status = 'ACTIVE'
        ORDER BY id DESC
        LIMIT 1
    """, (uid,))

    active_session = cursor.fetchone()

    if active_session:

        connection.close()

        print(
            f"WARNING: Worker already has an active session "
            f"(session ID {active_session[0]}, "
            f"signed in {active_session[1]})."
        )

        return False

    user = USERS.get(uid)

    if user is None:
        connection.close()
        print("ERROR: Unknown RFID card.")
        return False

    cursor.execute("""
        INSERT INTO work_sessions
        (
            worker_name,
            worker_id,
            rfid_uid,
            sign_in,
            status
        )
        VALUES (?, ?, ?, ?, ?)
    """, (
        user["name"],
        user["worker_id"],
        uid,
        timestamp,
        "ACTIVE"
    ))

    connection.commit()
    connection.close()

    return True


# =========================
# SIGN OUT
# =========================

def record_sign_out(uid, timestamp):

    connection = sqlite3.connect(DATABASE)

    cursor = connection.cursor()

    cursor.execute("""
        SELECT id, sign_in
        FROM work_sessions
        WHERE rfid_uid = ?
        AND status = 'ACTIVE'
        ORDER BY id DESC
        LIMIT 1
    """, (uid,))

    session = cursor.fetchone()

    if session is None:

        connection.close()

        print("WARNING: No active session found.")

        return False

    session_id = session[0]

    sign_in_time = datetime.strptime(
        session[1],
        "%Y-%m-%d %H:%M:%S"
    )

    sign_out_time = datetime.strptime(
        timestamp,
        "%Y-%m-%d %H:%M:%S"
    )

    duration = int(
        (sign_out_time - sign_in_time).total_seconds()
    )

    # Automatically close an active break when RFID sign-out occurs.
    cursor.execute("""
        SELECT id, break_start
        FROM work_breaks
        WHERE session_id = ?
        AND status = 'ACTIVE'
        ORDER BY id DESC
        LIMIT 1
    """, (session_id,))

    active_break = cursor.fetchone()

    if active_break:

        break_id = active_break[0]

        break_start_time = datetime.strptime(
            active_break[1],
            "%Y-%m-%d %H:%M:%S"
        )

        break_duration = max(
            0,
            int((sign_out_time - break_start_time).total_seconds())
        )

        cursor.execute("""
            UPDATE work_breaks
            SET
                break_end = ?,
                duration_seconds = ?,
                status = 'COMPLETED'
            WHERE id = ?
        """, (
            timestamp,
            break_duration,
            break_id
        ))

        print(
            f"Active break automatically closed: "
            f"{break_duration} seconds"
        )

    cursor.execute("""
        UPDATE work_sessions
        SET
            sign_out = ?,
            duration_seconds = ?,
            status = 'COMPLETED'
        WHERE id = ?
    """, (
        timestamp,
        duration,
        session_id
    ))

    connection.commit()
    connection.close()

    print(f"Session duration: {duration} seconds")
    
    return True


# =========================
# SERIAL EVENT PROCESSING
# =========================

def process_event(event):

    parts = event.split(",")

    if len(parts) != 2:
        return

    event_type = parts[0].strip()
    uid = parts[1].strip().upper()

    # Look up the worker associated with this RFID card.
    user = USERS.get(uid)

    if user is None:
        print("Unknown RFID card ignored.")
        return

    worker_name = user["name"]
    worker_id = user["worker_id"]

    timestamp = datetime.now().strftime(
        "%Y-%m-%d %H:%M:%S"
    )

    if event_type == "SIGN_IN":

        sign_in_created = record_sign_in(uid, timestamp)

        if not sign_in_created:
            return

        print()
        print("================================")
        print("          SIGNED IN")
        print("================================")
        print(f"Name:       {worker_name}")
        print(f"Worker ID:  {worker_id}")
        print(f"RFID UID:   {uid}")
        print(f"Sign-in:    {timestamp}")
        print("Status:     ACTIVE")
        print("================================")
        print()

    elif event_type == "SIGN_OUT":

        sign_out_created = record_sign_out(uid, timestamp)

        if not sign_out_created:
            return

        print()
        print("================================")
        print("          SIGNED OUT")
        print("================================")
        print(f"Name:       {worker_name}")
        print(f"Worker ID:  {worker_id}")
        print(f"RFID UID:   {uid}")
        print(f"Sign-out:   {timestamp}")
        print("Status:     COMPLETED")
        print("================================")
        print()


# =========================
# MAIN PROGRAM
# =========================

initialize_database()

print("================================")
print("      RFID TIME TRACKER")
print("================================")
print("Authorized workers:")
for uid, user in USERS.items():
    print(
        f"  {user['name']} | "
        f"Worker ID: {user['worker_id']} | "
        f"RFID: {uid}"
    )
print()
print(f"Connecting to {PORT}...")

arduino = serial.Serial(
    PORT,
    BAUD_RATE,
    timeout=1
)

print(f"Connected to {PORT}")
print("Database ready.")
print("Waiting for RFID events...")
print()

while True:

    line = arduino.readline().decode(
        "utf-8",
        errors="ignore"
    ).strip()

    if not line:
        continue

    print(f"Arduino: {line}")

    if line.startswith("SIGN_IN,"):
        process_event(line)

    elif line.startswith("SIGN_OUT,"):
        process_event(line)

    elif line.startswith("ACCESS_DENIED,"):
        print("Access denied.")