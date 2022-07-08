import json
import os

import requests
from dotenv import load_dotenv
from hikari import Snowflake

load_dotenv()
UNB_TOKEN = os.getenv('UNB_API_TOKEN')


def getMoney(player_id: Snowflake, guild_id: Snowflake):
    url = 'https://unbelievaboat.com/api/v1/guilds/' + str(guild_id) + '/users/' + str(player_id)
    header = {'Authorization': UNB_TOKEN}
    r = requests.get(url=url, headers=header)
    return r.json()["cash"]


def updateMoney(guild, player, amount):
    url = 'https://unbelievaboat.com/api/v1/guilds/' + guild + '/users/' + str(player.id)
    header = {'Authorization': UNB_TOKEN, 'Accept': 'application/json'}
    data = json.dumps({'cash': amount, 'reason': 'Stonks'}, indent = 4)
    r = requests.patch(url=url, data=data, headers=header)
    return r