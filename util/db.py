from decimal import Decimal

import hikari
import lightbulb
from bson import Decimal128
from multipledispatch import dispatch

from plugins.schedules import isAI

bot: lightbulb.BotApp

defaultFPIncrement = Decimal(".1")
defaultTPIncrement = Decimal(".125")
defaultHumanCOL = 75
defaultAICOL = 100


def isPlayer(member: hikari.Member) -> bool:
    return any(role for role in member.get_roles() if role.name == "Players")

# def getPlayerEntry(member: hikari.Member):
#     return bot.d.players.find_one({"user_id": member.id})


@dispatch(hikari.Member)
def updatePlayerEntry(member: hikari.Member):
    return updatePlayerEntry(member, {}, {})


@dispatch(hikari.Member, str, object)
def updatePlayerEntry(member: hikari.Member, key: str, value: object):
    return updatePlayerEntry(member, {key: value}, {})


@dispatch(hikari.Member, dict)
def updatePlayerEntry(member: hikari.Member, set_elements: dict):
    updatePlayerEntry(member, set_elements, {})


@dispatch(hikari.Member, dict, dict)
def updatePlayerEntry(member: hikari.Member, set_elements: dict, inc_elements: dict):
    bot.d.players.update_one({"user_id": member.id}, {
        "$set": {
            "user_id": member.id,
            "username": member.username,
            "display_name": member.display_name,
        } | set_elements,
        "$setOnInsert": {
            "tech.increment": Decimal128(defaultTPIncrement),
            "feat.increment": Decimal128(defaultFPIncrement),
            "col": defaultAICOL if (isAI(member)) else defaultHumanCOL
            },
        "$inc": inc_elements
        },
        upsert=True)

    # if not bot.d.players.find_one({"user_id": member.id}).get('tech', {}).get('currentIncrement'):
    #     bot.d.players.update_one({"user_id": member.id}, {"$set": {'tech.currentIncrement': defaultTPIncrement}})
    # if not bot.d.players.find_one({"user_id": member.id}).get('features', {}).get('currentIncrement'):
    #     bot.d.players.update_one({"user_id": member.id}, {"$set": {'features.currentIncrement': defaultFPIncrement}})

    return bot.d.players.find_one({"user_id": member.id})


@dispatch(hikari.Guild)
def updateAllPlayerEntries(guild: hikari.Guild):
    return updateAllPlayerEntries(guild)


@dispatch(str, object)
def updateAllPlayerEntries(guild: hikari.Guild, key: str, value: object):
    return updateAllPlayerEntries(guild, {key: value})


@dispatch(dict)
def updateAllPlayerEntries(guild: hikari.Guild, elements: dict):
    members = guild.get_members().values()
    for member in members:
        if isPlayer(member):
            updatePlayerEntry(member, elements)

# @dispatch(hikari.Member, str, object)
# def incrementPlayerEntry(member: hikari.Member, key: str, value: object):
#     return incrementPlayerEntry(member, {key: value})
#
#
# @dispatch(hikari.Member, dict)
# def incrementPlayerEntry(member: hikari.Member, elements: dict):
#     bot.d.players.update_one({"user_id": member.id}, {
#         "$inc": elements}, upsert=True)
#
#     return bot.d.players.find_one({"user_id": member.id})


def initDbHelper(bot_: lightbulb.BotApp):
    global bot
    bot = bot_
