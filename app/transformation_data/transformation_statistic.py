import csv
import pandas as pd
from aiogram.types.input_file import FSInputFile

def write_csv(statistic: dict):
    with open('statistic.csv', mode='w', newline='', encoding='utf-8-sig') as file:
        writer = csv.writer(file)
        writer.writerow(['Игрок', 'Баллы',
                         'Количество игр', 'Процент побед',
                         'Мафией', 'Мирным', 'Доном',
                         'Шерифом', 'Фолы за игру',
                         'Первый убиенный'])
        for key, value in statistic.items():
                reting = round(value['reting'], 2)
                count_games = value['count_games']
                winrate = round(value['winrate'], 2)
                mafia_winrate = round(value['mafia_winrate'], 2)
                civilian_winrate = round(value['civilian_winrate'], 2)
                don_winrate = round(value['don_winrate'], 2)
                sheriff_winrate = round(value['sheriff_winrate'], 2)
                fols_on_the_game = round(value['fols_on_the_game'] / value['count_games'], 2)
                first_dead = round(value['first_dead'] / value['count_games'] *100, 2)
                
                writer.writerow([
                key, reting, count_games, winrate, mafia_winrate, 
                civilian_winrate, don_winrate, sheriff_winrate, 
                fols_on_the_game, first_dead
            ])
    df = pd.read_csv('statistic.csv', encoding='utf-8-sig')
    df.to_excel('statistic.xlsx', index=False, engine='openpyxl')
    document = FSInputFile('statistic.xlsx')             
    return document
    

async def transformation_statistic(data: list[dict]):
    statistic = {}
    for player_in_game in data:
        if player_in_game['nickname'] not in statistic:
            statistic[player_in_game['nickname']] = {
                'reting' : 0,
                'count_games' : 0,
                'first_dead' : 0,
                'fols_on_the_game' : 0,
                'mafia_games' : 0,
                'sheriff_games' : 0,
                'don_games' : 0,
                'civilian_games' : 0,
                'mafia_win' : 0,
                'sheriff_win' : 0,
                'don_win' : 0,
                'civilian_win' : 0,
                'mafia_winrate' : 0,
                'sheriff_winrate' : 0,
                'don_winrate' : 0,
                'civilian_winrate' : 0,
                'winrate' : 0
            }
        if player_in_game['role'] == 'Дон' and player_in_game['winner'] == 'Мафия':
            statistic[player_in_game['nickname']]['don_games'] += 1
            statistic[player_in_game['nickname']]['don_win'] += 1
        elif player_in_game['role'] == 'Дон':
            statistic[player_in_game['nickname']]['don_games'] += 1
        if player_in_game['role'] == 'Шериф' and player_in_game['winner'] == 'Мирные':
            statistic[player_in_game['nickname']]['sheriff_games'] += 1
            statistic[player_in_game['nickname']]['sheriff_win'] += 1
        elif player_in_game['role'] == 'Шериф':
            statistic[player_in_game['nickname']]['sheriff_games'] += 1
        if player_in_game['role'] == 'Мафия' and player_in_game['winner'] == 'Мафия':
            statistic[player_in_game['nickname']]['mafia_games'] += 1
            statistic[player_in_game['nickname']]['mafia_win'] += 1
        elif player_in_game['role'] == 'Мафия':
            statistic[player_in_game['nickname']]['mafia_games'] += 1
        if player_in_game['role'] == 'Мирный' and player_in_game['winner'] == 'Мирные':
            statistic[player_in_game['nickname']]['civilian_games'] += 1
            statistic[player_in_game['nickname']]['civilian_win'] += 1
        elif player_in_game['role'] == 'Мирный':
            statistic[player_in_game['nickname']]['civilian_games'] += 1
        statistic[player_in_game['nickname']]['count_games'] += 1
        
        statistic[player_in_game['nickname']]['reting'] += player_in_game['points'] + player_in_game['dop_points']
        
        if str(player_in_game['seat_number']) == player_in_game['first_dead']:
            statistic[player_in_game['nickname']]['first_dead'] += 1  
        statistic[player_in_game['nickname']]['fols_on_the_game'] += player_in_game['fols']
        
    for key, player_in_game in statistic.items():
        if player_in_game['mafia_games'] != 0:
            player_in_game['mafia_winrate'] = player_in_game['mafia_win'] / player_in_game['mafia_games'] * 100
        if player_in_game['sheriff_games'] != 0:
            player_in_game['sheriff_winrate'] = player_in_game['sheriff_win'] / player_in_game['sheriff_games'] * 100
        if player_in_game['don_games'] != 0:
            player_in_game['don_winrate'] = player_in_game['don_win'] / player_in_game['don_games'] * 100
        if player_in_game['civilian_games'] != 0:
            player_in_game['civilian_winrate'] = player_in_game['civilian_win'] / player_in_game['civilian_games'] * 100
        player_in_game['winrate'] = (player_in_game['mafia_win'] + 
                                                            player_in_game['sheriff_win'] + 
                                                            player_in_game['don_win'] +
                                                            player_in_game['civilian_win'])/ player_in_game['count_games'] * 100    
    document = write_csv(statistic)
    return document