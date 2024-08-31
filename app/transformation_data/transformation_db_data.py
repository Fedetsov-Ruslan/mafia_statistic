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
    
async def tr(game:Games):

    data_game = []
    data_and_number = ['Дата', game.date_game, '', 'Номер', game.id, '']
    header = ['No', 'Игровой ник', 'роль', 'фолы', 'Баллы', 'Доп. баллы']
    data_game.append(data_and_number)
    data_game.append(header)
    for i in range(10):
        row = [i+1, game.gamers[i], game.roles[i], game.fols[i], game.points[i], game.dop_points[i]]
        data_game.append(row)
    winner = ['Победившая команда', '','', game.winner,'','']
    data_game.append(winner)
    if game.first_dead != '':
        footer = ['ПУ', game.first_dead, '', game.gamers.index(game.best_step[0]), game.gamers.index(game.best_step[1]), game.gamers.index(game.best_step[2])]
    else:
        footer = ['','', '', '', '', '']
    data_game.append(footer)
    image = transformation_in_image(data_game)
    return image

def transformation_in_image(data_game):
    rows = 14
    cols = 6
    cell_width = 40
    cell_height = 20

    # Размеры изображения
    width = cols * cell_width
    height = rows * cell_height

    # Создаем белый фон
    img = Image.new('L', (width, height), color= 255)
    draw = ImageDraw.Draw(img)

    # Рисуем сетку таблицы
    for i in range(rows + 1):
        draw.line([(0, i * cell_height), (width, i * cell_height)], fill='black', width=2)

    for i in range(cols + 1):
        draw.line([(i * cell_width, 0), (i * cell_width, height)], fill='black', width=2)

    # Используем системный шрифт, если PIL не находит TTF шрифт.
    try:
        font = ImageFont.truetype("arial.ttf", 18)
    except IOError:
        font = ImageFont.load_default()
     # Добавление текста в ячейки
    for i in range(rows):
        for j in range(cols):
            text = data_game[i * cols + j] if i * cols + j < len(data_game) else ''
            
            # Получение размеров текста
            bbox = draw.textbbox((0, 0), text, font=font)
            text_width, text_height = bbox[2] - bbox[0], bbox[3] - bbox[1]
            text_x = j * cell_width + (cell_width - text_width) // 2
            text_y = i * cell_height + (cell_height - text_height) // 2
            draw.text((text_x, text_y), text, fill="black", font=font)

    return img
    # # Сохранение изображения
    # img.save("table_image.png")
    # img.show()