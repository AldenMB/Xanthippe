from flask import Flask, request
import sqlite3
from explore import BUTTONS

app = Flask(__name__)
allowed_buttons = frozenset(BUTTONS)
allowed_symbols = frozenset(allowed_buttons | {","})


@app.route("/", methods=["POST"])
def receive_buttons():
    if request.content_length > 10_000:
        app.logger.warning(
            f"Received a request of length {request.content_length} bytes"
        )
        return ""
    data = request.get_data(as_text=True)
    if set(data) - allowed_symbols:
        app.logger.warning(f"Received a post with invalid data")
        return ""

    app.logger.info(f"Received a request to check {data}")
    rows = sorted(
        set(
            (buttons[: i + 1],)
            for buttons in data.split(",")
            for i in range(len(buttons))
        )
    )

    con = sqlite3.connect("xanthippe.db")
    with con:
        cur = con.executemany(
            """INSERT INTO sessions(buttons, requested)
            VALUES(?, TRUE)
            ON CONFLICT(buttons) WHERE requested = FALSE
            DO UPDATE SET requested = TRUE""",
            rows,
        )
        app.logger.info(f"updated {cur.rowcount} entries of the database")

    return ""


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=80)
