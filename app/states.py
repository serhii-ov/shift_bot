from aiogram.fsm.state import State, StatesGroup


class ScheduleFSM(StatesGroup):
    choosing_shift = State()
    choosing_action = State()
    picking_date = State()
    picking_week = State()
    picking_month = State()
