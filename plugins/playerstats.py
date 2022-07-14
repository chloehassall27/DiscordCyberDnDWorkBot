import hikari
import lightbulb
from bson import Decimal128

from api.unb import getMoney, updateMoney
from util.config import config
from util.db import updatePlayerEntry
from util.permissions import runOnOtherPlayers, dmOnly

plugin = lightbulb.Plugin("Stats")

currencySymbol = config.get('currencySymbol')


def chargeCOL(member: hikari.Member, count=1) -> int:
    player = updatePlayerEntry(member)
    col = player.get('col', 0)

    successes = 0
    if getMoney(member) > col and successes < count:
        updateMoney(member, -col)
        successes += 1

    return successes



def createUserStatsEmbed(member: hikari.Member) -> hikari.Embed:
    player = updatePlayerEntry(member)
    # if not player:
    #     player = updatePlayerEntry(member)

    money = getMoney(member)
    col = player.get('col', 0)
    job = player.get('job', {})
    job_name = job.get('name', "Bum")
    job_desc = (job.get('description') + '\n') if job.get('description') else ""
    income = job.get('income') or 0
    tp = player.get('tech').get('points', Decimal128("0")).to_decimal()
    tp_inc = player.get('tech').get('increment').to_decimal()
    fp = player.get('feat').get('points', Decimal128("0")).to_decimal()
    fp_inc = player.get('feat').get('increment').to_decimal()
    exhaustion = player.get('exhaustion') or 0

    embed = (
        hikari.Embed(title=member.display_name + "'s stats")
            .add_field("Cost of Living:", currencySymbol + str(col))
            .add_field("Money:", currencySymbol + str(money))
            .add_field("Job: " + job_name, job_desc + "Income: " + currencySymbol + str(income))
            .add_field("Tech Points: ", str(tp) + " (+" + str(tp_inc) + "/period)")
            .add_field("Feature Points: ", str(fp) + " (+" + str(fp_inc) + "/period)")
            .set_thumbnail(member.display_avatar_url)
    )

    if exhaustion:
        embed.add_field("Exhaustion: ", str(exhaustion)).color = hikari.Color.from_rgb(255, 0, 0)

    return embed


@plugin.command
@lightbulb.add_checks(dmOnly)
@lightbulb.option("target", "The player whose cost of living to change", hikari.Member, required=True)
@lightbulb.option("amount", "The cost per one human maintenance session (typically once charged every day)", int, required=True)
@lightbulb.command("change-col", "Change the cost of living of a player")  # , ephemeral=True
# Define the command type(s) that this command implements
@lightbulb.implements(lightbulb.SlashCommand)
# Define the command's callback. The callback should take a single argument which will be
# an instance of a subclass of lightbulb.context.Context when passed in
async def changeCol(ctx: lightbulb.Context) -> None:
    target = ctx.options.target
    updatePlayerEntry(target, 'col', ctx.options.amount)
    await ctx.respond(createUserStatsEmbed(target))


@plugin.command
@lightbulb.add_checks(runOnOtherPlayers)
@lightbulb.option("target", "The player whose income to change", hikari.Member, required=False)
@lightbulb.command("stats", "Change the income of a player")  # , ephemeral=True
# Define the command type(s) that this command implements
@lightbulb.implements(lightbulb.SlashCommand)
# Define the command's callback. The callback should take a single argument which will be
# an instance of a subclass of lightbulb.context.Context when passed in
async def stats(ctx: lightbulb.Context) -> None:
    target = ctx.options.target or ctx.member
    # bot.d.players.update_one({"user_id": target.id}, {"$set": {"username": target.username, "display_name": target.display_name}}, upsert=True)
    updatePlayerEntry(target)
    await ctx.respond(createUserStatsEmbed(target))


def load(bot: lightbulb.BotApp) -> None:
    bot.add_plugin(plugin)
