


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
        elif player_in_game['role'] == 'Мирные':
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
    return statistic