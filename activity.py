
from datetime import date, datetime

def log_activity(ws_log, action, status = "Success"):
   ws_log.append([
        datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        action,
        status
    ])

def update_history(ws_history, values):

    row = [
        date.today(),
        values["Dow"]["price"],
        values["S&P 500"]["price"],
        values["Nasdaq"]["price"]
    ]

    ws_history.append(row)