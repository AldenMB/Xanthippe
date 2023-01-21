import sqlite3
from calculator import Calculator, BUTTON_CODES
import random
import itertools

BUTTONS = tuple(sorted(set(BUTTON_CODES.values()) - {BUTTON_CODES["reset"]}))
strats = []


def strategy(func):
    strats.append(func)
    return func


class Explorer:
    def __init__(self):
        self.db = sqlite3.connect("xanthippe.db")
        self.calculator = Calculator()
        self.strats = [strat(self) for strat in strats]

    def already_covered(self, target):
        with self.db:
            cur = self.db.execute(
                """SELECT EXISTS(
                SELECT 1 FROM sessions
                WHERE buttons = ?
                AND screen IS NOT NULL)""",
                [target],
            )
            (ans,) = cur.fetchone()
        return ans

    def get_target(self):
        while True:
            try:
                target = next(random.choice(self.strats))
            except StopIteration:
                self.strats.remove(strategy)
                continue
            if target is not None and not self.already_covered(target):
                return target

    def explore(self):
        target = self.get_target()
        screens = self.calculator.session(target)
        buttons = (target[:i] for i in range(1, len(target) + 1))
        data = ({"but": b, "scrn": bytes(s)} for b, s in zip(buttons, screens))
        with self.db:
            self.db.executemany(
                """INSERT INTO sessions(buttons, screen)
                VALUES(:but, :scrn)
                ON CONFLICT(buttons) WHERE screen IS NULL
                DO UPDATE SET screen = :scrn""",
                data,
            )


@strategy
def random_fixed_length(explorer, length=10):
    while True:
        yield "".join(random.choices(BUTTONS, k=length))


@strategy
def alphabetical(explorer):
    for length in itertools.count(1):
        for combo in itertools.combinations_with_replacement(BUTTONS, length):
            yield "".join(combo)


# @strategy
def requested(explorer):
    while True:
        with explorer.db:
            cur = explorer.db.execute(
                """SELECT buttons FROM sessions
                WHERE requested = TRUE AND screen IS NULL
                LIMIT 20"""
            )
            buttons = cur.fetchall()
        if not buttons:
            yield None
        yield from buttons


# @strategy
def random_after_requested(explorer):
    while True:
        with explorer.db:
            cur = explorer.db.execute(
                """SELECT buttons FROM sessions
                WHERE requested = TRUE
                ORDER BY RANDOM()
                LIMIT 1"""
            )
            (buttons,) = cur.fetchone()
        for __ in range(10):
            tail = "".join(random.choices(BUTTONS, k=5))
            yield buttons + tail


if __name__ == "__main__":
    ex = Explorer()
    for __ in range(10):
        ex.explore()
    for line in ex.db.iterdump():
        print(line)
