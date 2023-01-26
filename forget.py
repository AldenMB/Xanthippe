from calculator import BUTTON_CODES

import sqlite3


def decode(buttons):
    return "".join(BUTTON_CODES[b] for b in buttons.split(' '))

def count(buttons, con):
    with con:
        con.execute("PRAGMA case_sensitive_like = True;")
        cursor = con.execute(
            "SELECT COUNT(*) FROM sessions WHERE buttons LIKE (? || '%')", [buttons]
        )
        affected, = cursor.fetchone()
        return affected
    

def forget(buttons, con):
    with con:
        con.execute("PRAGMA case_sensitive_like = True;")
        con.execute(
            "UPDATE sessions SET screen = NULL WHERE buttons LIKE (? || '%')", [buttons]
        )
        con.execute(
            "UPDATE sessions SET requested = TRUE WHERE buttons = :start;", [buttons]
        )


if __name__ == "__main__":
    buttons = input("Enter buttons to forget separated by spaces> ")
    buttons = decode(buttons)
    if buttons:
        con = sqlite3.connect("xanthippe.db")
        affected = count(buttons, con)
        confirm = input(f"This will affect {affected} entries. Are you sure? Type y to continue > ")
        if confirm == 'y':
            forget(buttons)
