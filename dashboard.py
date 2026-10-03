from fastapi import FastAPI
from fastapi.responses import HTMLResponse
from fastapi.responses import FileResponse
from fastapi.responses import StreamingResponse
import sqlite3
from datetime import datetime, timedelta
from pathlib import Path
import csv
import io


DB_FILE = "time_tracker.db"

BASE_DIR = Path(__file__).resolve().parent


app = FastAPI(
    title="RFID Time Tracker"
)


def get_connection():
    connection = sqlite3.connect(DB_FILE)
    connection.row_factory = sqlite3.Row
    return connection


@app.get("/", response_class=HTMLResponse)
def home():
    return FileResponse(
        BASE_DIR / "dashboard.html"
    )


@app.get("/dashboard.css")
def css():
    return FileResponse(
        BASE_DIR / "dashboard.css",
        media_type="text/css"
    )


@app.get("/dashboard.js")
def javascript():
    return FileResponse(
        BASE_DIR / "dashboard.js",
        media_type="application/javascript"
    )


@app.get("/api/status")
def get_status():

    connection = get_connection()

    active_session = connection.execute(
        """
        SELECT *
        FROM work_sessions
        WHERE status = 'ACTIVE'
        ORDER BY id DESC
        LIMIT 1
        """
    ).fetchone()

    connection.close()


    if active_session:

        sign_in = datetime.strptime(
            active_session["sign_in"],
            "%Y-%m-%d %H:%M:%S"
        )

        elapsed_seconds = int(
            (
                datetime.now() - sign_in
            ).total_seconds()
        )


        return {
            "status": "ACTIVE",
            "name": active_session["worker_name"],
            "worker_id": active_session["worker_id"],
            "rfid_uid": active_session["rfid_uid"],
            "sign_in": active_session["sign_in"],
            "elapsed_seconds": elapsed_seconds
        }


    return {
        "status": "OFF",
        "name": "Keyona Briggs",
        "worker_id": "2886776",
        "rfid_uid": "22:BC:BF:22",
        "sign_in": None,
        "elapsed_seconds": 0
    }
@app.get("/api/break/status")
def get_break_status():

    connection = get_connection()

    active_session = connection.execute(
        """
        SELECT id
        FROM work_sessions
        WHERE status = 'ACTIVE'
        ORDER BY id DESC
        LIMIT 1
        """
    ).fetchone()

    if not active_session:
        connection.close()

        return {
            "status": "OFF",
            "break_status": "NONE",
            "break_start": None,
            "elapsed_seconds": 0
        }

    active_break = connection.execute(
        """
        SELECT *
        FROM work_breaks
        WHERE session_id = ?
        AND status = 'ACTIVE'
        ORDER BY id DESC
        LIMIT 1
        """,
        (active_session["id"],)
    ).fetchone()

    connection.close()

    if not active_break:
        return {
            "status": "ACTIVE",
            "break_status": "NONE",
            "break_start": None,
            "elapsed_seconds": 0
        }

    break_start = datetime.strptime(
        active_break["break_start"],
        "%Y-%m-%d %H:%M:%S"
    )

    elapsed_seconds = int(
        (datetime.now() - break_start).total_seconds()
    )

    return {
        "status": "ACTIVE",
        "break_status": "ACTIVE",
        "break_start": active_break["break_start"],
        "elapsed_seconds": max(0, elapsed_seconds)
    }


@app.post("/api/break/start")
def start_break():

    connection = get_connection()

    active_session = connection.execute(
        """
        SELECT id
        FROM work_sessions
        WHERE status = 'ACTIVE'
        ORDER BY id DESC
        LIMIT 1
        """
    ).fetchone()

    if not active_session:
        connection.close()

        return {
            "success": False,
            "message": "Cannot start a break while signed out."
        }

    existing_break = connection.execute(
        """
        SELECT id
        FROM work_breaks
        WHERE session_id = ?
        AND status = 'ACTIVE'
        LIMIT 1
        """,
        (active_session["id"],)
    ).fetchone()

    if existing_break:
        connection.close()

        return {
            "success": False,
            "message": "A break is already active."
        }

    break_start = datetime.now().strftime(
        "%Y-%m-%d %H:%M:%S"
    )

    connection.execute(
        """
        INSERT INTO work_breaks (
            session_id,
            break_start,
            status
        )
        VALUES (?, ?, 'ACTIVE')
        """,
        (
            active_session["id"],
            break_start
        )
    )

    connection.commit()
    connection.close()

    return {
        "success": True,
        "message": "Break started.",
        "break_start": break_start
    }


@app.post("/api/break/end")
def end_break():

    connection = get_connection()

    active_session = connection.execute(
        """
        SELECT id
        FROM work_sessions
        WHERE status = 'ACTIVE'
        ORDER BY id DESC
        LIMIT 1
        """
    ).fetchone()

    if not active_session:
        connection.close()

        return {
            "success": False,
            "message": "Cannot end a break while signed out."
        }

    active_break = connection.execute(
        """
        SELECT *
        FROM work_breaks
        WHERE session_id = ?
        AND status = 'ACTIVE'
        ORDER BY id DESC
        LIMIT 1
        """,
        (active_session["id"],)
    ).fetchone()

    if not active_break:
        connection.close()

        return {
            "success": False,
            "message": "No active break found."
        }

    break_start = datetime.strptime(
        active_break["break_start"],
        "%Y-%m-%d %H:%M:%S"
    )

    break_end = datetime.now()

    duration_seconds = max(
        0,
        int((break_end - break_start).total_seconds())
    )

    connection.execute(
        """
        UPDATE work_breaks
        SET
            break_end = ?,
            duration_seconds = ?,
            status = 'COMPLETED'
        WHERE id = ?
        """,
        (
            break_end.strftime("%Y-%m-%d %H:%M:%S"),
            duration_seconds,
            active_break["id"]
        )
    )

    connection.commit()
    connection.close()

    return {
        "success": True,
        "message": "Break ended.",
        "break_end": break_end.strftime(
            "%Y-%m-%d %H:%M:%S"
        ),
        "duration_seconds": duration_seconds
    }

@app.get("/api/history")
def get_history():

    connection = get_connection()

    sessions = connection.execute(
        """
        SELECT
            id,
            worker_name,
            worker_id,
            rfid_uid,
            sign_in,
            sign_out,
            duration_seconds,
            status
        FROM work_sessions
        ORDER BY id DESC
        """
    ).fetchall()

    connection.close()


    return {
        "sessions": [
            dict(session)
            for session in sessions
        ]
    }
@app.get("/api/summary")
def get_summary():
    connection = get_connection()

    sessions = connection.execute(
        """
        SELECT
            sign_in,
            sign_out,
            status
        FROM work_sessions
        ORDER BY sign_in ASC
        """
    ).fetchall()

    breaks = connection.execute(
        """
        SELECT
            break_start,
            break_end,
            status
        FROM work_breaks
        ORDER BY break_start ASC
        """
    ).fetchall()

    connection.close()

    now = datetime.now()

    today_start = now.replace(
        hour=0,
        minute=0,
        second=0,
        microsecond=0
    )

    week_start = today_start - timedelta(
        days=today_start.weekday()
    )

    month_start = today_start.replace(
        day=1
    )

    period_starts = {
        "today": today_start,
        "week": week_start,
        "month": month_start
    }

    work_totals = {
        "today": 0,
        "week": 0,
        "month": 0
    }

    break_totals = {
        "today": 0,
        "week": 0,
        "month": 0
    }

    for session in sessions:

        sign_in = datetime.strptime(
            session["sign_in"],
            "%Y-%m-%d %H:%M:%S"
        )

        if session["sign_out"]:
            sign_out = datetime.strptime(
                session["sign_out"],
                "%Y-%m-%d %H:%M:%S"
            )
        else:
            sign_out = now

        if sign_out <= sign_in:
            continue

        for period_name, period_start in period_starts.items():

            overlap_start = max(
                sign_in,
                period_start
            )

            overlap_end = min(
                sign_out,
                now
            )

            if overlap_end > overlap_start:
                work_totals[period_name] += int(
                    (overlap_end - overlap_start).total_seconds()
                )

    for break_record in breaks:

        break_start = datetime.strptime(
            break_record["break_start"],
            "%Y-%m-%d %H:%M:%S"
        )

        if break_record["break_end"]:
            break_end = datetime.strptime(
                break_record["break_end"],
                "%Y-%m-%d %H:%M:%S"
            )
        else:
            break_end = now

        if break_end <= break_start:
            continue

        for period_name, period_start in period_starts.items():

            overlap_start = max(
                break_start,
                period_start
            )

            overlap_end = min(
                break_end,
                now
            )

            if overlap_end > overlap_start:
                break_totals[period_name] += int(
                    (overlap_end - overlap_start).total_seconds()
                )

    net_totals = {
        "today": max(0, work_totals["today"] - break_totals["today"]),
        "week": max(0, work_totals["week"] - break_totals["week"]),
        "month": max(0, work_totals["month"] - break_totals["month"])
    }

    return {
        "today_seconds": work_totals["today"],
        "week_seconds": work_totals["week"],
        "month_seconds": work_totals["month"],
        "break_today_seconds": break_totals["today"],
        "break_week_seconds": break_totals["week"],
        "break_month_seconds": break_totals["month"],
        "net_today_seconds": net_totals["today"],
        "net_week_seconds": net_totals["week"],
        "net_month_seconds": net_totals["month"]
    }


@app.get("/api/export")
def export_csv():
    connection = get_connection()

    sessions = connection.execute(
        """
        SELECT
            id,
            worker_name,
            worker_id,
            rfid_uid,
            sign_in,
            sign_out,
            duration_seconds,
            status
        FROM work_sessions
        ORDER BY id DESC
        """
    ).fetchall()

    connection.close()

    output = io.StringIO()

    writer = csv.writer(output)

    writer.writerow([
        "ID",
        "Agent Name",
        "Agent ID",
        "RFID UID",
        "Sign In",
        "Sign Out",
        "Duration Seconds",
        "Status"
    ])

    for session in sessions:
        writer.writerow([
            session["id"],
            session["worker_name"],
            session["worker_id"],
            session["rfid_uid"],
            session["sign_in"],
            session["sign_out"],
            session["duration_seconds"],
            session["status"]
        ])

    output.seek(0)

    return StreamingResponse(
        iter([output.getvalue()]),
        media_type="text/csv",
        headers={
            "Content-Disposition":
                "attachment; filename=work_sessions.csv"
        }
    )