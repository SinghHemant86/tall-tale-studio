"""Publishing calendar: long videos on fixed weekdays, one Short a day in between.

Slots already taken are remembered in done/schedule.json (committed by the daily run), so two
stories never get the same slot.
"""
import json
from datetime import datetime, timedelta
from zoneinfo import ZoneInfo

from .common import ROOT

STATE = ROOT / "done" / "schedule.json"
DAYS = {"mon": 0, "tue": 1, "wed": 2, "thu": 3, "fri": 4, "sat": 5, "sun": 6}


def _load() -> dict:
    try:
        return json.loads(STATE.read_text())
    except (OSError, ValueError):
        return {"long": [], "short": []}


def _save(state: dict) -> None:
    STATE.parent.mkdir(exist_ok=True)
    STATE.write_text(json.dumps(state, indent=1))


def _at(day: datetime, hhmm: str) -> datetime:
    h, m = (int(x) for x in hhmm.split(":"))
    return day.replace(hour=h, minute=m, second=0, microsecond=0)


def plan(scfg: dict, n_shorts: int, now: datetime | None = None) -> tuple[datetime, list[datetime]]:
    """Next free long-video slot, then the next n free daily Short slots after it (local time)."""
    tz = ZoneInfo(scfg.get("timezone", "Asia/Kolkata"))
    now = (now or datetime.now(tz)).astimezone(tz)
    state = _load()
    taken_long = set(state["long"])
    taken_short = set(state["short"])
    lead = timedelta(hours=scfg.get("min_lead_hours", 6))

    long_days = [DAYS[d.lower()[:3]] for d in scfg.get("long_days", ["mon", "fri"])]
    day = now
    while True:
        slot = _at(day, scfg.get("long_time", "20:00"))
        if day.weekday() in long_days and slot >= now + lead and slot.isoformat() not in taken_long:
            break
        day += timedelta(days=1)
    long_slot = slot

    shorts, day = [], long_slot + timedelta(days=1)
    while len(shorts) < n_shorts:
        s = _at(day, scfg.get("short_time", "19:30"))
        if s.isoformat() not in taken_short:
            shorts.append(s)
        day += timedelta(days=1)
    return long_slot, shorts


def commit(long_slot: datetime | None, short_slots: list[datetime]) -> None:
    state = _load()
    if long_slot:
        state["long"].append(long_slot.isoformat())
    state["short"] += [s.isoformat() for s in short_slots]
    # keep the file small: forget slots older than 60 days
    cutoff = (datetime.now(ZoneInfo("UTC")) - timedelta(days=60)).isoformat()
    for k in state:
        state[k] = sorted(x for x in set(state[k]) if datetime.fromisoformat(x).astimezone(ZoneInfo("UTC")).isoformat() > cutoff)
    _save(state)


def rfc3339_utc(dt: datetime) -> str:
    return dt.astimezone(ZoneInfo("UTC")).strftime("%Y-%m-%dT%H:%M:%SZ")
