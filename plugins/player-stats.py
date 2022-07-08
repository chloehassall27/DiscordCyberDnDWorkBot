import hikari
import lightbulb

from api.unb import getMoney
from permissions import dmOnly, runOnOtherPlayers

plugin = lightbulb.Plugin("Schedules")
bot = lightbulb.BotApp


def createUserStatsEmbed(member: hikari.Member) -> hikari.Embed:
    money = getMoney(member.id, member.guild_id)

    embed = (
        hikari.Embed(title=member.display_name + "'s stats")
        .add_field("Money", money)
        # .add_field("Income", noon)
        # .add_field("Night", night)
        .set_thumbnail(member.display_avatar_url)
    )

    return embed


@plugin.command
@lightbulb.add_checks(dmOnly)
@lightbulb.option("target", "The player whose income to change", hikari.User, required=True)
@lightbulb.option("amount", "The $ amount per 8hrs of work", int, required=True)
@lightbulb.command("change-income", "Change the income of a player", ephemeral=True)
# Define the command type(s) that this command implements
@lightbulb.implements(lightbulb.SlashCommand)
# Define the command's callback. The callback should take a single argument which will be
# an instance of a subclass of lightbulb.context.Context when passed in
async def changeIncome(ctx: lightbulb.Context) -> None:
    ()


@plugin.command
@lightbulb.add_checks(runOnOtherPlayers)
@lightbulb.option("target", "The player whose income to change", hikari.Member, required=False)
@lightbulb.command("stats", "Change the income of a player", ephemeral=True)
# Define the command type(s) that this command implements
@lightbulb.implements(lightbulb.SlashCommand)
# Define the command's callback. The callback should take a single argument which will be
# an instance of a subclass of lightbulb.context.Context when passed in
async def stats(ctx: lightbulb.Context) -> None:
    target = ctx.options.target or ctx.member
    await ctx.respond(createUserStatsEmbed(target))


def load(bot_: lightbulb.BotApp) -> None:
    bot_.add_plugin(plugin)
    global bot
    bot = plugin.bot
