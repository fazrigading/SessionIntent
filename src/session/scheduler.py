"""
SessionIntent Time Scheduler
Provides time-based automatic mode switching.
"""

from __future__ import annotations

import time
from typing import Any
from datetime import datetime, time as dt_time, timedelta

from ..session.log import info, warning


class TimeSchedule:
    """Schedule for time-based mode switching."""

    def __init__(
        self,
        mode: str,
        start_time: dt_time,
        end_time: dt_time,
        days: list[int] | None = None,
    ) -> None:
        self.mode = mode
        self.start_time = start_time
        self.end_time = end_time
        self.days = days or [0, 1, 2, 3, 4, 5, 6]

    def is_active(self, check_time: datetime | None = None) -> bool:
        """Check if schedule is currently active."""
        now = check_time or datetime.now()
        current_time = now.time()
        current_day = now.weekday()

        if current_day not in self.days:
            return False

        if self.start_time <= self.end_time:
            return self.start_time <= current_time <= self.end_time
        else:
            return current_time >= self.start_time or current_time <= self.end_time


def get_active_schedule(
    config: dict[str, Any],
    check_time: datetime | None = None,
) -> str | None:
    """Get the active mode based on time schedules."""
    schedules = config.get("time_schedules", {})

    if not schedules:
        return None

    for mode_name, schedule_data in schedules.items():
        try:
            start = dt_time.fromisoformat(schedule_data["start"])
            end = dt_time.fromisoformat(schedule_data["end"])
            days = schedule_data.get("days", [0, 1, 2, 3, 4, 5, 6])

            schedule = TimeSchedule(mode_name, start, end, days)
            if schedule.is_active(check_time):
                return mode_name
        except (KeyError, ValueError) as e:
            warning(f"Invalid schedule for {mode_name}: {e}")

    return None


def get_next_schedule_change(
    config: dict[str, Any],
    after_mode: str | None = None,
) -> tuple[str, datetime] | None:
    """Get the next scheduled mode change."""
    schedules = config.get("time_schedules", {})

    if not schedules:
        return None

    now = datetime.now()
    active_schedule: TimeSchedule | None = None
    next_change: datetime | None = None
    next_mode: str | None = None

    for mode_name, schedule_data in schedules.items():
        try:
            start = dt_time.fromisoformat(schedule_data["start"])
            end = dt_time.fromisoformat(schedule_data["end"])
            days = schedule_data.get("days", [0, 1, 2, 3, 4, 5, 6])

            schedule = TimeSchedule(mode_name, start, end, days)

            if schedule.is_active(now):
                active_schedule = schedule
                continue

            for day_offset in range(1, 8):
                check_date = now.date() + timedelta(days=day_offset)
                candidate = datetime.combine(check_date, start)

                if candidate > now:
                    if next_change is None or candidate < next_change:
                        next_change = candidate
                        next_mode = mode_name
        except (KeyError, ValueError):
            continue

    if active_schedule and next_mode and next_change:
        return (next_mode, next_change)

    return None


class TimeScheduler:
    """Background scheduler for time-based mode switching."""

    def __init__(
        self,
        check_interval: float = 60.0,
    ) -> None:
        self._check_interval = check_interval
        self._running = False
        self._thread: Any = None
        self._current_mode: str | None = None

    def start(
        self,
        session_manager: Any,
    ) -> None:
        """Start the scheduler."""
        self._running = True
        self._session_manager = session_manager

        import threading

        self._thread = threading.Thread(target=self._run_loop, daemon=True)
        self._thread.start()
        info("Time scheduler started")

    def stop(self) -> None:
        """Stop the scheduler."""
        self._running = False
        if self._thread:
            self._thread.join()
        info("Time scheduler stopped")

    def _run_loop(self) -> None:
        """Main scheduler loop."""
        while self._running:
            time.sleep(self._check_interval)

            if not self._running:
                break

            try:
                new_mode = get_active_schedule(self._session_manager.config)

                if new_mode and new_mode != self._current_mode:
                    info(f"Auto-switching to mode: {new_mode}")
                    self._session_manager.apply_mode(new_mode)
                    self._current_mode = new_mode
            except Exception as e:
                warning(f"Scheduler error: {e}")


__all__ = [
    "TimeSchedule",
    "TimeScheduler",
    "get_active_schedule",
    "get_next_schedule_change",
]