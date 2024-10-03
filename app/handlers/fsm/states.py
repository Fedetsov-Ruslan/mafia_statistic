from aiogram.fsm.state import State, StatesGroup


class ActionSelection(StatesGroup):
    choice_action = State()
    users = State()
    club = State()
    games = State()
    statistics_date = State()
    viewing_user = State()
    get_all_in_club = State()
    type_game = State()
    add_game_or_show_game = State()
    

class AddGame(StatesGroup):
    add_players_in_game = State()
    add_role = State()
    add_fol = State()
    add_point = State()
    add_first_dead = State()
    add_best_step = State()
    winner = State()
    date_game = State()
    review = State()


class AddUser(StatesGroup):
    nickname = State()
    gender = State()
    club = State()
    confirmation = State()
    add_complite = State()