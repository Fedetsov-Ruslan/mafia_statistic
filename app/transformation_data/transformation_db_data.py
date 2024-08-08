
from app.database.models import Games
from tabulate import tabulate


async def transformation_db_data(game:Games):

    data_game = []
    date_and_number = 'Дата' +f'{game.date_game};'.rjust(20) + f'Номер {game.id}'.rjust(20)
    header = '№'.rjust(4) + ' Игровой ник'.rjust(12) + '  роль'.rjust(8)+ 'фолы'.rjust(6) + 'Баллы '.rjust(7) + 'Доп. баллы'
    data_game.append(date_and_number)
    data_game.append(header)

    for i in range(10):
        row = f'{i+1}'.ljust(4) + f'{game.gamers[i][:10]}'.ljust(20, '-') + f'{game.roles[i]}'.rjust(10) + f'{game.fols[i]}'.rjust(6) + f'{game.points[i]}'.rjust(6) + f'{game.dop_points[i]}'.rjust(6)
        data_game.append(row)
    winner = f'Победившая команда: {game.winner}'
    data_game.append(winner)
    if game.first_dead != '':
        footer = 'ПУ'.rjust(4) + f'  {game.first_dead[:10]}'.rjust(12) + 'ЛХ'.rjust(6) + f'{game.gamers.index(game.best_step[0])}'.rjust(6) +f'{game.gamers.index(game.best_step[1])}'.rjust(6)+f'{game.gamers.index(game.best_step[2])}'.rjust(6)
    else:
        footer = '   '
    data_game.append(footer)
    # table = tabulate(data_game, headers='secondrow', tablefmt='grid')
    return data_game
    

