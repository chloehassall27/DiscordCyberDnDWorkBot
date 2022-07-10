import hikari
import lightbulb

from api.unb import getMoney
from util.config import config
from util.db import updatePlayerEntry, findPlayerEntry
from util.permissions import runOnOtherPlayers

plugin = lightbulb.Plugin("Stats")

currencySymbol = config.get('currencySymbol')


def createUserStatsEmbed(member: hikari.Member) -> hikari.Embed:
    player = findPlayerEntry(member)
    if not player:
        player = updatePlayerEntry(member)

    money = getMoney(member.id, member.guild_id)
    job = player.get('job') or {}
    job_name = job.get('name') or "Bum"
    job_desc = (job.get('description') + '\n') if job.get('description') else ""
    income = job.get('income') or 0
    tp = player.get('tech_points') or 0
    fp = player.get('feature_points') or 0
    exhaustion = player.get('exhaustion') or 0

    embed = (
        hikari.Embed(title=member.display_name + "'s stats")
            .add_field("Money: ", currencySymbol + str(money))
            .add_field("Job: " + job_name, job_desc + "Income: " + currencySymbol + str(income))
            .add_field("Tech Points: ", str(tp))
            .add_field("Feature Points: ", str(fp))
            .set_thumbnail(member.display_avatar_url)
    )

    if exhaustion:
        embed.add_field("Exhaustion: ", str(exhaustion)).color(hikari.Color.from_rgb(255, 0, 0))

    return embed


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
