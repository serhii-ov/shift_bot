from datetime import date, timedelta

from aiogram import Router, F
from aiogram.filters import Command
from aiogram.types import CallbackQuery, Message
from aiogram.fsm.context import FSMContext

from keyboards import (
    shift_kb, action_kb, build_calendar, build_month_selector,
    )
from states import ScheduleFSM 
from scheduler import ShiftSchedule

router = Router()


async def show_action_menu(
        callback: CallbackQuery | None, 
        message: Message,
        state: FSMContext
        ):
    await state.set_state(ScheduleFSM.choosing_action)
    await message.answer(
        "Оберіть опцію:",
        reply_markup=action_kb
        )
    
    if callback:
        await callback.answer()


@router.message(Command("start"))
async def start(message: Message, state: FSMContext):
    # await state.clear()
    await state.set_state(ScheduleFSM.choosing_shift)
    await message.answer("Оберіть зміну:", reply_markup=shift_kb)


@router.message(ScheduleFSM.choosing_shift)
async def shift_chosen(message: Message, state: FSMContext):
    shift = message.text

    await state.update_data(shift=shift)
    await state.set_state(ScheduleFSM.choosing_action)

    await message.answer("Що показати?", reply_markup=None)
    await message.answer("Оберіть опцію:", reply_markup=action_kb)


@router.callback_query(F.data == "change_shift")
async def change_shift(callback: CallbackQuery, state: FSMContext):
    await state.set_state(ScheduleFSM.choosing_shift)

    await callback.message.answer(
        "Оберіть нову зміну:",
        reply_markup=shift_kb
    )

    await callback.answer()


@router.callback_query(
        F.data.startswith("pick_"), 
        ScheduleFSM.choosing_action,
        )
async def action_handler(
    callback: CallbackQuery, 
    state: FSMContext
    ):
    today = date.today() 

    if callback.data == "pick_date":
        await state.set_state(ScheduleFSM.picking_date)

        await callback.message.answer(
            "Оберіть дату:",
            reply_markup=build_calendar(today.year, today.month, mode="date"),
        )

    elif callback.data == "pick_week":
        await state.set_state(ScheduleFSM.picking_week)

        await callback.message.answer(
            "Оберіть день тижня:",
            reply_markup=build_calendar(today.year, today.month, mode="week"),
        )

    elif callback.data == "pick_month":
        await state.set_state(ScheduleFSM.picking_month)

        await callback.message.answer(
            "Оберіть місяць:",
            reply_markup=build_month_selector(today.year),
    )
    await callback.answer()


@router.callback_query(F.data.startswith("nav:"))
async def navigate_calendar(callback: CallbackQuery):
    _, direction, year, month, mode = callback.data.split(":")
    year, month = int(year), int(month)

    if direction == "prev":
        month -= 1
        if month == 0:
            month = 12
            year -= 1
    else:
        month += 1
        if month == 13:
            month = 1
            year += 1

    await callback.message.edit_reply_markup(
        reply_markup=build_calendar(year, month, mode)
    )
    await callback.answer()


@router.callback_query(F.data.startswith("date:"))
async def handle_date(callback: CallbackQuery, state: FSMContext):
    _, y, m, d = callback.data.split(":")
    selected = date(int(y), int(m), int(d))

    data = await state.get_data()
    schedule = ShiftSchedule(data["shift"])

    await callback.message.answer(schedule.shift.capitalize() + " - " +
        schedule.date_presentation(selected)
    )

    await show_action_menu(callback, callback.message, state)

    await callback.answer()


@router.callback_query(F.data.startswith("week:"))
async def handle_week(callback: CallbackQuery, state: FSMContext):
    _, y, m, d = callback.data.split(":")
    selected = date(int(y), int(m), int(d))

    monday = selected - timedelta(days=selected.weekday())

    data = await state.get_data()
    schedule = ShiftSchedule(data["shift"])

    result = "\n".join(
        [schedule.shift.capitalize()] + schedule.get_days_type_for_week(monday)
    )

    await callback.message.answer(result)

    await show_action_menu(callback, callback.message, state)

    await callback.answer()


@router.callback_query(F.data.startswith("month:"))
async def handle_month(callback: CallbackQuery, state: FSMContext):
    _, y, m = callback.data.split(":")
    year, month = int(y), int(m)

    data = await state.get_data()
    schedule = ShiftSchedule(data["shift"])

    result = "\n".join(
        [schedule.shift.capitalize()] + schedule.get_schedule_for_month(month, year)
        
    )

    await callback.message.answer(result)

    await show_action_menu(callback, callback.message, state)
    
    await callback.answer()