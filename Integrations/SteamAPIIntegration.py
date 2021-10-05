import os

import requests

try:
    import ujson as json
except ImportError:
    import json


class SteamApi:
    config = json.load(open(os.path.dirname(__file__) + '/../config.json'))
    appList = None
    base_api_url = f"https://api.steampowered.com/{{interface}}/{{methodName}}/v{{version}}/?key={config['SteamApiKey']}&format=json"
    store_api_url = f"https://store.steampowered.com/api/appdetails?appids={{appId}}"
    cachedJson = None
    cache = dict()

    @classmethod
    def getApiUrl(cls, interface, methodName, version):
        return cls.base_api_url.replace("{interface}", interface).replace("{methodName}", methodName).replace(
            "{version}",
            version)

    @classmethod
    def getStoreApiUrl(cls, appId):
        return cls.store_api_url.replace("{appId}", appId)

    @classmethod
    def getFriends(cls, steamId):
        friendsList = requests.get(
            f"{cls.getApiUrl('ISteamUser', 'GetFriendList', '0001')}&steamid={steamId}&relationship=friend")
        friendsList.encoding = "utf-8-sig"
        friendsList = friendsList.json().get('friendslist').get('friends')
        friendIds = ""
        for friend in friendsList:
            currentIndex = friendsList.index(friend)
            friendIds += f"{friend.get('steamid')}{cls.getComma(currentIndex, len(friendsList))}"

        return cls.getPlayerSummaries(friendIds)

    @classmethod
    def getPlayerSummaries(cls, steamIds):
        playerSummaries = requests.get(f"{cls.getApiUrl('ISteamUser', 'GetPlayerSummaries', '2')}&steamids={steamIds}")
        playerSummaries.encoding = "utf-8-sig"
        return playerSummaries.json().get('response')

    @classmethod
    def getOwnedGames(cls, steamId):
        games = requests.get(f"{cls.getApiUrl('IPlayerService', 'GetOwnedGames', '1')}&steamid={steamId}")
        games.encoding = "utf-8-sig"
        if games.status_code != 200 or not games.headers["Content-Type"].strip().startswith("application/json"):
            return

        ownedGames = games.json().get('response')

        if ownedGames is None:
            return

        ownedGames = ownedGames.get('games')
        if ownedGames is None:
            return

        for game in ownedGames:
            details = cls.getGameDetails(game.get('appid'))
            if details is not None:
                game['gamename'] = details.get('name')
                game['is_free'] = details.get('is_free')
                priceOverview = details.get('price_overview')
                if priceOverview is not None:
                    game['price'] = priceOverview.get('final_formatted')

                game['description'] = details.get('detailed_description')
                game['short_description'] = details.get('short_description')
                game['main_image'] = details.get('header_image')
                game['images'] = details.get('screenshots')
                game['genres'] = details.get('genres')
                game['trailer'] = details.get('movies')
                game['background_image'] = details.get('background')
                game['categories'] = details.get('categories')

        return ownedGames

    @classmethod
    def findGameByAppId(cls, appId):
        if cls.appList is None:
            cls.appList = cls.getAppList()
        return next((app for app in cls.appList.apps if app.appid == appId), None)

    @classmethod
    def getGameDetails(cls, appId):
        if appId not in cls.cache:

            gameDetails = requests.get(f"{cls.getStoreApiUrl(str(appId))}")
            gameDetails.encoding = "utf-8-sig"
            if gameDetails.status_code != 200 or not gameDetails.headers['Content-Type'].strip().startswith('application/json'):
                return
            gameDetails = gameDetails.json()
            if gameDetails is None:
                return
            cls.cache[appId] = gameDetails[str(appId)]

        return cls.cache[appId].get('data')

    @classmethod
    def getAppList(cls):
        if cls.cachedJson is None:
            appList = requests.get(f"{cls.getApiUrl('ISteamApps', 'GetAppList', '2')}")
            appList.encoding = "utf-8-sig"
            cls.cachedJson = appList.text
        return cls.cachedJson.json().get('applist')

    @classmethod
    def getComma(cls, index, length):
        if index != length - 1:
            return ","
        else:
            return ""
