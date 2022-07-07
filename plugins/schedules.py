import asyncio

import hikari
import lightbulb

from permissions import runOnOtherPlayers

plugin = lightbulb.Plugin("Schedules")
bot = lightbulb.BotApp

TASKS = {
    "Work Job": "works job (+${player.job.income})",
    "Practice Skill": "skills take time (+{player.skill.currentIncrement}SP)",
    "Human Maintenance": "eat, sleep, you know, whatever normal people do (-${player.maintenanceCost})",
    "Perform an Upgrade": "some upgrades take time to install new hardware and test for issues"
}


def createUserScheduleEmbed(user: hikari.User) -> hikari.Embed:
    res = bot.d.current_actions.find_one({"user_id": user.id, "period": "morning"})
    morning = ((res and res['activity']) or "nothing").replace("_", " ").capitalize()
    res = bot.d.current_actions.find_one({"user_id": user.id, "period": "noon"})
    noon = ((res and res['activity']) or "nothing").replace("_", " ").capitalize()
    res = bot.d.current_actions.find_one({"user_id": user.id, "period": "night"})
    night = ((res and res['activity']) or "nothing").replace("_", " ").capitalize()

    return (
        hikari.Embed(title=user.username + "'s schedule")
            .add_field("Morning", morning)
            .add_field("Midday", noon)
            .add_field("Night", night)
            .set_thumbnail(user.display_avatar_url)
        # .set_footer("Last updated: ")
    )


# Register the command to the bot
@plugin.command
@lightbulb.command("change-schedule", "Choose how to spend your time", ephemeral=True)
# Define the command type(s) that this command implements
@lightbulb.implements(lightbulb.SlashCommand)
# Define the command's callback. The callback should take a single argument which will be
# an instance of a subclass of lightbulb.context.Context when passed in
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

    resp = await ctx.respond(
        "Which time slot would you like to change?",  # Message content
        component=row,
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
            str.title(time) + " activity",
            component=select_menu.add_to_container(),
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
            player_choice = {"user_id": event.interaction.user.id, "username": event.interaction.user.username,
                             "period": time, "activity": activity,
                             "timestamp": event.interaction.created_at}
            bot.d.current_actions.replace_one({"user_id": event.interaction.user.id, "period": time}, player_choice,
                                              upsert=True)

            activity = activity.replace("_", " ")

            await event.interaction.create_initial_response(
                hikari.ResponseType.MESSAGE_UPDATE,
                f"You will {activity} in the " + time + "! :3", components=[]
            )


# Register the command to the bot
@plugin.command
@lightbulb.add_checks(runOnOtherPlayers)
# Use the command decorator to convert the function into a command
@lightbulb.option(
    "target", "The member whose schedule to view", hikari.User, required=False
)
@lightbulb.command("view-schedule", "View your current schedule", ephemeral=True)
# Define the command type(s) that this command implements
@lightbulb.implements(lightbulb.SlashCommand)
# Define the command's callback. The callback should take a single argument which will be
# an instance of a subclass of lightbulb.context.Context when passed in
async def viewSchedule(ctx: lightbulb.Context) -> None:
    target = ctx.options.target or ctx.user
    await ctx.respond(createUserScheduleEmbed(target))


def load(bot_: lightbulb.BotApp) -> None:
    bot_.add_plugin(plugin)
    global bot
    bot = plugin.bot