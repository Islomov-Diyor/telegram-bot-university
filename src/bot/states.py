from aiogram.fsm.state import State, StatesGroup


class StudentRegistrationState(StatesGroup):
    """FSM states for student registration workflow."""
    waiting_for_full_name = State()
    waiting_for_course = State()
    waiting_for_phone = State()
    waiting_for_confirmation = State()
