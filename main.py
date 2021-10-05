# This is a sample Python script.

# Press Shift+F10 to execute it or replace it with your code.
# Press Double Shift to search everywhere for classes, files, tool windows, actions, and settings.
try:
    import ujson as json
except ImportError:
    import json

from Integrations import SteamAPIIntegration

config = json.load(open("config.json"))

# Press the green button in the gutter to run the script.
if __name__ == '__main__':
    print('Service Staring')

    steamApi = SteamAPIIntegration.SteamApi()
    friends = steamApi.getFriends(config['SteamUserKey'])
    for friend in friends.get('players'):
        ownedGames = steamApi.getOwnedGames(friend.get('steamid'))
        if ownedGames is None:
            continue
        ownedGames[0]['playerName'] = friend.get('personaname')
        games = list(ownedGames)
        print(json.dumps(games))

# See PyCharm help at https://www.jetbrains.com/help/pycharm/
