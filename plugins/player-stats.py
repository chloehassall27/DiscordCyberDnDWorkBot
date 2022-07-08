import hikari
import lightbulb

from api.unb import getMoney
from util.db import updatePlayerEntry, findPlayerEntry
from util.permissions import runOnOtherPlayers

plugin = lightbulb.Plugin("Stats")
bot: lightbulb.BotApp


def createUserStatsEmbed(member: hikari.Member) -> hikari.Embed:
    player = findPlayerEntry(member)
    if not player:
        player = updatePlayerEntry(member)

    money = getMoney(member.id, member.guild_id)
    job = player.get('job') or {}
    name = job.get('name') or "Bum"
    desc = job.get('description') or ""
    income = job.get('income') or 0

    return (
        hikari.Embed(title=member.display_name + "'s stats")
        .add_field("Money", money)
        .add_field(name, desc + "\nIncome: $" + str(income))
        # .add_field("Night", night)
        .set_thumbnail(member.display_avatar_url)
    )


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


def load(bot_: lightbulb.BotApp) -> None:
    bot_.add_plugin(plugin)
    global bot
    bot = plugin.bot
