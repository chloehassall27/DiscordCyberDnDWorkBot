import asyncio
from collections import Counter
from datetime import datetime

import hikari
import lightbulb
from bson import Decimal128
from multipledispatch import dispatch
from pytz import timezone

from plugins.jobs import workJob
from plugins.playerstats import createUserStatsEmbed, chargeCOL
from util.db import updatePlayerEntry
from util.permissions import runOnOtherPlayers, dmOnly

plugin = lightbulb.Plugin("Schedules")
bot: lightbulb.BotApp

TASKS = {
    "Work Job": "works job (+${player.job.income})",  # work_job
    "Practice Feature": "skills take time (+{player.feat.increment}FP)",  # practice_skill
    "Practice Tech": "tech takes time (+{player.tech.increment}TP)",  # practice_tech
    "Human Maintenance": "eat, sleep, you know, whatever normal people do (-${player.maintenanceCost})",  # human_maintenance
    # "Perform an Upgrade": "some upgrades take time to install new hardware/software and test for issues"  # perform_an_upgrade
}


def isAI(member: hikari.Member) -> bool:
    return any(role for role in member.get_roles() if role.name == "AI")


@dispatch(hikari.Guild)
def performDayUpdate(guild: hikari.Guild):
    members = guild.get_members().values()
    for member in members:
        if any(role for role in member.get_roles() if role.name == "Players"):
            performDayUpdate(member)


@dispatch(hikari.Member)
def performDayUpdate(member: hikari.Member):
    player = updatePlayerEntry(member)
    player_actions = bot.d.current_actions.find_one({"user_id": member.id})
    activities_list = []

    for period_name in ['morning', 'noon', 'night']:
        period = player_actions.get(period_name)
        if period:
            activities_list.append(period.get('activity'))

    activities = Counter(activities_list)
    changes_inc = {}
    changes_set = {}

    # Work job first so that human maintenance has best chance to happen
    count = activities.get('work_job')
    if count:
        workJob(member, count)

    if not isAI(member):
        count = activities.get('human_maintenance')
        exhaustion = player.get("exhaustion", 0) - count + 1  # Each day, 1 exhaustion is added
        if exhaustion < 0:
            exhaustion = 0
        changes_set["exhaustion"] = exhaustion

    count = activities.get('practice_feature')
    if count:
        changes_inc["feat.points"] = Decimal128(str(player.get('feat').get('increment').to_decimal() * count))

    count = activities.get('practice_tech')
    if count:
        changes_inc["tech.points"] = Decimal128(str(player.get('tech').get('increment').to_decimal() * count))
    # elif activity == 'perform_an_upgrade':

    updatePlayerEntry(member, {"last_day_update": str(datetime.now(timezone('America/New_York')))} | changes_set, changes_inc)

    if not chargeCOL(member):
        member.send("You have run out of money and were unable to complete your human maintenance period(s). Your exhaustion has gone up and is now at: " + str(exhaustion))


def verifyUserActionChange(member: hikari.Member, activity: str, period: str) -> str | None:
    # res = bot.d.current_actions.find_one({"user_id": member.id})
    # if not res:
    #     return None

    if activity == "human_maintenance" and (any(role for role in member.get_roles() if role.name == "AI")):
        return "AI cannot perform human maintenance"
    # elif activity == "human_maintenance" and res['activity'] == activity and res['period'] != period:
    #     return "Cannot perform human maintenance twice in same day"
    # elif(activity == "work_job" and res.activity is activity and res.period is not period):
    #     return "Cannot work job twice in same day"

    return None


def createUserScheduleEmbed(user: hikari.Member, updated=False) -> hikari.Embed:
    res = bot.d.current_actions.find_one({"user_id": user.id}) or {}
    morning = (res.get("morning", {}).get("activity") or "nothing").replace("_", " ").capitalize()
    noon = (res.get("noon", {}).get("activity") or "nothing").replace("_", " ").capitalize()
    night = (res.get("night", {}).get("activity") or "nothing").replace("_", " ").capitalize()

    embed = (
        hikari.Embed(title=user.display_name + "'s schedule")
            .add_field("Morning", morning)
            .add_field("Midday", noon)
            .add_field("Night", night)
            .set_thumbnail(user.display_avatar_url)
    )

    if updated:
        embed.set_footer("(updated)") \
            .color = hikari.Color.from_rgb(0, 255, 0)

    return embed


@plugin.command
@lightbulb.add_checks(dmOnly)
@lightbulb.option("player", "Name of a specific player to cause a new day for", hikari.Member, required=False)
@lightbulb.command("execute-day", "Update players' stats")
@lightbulb.implements(lightbulb.SlashCommand)
async def executeSchedule(ctx: lightbulb.Context) -> None:
    player = ctx.raw_options.get('player')
    performDayUpdate(player)
    if ctx.raw_options.get('player'):
        embed = createUserStatsEmbed(player)
        await ctx.respond(player.display_name + "'s day has been executed!", embed=embed,
                          flags=hikari.MessageFlag.EPHEMERAL)
    else:
        await ctx.respond("A new day is upon us!")


@plugin.command
@lightbulb.command("change-schedule", "Choose how to spend your time", ephemeral=True)
@lightbulb.implements(lightbulb.SlashCommand)
async def changeSchedule(ctx: lightbulb.Context) -> None:
    row = ctx.bot.rest.build_action_row()
    row.add_button(hikari.ButtonStyle.PRIMARY, "morning") \
        .set_label("Morning") \
        .add_to_container()
    row.add_button(hikari.ButtonStyle.PRIMARY, "noon") \
        .set_label("Noon") \
        .add_to_container()
    row.add_button(hikari.ButtonStyle.PRIMARY, "night") \
        .set_label("Night") \
        .add_to_container()

    sched = createUserScheduleEmbed(ctx.member)
    sched_response = await ctx.respond(sched)

    resp = await ctx.respond(
        "Which time slot would you like to change?",  # Message content
        component=row,
        # embed=sched,
    )
    msg = await resp.message()

    try:
        event = await ctx.bot.wait_for(
            hikari.InteractionCreateEvent,
            timeout=60,
            predicate=lambda e:
            isinstance(e.interaction, hikari.ComponentInteraction)
            and e.interaction.user.id == ctx.author.id
            and e.interaction.message.id == msg.id
        )

    except asyncio.TimeoutError:
        await msg.edit("The menu timed out :c", components=[])

    else:
        time = event.interaction.custom_id
        select_menu = (
            ctx.bot.rest.build_action_row()
                .add_select_menu(time + "_select")
                .set_placeholder("Pick an activity for " + time)
        )

        for title, description in TASKS.items():
            select_menu.add_option(
                title + " - " + description,  # the label, which users see
                title.lower().replace(" ", "_"),  # the value, which is used by us later
            ).add_to_menu()

        await event.interaction.create_initial_response(
            hikari.ResponseType.MESSAGE_UPDATE,
            "Changing " + time + " activity",
            component=select_menu.add_to_container(),
            # embed=sched,
        )

        try:
            event = await ctx.bot.wait_for(
                hikari.InteractionCreateEvent,
                timeout=60,
                predicate=lambda e:
                isinstance(e.interaction, hikari.ComponentInteraction)
                and e.interaction.user.id == ctx.author.id
                and e.interaction.message.id == msg.id
                and e.interaction.component_type == hikari.ComponentType.SELECT_MENU
            )
        except asyncio.TimeoutError:
            await msg.edit("The menu timed out :c", components=[])
        else:
            activity = event.interaction.values[0]

            user_action_illegal_msg = verifyUserActionChange(event.interaction.member, activity, time)
            if user_action_illegal_msg:
                await event.interaction.create_initial_response(
                    hikari.ResponseType.MESSAGE_UPDATE,
                    user_action_illegal_msg,
                    components=[],
                    # embed=sched,
                )
                return

            player_choice = {
                "user_id": event.interaction.member.id,
                "username": event.interaction.member.username,
                time + ".activity": activity,
                time + ".timestamp": str(datetime.now(timezone('America/New_York')))
            }
            bot.d.current_actions.update_one({"user_id": event.interaction.user.id}, {"$set": player_choice}, upsert=True)

            activity = activity.replace("_", " ")

            await event.interaction.create_initial_response(
                hikari.ResponseType.MESSAGE_UPDATE,
                f"You will {activity} in the " + time + "! :3",
                components=[],
                # embed=createUserScheduleEmbed(ctx.user, True),
            )

            # sched = createUserScheduleEmbed(ctx.user)
            await sched_response.edit(createUserScheduleEmbed(ctx.member, True))


@plugin.command
@lightbulb.add_checks(runOnOtherPlayers)
@lightbulb.option("target", "The member whose schedule to view", hikari.User, required=False)
@lightbulb.command("view-schedule", "View your current schedule", ephemeral=True)
@lightbulb.implements(lightbulb.SlashCommand)
async def viewSchedule(ctx: lightbulb.Context) -> None:
    target = ctx.options.target or ctx.member
    await ctx.respond(createUserScheduleEmbed(target))


def load(bot_: lightbulb.BotApp) -> None:
    bot_.add_plugin(plugin)
    global bot
    bot = plugin.bot
