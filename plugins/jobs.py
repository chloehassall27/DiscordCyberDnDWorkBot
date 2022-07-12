import random

import hikari
import lightbulb

from api.unb import updateMoney
from util.config import config
from util.db import updatePlayerEntry
from util.permissions import dmOnly

plugin = lightbulb.Plugin("Jobs")


def workJob(member: hikari.Member, count=1):
    player = updatePlayerEntry(member)
    income = player.get('job', {}).get('income', 0)
    success_rate = player.get('job', {}).get('success-rate', 100)
    for i in range(count):
        random.seed()
        if random.randint(1, 100) <= success_rate:
            updateMoney(member, income)


@plugin.command
@lightbulb.add_checks(dmOnly)
@lightbulb.option("income", "The " + config.get('currencySymbol') + " amount per 8hrs of work", int, required=False)
@lightbulb.option("job-name", "Name of the job", str, required=False)
@lightbulb.option("job-description", "Description of the job", str, required=False)
@lightbulb.option("job-success-rate", "% of the time player gets paid (ex. 75 means 3/4 working periods pay out)", int, required=False)
@lightbulb.option("target", "The player whose income to change", hikari.Member, required=True)
@lightbulb.command("change-job", "Change the job info of a player", ephemeral=True)
# Define the command type(s) that this command implements
@lightbulb.implements(lightbulb.SlashCommand)
# Define the command's callback. The callback should take a single argument which will be
# an instance of a subclass of lightbulb.context.Context when passed in
async def changeJob(ctx: lightbulb.Context) -> None:
    job = updatePlayerEntry(ctx.options.target).get("job")
    prev_name = ""
    if job:
        prev_name = job.get("name")
    income = ctx.raw_options.get('income')
    name = ctx.raw_options.get('job-name')
    desc = ctx.raw_options.get('job-description')
    success_rate = ctx.raw_options.get('job-success-rate')
    changed_fields = ""
    if income:
        if income < 0:
            await ctx.respond("Income must be >= 0")
            return
        if income > 0 and not (name or prev_name):
            await ctx.respond("Must include job name if income is > " + config.get('currencySymbol') + "0")
            return
        if income == 0 and not name:
            updatePlayerEntry(ctx.options.target, "job.name", "")
            return
    if success_rate and (success_rate < 1 or success_rate > 100):
        await ctx.respond("Success rate must be between 1-100 (inclusive)")
        return

    if name:
        updatePlayerEntry(ctx.options.target, "job.name", name)
        changed_fields = changed_fields + "job name, "
    if desc:
        updatePlayerEntry(ctx.options.target, "job.description", desc)
        changed_fields = changed_fields + "job description, "
    if income:
        updatePlayerEntry(ctx.options.target, "job.income", income)
        changed_fields = changed_fields + "income, "
    if success_rate:
        updatePlayerEntry(ctx.options.target, "job.success-rate", success_rate)
        changed_fields = changed_fields + "success rate, "

    changed_fields = changed_fields[:-2]

    await ctx.respond("Changed " + changed_fields + " successfully!")


def load(bot: lightbulb.BotApp) -> None:
    bot.add_plugin(plugin)
