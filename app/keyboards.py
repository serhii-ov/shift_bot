import calendar
from aiogram.types import (
    ReplyKeyboardMarkup, 
    KeyboardButton, 
    InlineKeyboardMarkup, 
    InlineKeyboardButton,
    )
from constants import (
    MONTHS, SHIFT_NAMES, ACTION_BUTTONS, WEEK_DAYS,
    )


shift_kb = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text=SHIFT_NAMES[0])],
        [KeyboardButton(text=SHIFT_NAMES[1])],
        [KeyboardButton(text=SHIFT_NAMES[2])],
        [KeyboardButton(text=SHIFT_NAMES[3])],
    ],
    resize_keyboard=True,
)

action_kb = InlineKeyboardMarkup(
    inline_keyboard=[
        [
            InlineKeyboardButton(text=ACTION_BUTTONS[0], callback_data="pick_date"),
            InlineKeyboardButton(text=ACTION_BUTTONS[1], callback_data="pick_week"),
            InlineKeyboardButton(text=ACTION_BUTTONS[2], callback_data="pick_month"),
        ]
    ]
)


def build_calendar(year: int, month: int, mode: str = "date"):
    keyboard = []

    keyboard.append([
        InlineKeyboardButton(text="«", callback_data=f"nav:prev:{year}:{month}:{mode}"),
        InlineKeyboardButton(text=f"{month}.{year}", callback_data="ignore"),
        InlineKeyboardButton(text="»", callback_data=f"nav:next:{year}:{month}:{mode}")
    ])

    keyboard.append(
        [InlineKeyboardButton(text=d, callback_data="ignore") for d in WEEK_DAYS]
    )

    cal = calendar.monthcalendar(year, month)

    for week in cal:
        row = []
        for day in week:
            if day == 0:
                row.append(InlineKeyboardButton(text=" ", callback_data="ignore"))
            else:
                row.append(
                    InlineKeyboardButton(
                        text=str(day),
                        callback_data=f"{mode}:{year}:{month}:{day}"
                    )
                )
        keyboard.append(row)

    return InlineKeyboardMarkup(inline_keyboard=keyboard)


def build_month_selector(year: int):
    months = list(MONTHS.values())

    keyboard = []
    row = []

    for i, name in enumerate(months, start=1):
        row.append(
            InlineKeyboardButton(
                text=name,
                callback_data=f"month:{year}:{i}"
            )
        )
        if len(row) == 3:
            keyboard.append(row)
            row = []

    return InlineKeyboardMarkup(inline_keyboard=keyboard)
