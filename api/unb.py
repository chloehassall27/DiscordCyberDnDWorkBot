import json
import os

import requests
from dotenv import load_dotenv
from hikari import Member

load_dotenv()
UNB_TOKEN = os.getenv('UNB_API_TOKEN')


def getMoney(member: Member):
    url = 'https://unbelievaboat.com/api/v1/guilds/' + str(member.guild_id) + '/users/' + str(member.id)
    header = {'Authorization': UNB_TOKEN}
    r = requests.get(url=url, headers=header)
    return r.json()["cash"]


def updateMoney(player: Member, amount, reason="CyberDnDWorkBot"):
    url = 'https://unbelievaboat.com/api/v1/guilds/' + str(player.guild_id) + '/users/' + str(player.id)
    header = {'Authorization': UNB_TOKEN, 'Accept': 'application/json'}
    data = json.dumps({'bank': str(amount), 'reason': reason}, indent = 4)
    r = requests.patch(url=url, data=data, headers=header)
    return r