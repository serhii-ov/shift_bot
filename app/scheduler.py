from datetime import date, timedelta, datetime
import calendar
from typing import Union, List

from constants import (
    CYCLE, 
    WEEK_DAYS, 
    INIT_DATE_FOR_SHIFT, 
    WEEK_LENGTH, 
    MONTHS,
    )


class ShiftSchedule:

    def __init__(self, shift: str):
        if shift not in INIT_DATE_FOR_SHIFT:
            raise ValueError(
                f"Unknown shift '{shift}'. "
                f"Available: {', '.join(INIT_DATE_FOR_SHIFT.keys())}"
            )

        self.shift = shift

    @staticmethod
    def _parse_date(day: Union[str, date]) -> date:
        if isinstance(day, str):
            return datetime.strptime(day, "%Y-%m-%d").date()
        return day

    @property
    def init_date(self):
        try:
            return INIT_DATE_FOR_SHIFT[self.shift]
        except KeyError:
            raise ValueError("Invalid shift configuration")


    def get_day_type(self, day: Union[str, date]) -> str:
        day_ = self._parse_date(day)
        delta = abs(day_ - self.init_date).days
        return CYCLE[delta % len(CYCLE)]

    def date_presentation(self, day: date) -> str:
        return (
            f"{day.strftime('%d.%m.%Y')}: "
            f"{WEEK_DAYS[day.weekday()]} - "
            f"{self.get_day_type(day)}"
        )

    def get_days_type_for_week(self, day: Union[str, date]) -> List[str]:
        day_ = self._parse_date(day)
        return [
            self.date_presentation(day_ + timedelta(days=i))
            for i in range(WEEK_LENGTH)
        ]

    def get_schedule_for_month(
        self,
        month: Union[str, int],
        year: int,
    ) -> List[str]:

        if isinstance(month, str):
            normalized = month.strip().lower()
            month_ = MONTHS.get(normalized)

            if not month_:
                raise ValueError("Невірна назва місяця")

        if not isinstance(month, int):
            raise ValueError("Month must be int or valid month name")

        if not 1 <= month <= 12:
            raise ValueError("Month must be between 1 and 12")

        _, days_in_month = calendar.monthrange(year, month)

        return [
            self.date_presentation(date(year, month, day))
            for day in range(1, days_in_month + 1)
        ]
