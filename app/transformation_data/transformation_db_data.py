import datetime

from app.database.models import Games
from tabulate import tabulate
from PIL import Image, ImageDraw, ImageFont


async def transformation_db_data(games:list[dict], bs_list:list[dict]):
    all_games_list = []
    for game in games:
        data_game = []
        date_and_number = 'Дата' +f'{game[0]['date_game'].strftime('%Y-%m-%d')};'.rjust(20) + f'Номер {game[0]['id']}'.rjust(20)
        header = '№'.rjust(2) + ' ____Игровой ник____'.rjust(16) + '__роль__'.rjust(6)+ ' _фолы_'.rjust(5) + '_Баллы_'.rjust(5) + '_Доп. баллы_'
        data_game.append(date_and_number)
        data_game.append(header)

        for i in range(10):
            row = f'{i+1}'.ljust(4) + f'{game[i]['nickname'][:10]}'.ljust(20, '_') + f'{game[i]['role']}'.rjust(10) + f'  {game[i]['fols']}  '.rjust(6) + f'  {game[i]['points']}  '.rjust(6) + f'  {game[i]['dop_points']}  '.rjust(6)
            data_game.append(row)
        winner = f'Победившая команда: {game[i]['winner']}'
        data_game.append(winner)
        if game[i]['first_dead'] != '':
            bs = bs_list.pop(0)
            footer = 'ПУ'.rjust(4) + f'  {game[i]['first_dead'][:10]}'.rjust(12) + 'ЛХ'.rjust(6) + f'{bs[0]['nickname']}'.rjust(16)
            data_game.append(footer)
            footer = '                               ' + f'{bs[1]['nickname']}'.rjust(16)
            data_game.append(footer)
            footer = '                               ' + f'{bs[2]['nickname']}'.rjust(16)
            data_game.append(footer)
        else:
            footer = '   '
            data_game.append(footer)
        all_games_list.append(data_game)
    return all_games_list
    