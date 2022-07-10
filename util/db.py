import hikari
import lightbulb

from multipledispatch import dispatch
# from app import bot

bot: lightbulb.BotApp


def findPlayerEntry(member: hikari.Member):
    return bot.d.players.find_one({"user_id": member.id})


@dispatch(hikari.Member)
def updatePlayerEntry(member: hikari.Member):
    return updatePlayerEntry(member, {})


@dispatch(hikari.Member, str, object)
def updatePlayerEntry(member: hikari.Member, key: str, value: object):
    return updatePlayerEntry(member, {key: value})


@dispatch(hikari.Member, dict)
def updatePlayerEntry(member: hikari.Member, elements: dict):
    bot.d.players.update_one({"user_id": member.id}, {
        "$set": {"user_id": member.id, "username": member.username, "display_name": member.display_name} | elements},
                             upsert=True)
    return bot.d.players.find_one({"user_id": member.id})


def initDbHelper(bot_: lightbulb.BotApp):
    global bot
    bot = bot_
