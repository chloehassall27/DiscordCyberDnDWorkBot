import hikari
import lightbulb

from util.db import updatePlayerEntry
from util.permissions import dmOnly

plugin = lightbulb.Plugin("Jobs")
bot: lightbulb.BotApp


@plugin.command
@lightbulb.add_checks(dmOnly)
@lightbulb.option("income", "The $ amount per 8hrs of work", int, required=False)
@lightbulb.option("job-name", "Name of the job", int, required=False)
@lightbulb.option("job-description", "Description of the job", int, required=False)
@lightbulb.option("target", "The player whose income to change", hikari.User, required=True)
@lightbulb.command("change-job", "Change the job info of a player", ephemeral=True)
# Define the command type(s) that this command implements
@lightbulb.implements(lightbulb.SlashCommand)
# Define the command's callback. The callback should take a single argument which will be
# an instance of a subclass of lightbulb.context.Context when passed in
async def setIncome(ctx: lightbulb.Context) -> None:
    income = ctx.raw_options.get('income')
    name = ctx.raw_options.get('job-name')
    desc = ctx.raw_options.get('job-description')
    changed_fields = []
    if income:
        if income < 0:
            await ctx.respond("Income must be >= 0")
            return
        if income > 0 and not name:
            await ctx.respond("Must include job name if income")
            return
        if income == 0 and not name:
            updatePlayerEntry(ctx.options.target, "job.name", "")
            return
    if name:
        updatePlayerEntry(ctx.options.target, "job.name", name)
        changed_fields += "job name"
    if desc:
        updatePlayerEntry(ctx.options.target, "job.description", desc)
        changed_fields += "job description"
    if income:
        updatePlayerEntry(ctx.options.target, "job.income", income)
        changed_fields += "income"

    await ctx.respond("Changed " + str(", ".join(changed_fields)) + " successfully!")


def load(bot_: lightbulb.BotApp) -> None:
    bot_.add_plugin(plugin)
    global bot
    bot = plugin.bot
