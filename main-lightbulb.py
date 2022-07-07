# Import the command handler

import asyncio

import hikari
import lightbulb
import pymongo

# Instantiate a Bot instance
bot = lightbulb.BotApp(token="OTc1NDQyNzAzMTIwNzUyNzEw.G8hwPr.gL73M-AKdfkdA8rolgCC7dt19tg5UVM8KhivZM")


# Register the command to the bot
@bot.command
# Use the command decorator to convert the function into a command
@lightbulb.command("ping", "checks the bot is alive")
# Define the command type(s) that this command implements
@lightbulb.implements(lightbulb.SlashCommand)
# Define the command's callback. The callback should take a single argument which will be
# an instance of a subclass of lightbulb.context.Context when passed in
async def ping(ctx: lightbulb.Context) -> None:
    # Send a message to the channel the command was used in
    bot.d.test = "ping"
    await ctx.respond("Pong!")

@lightbulb.Check
async def checkPermission(ctx: lightbulb.Context) -> bool:
    guild = ctx.get_guild()
    target = caller = guild.get_member(ctx.user)

    if ctx.options.target and caller != ctx.options.target:
        for role in caller.get_roles():
            if role.name == "DMs":
                print("DM!")
                # target = guild.get_member(ctx.options.target)
                return True
        else:
            await ctx.respond("You do not have permission to run this command on another player.")
            return False

    return True


TASKS = {
    "Work Job": "works job (+${player.job.income})",
    "Practice Skill": "skills take time (+{player.skill.currentIncrement}SP)",
    "Human Maintenance": "eat, sleep, you know, whatever normal people do (-${player.maintenanceCost})",
    "Perform an Upgrade": "some upgrades take time to install new hardware and test for issues"
}


# Register the command to the bot
@bot.command
@lightbulb.add_checks(checkPermission)
# Use the command decorator to convert the function into a command
@lightbulb.option(
    "target", "The member whose day to start.", hikari.User, required=False
)
@lightbulb.command("change-schedule", "presents every player the options on what to do with their day", ephemeral=True, aliases="cs")
# Define the command type(s) that this command implements
@lightbulb.implements(lightbulb.SlashCommand)
# Define the command's callback. The callback should take a single argument which will be
# an instance of a subclass of lightbulb.context.Context when passed in
async def changeSchedule(ctx: lightbulb.Context) -> None:
    row = ctx.bot.rest.build_action_row()

    row.add_button(hikari.ButtonStyle.PRIMARY, "morning")\
        .set_label("Morning")\
        .add_to_container()
    row.add_button(hikari.ButtonStyle.PRIMARY, "noon")\
        .set_label("Noon")\
        .add_to_container()
    row.add_button(hikari.ButtonStyle.PRIMARY, "night")\
        .set_label("Night")\
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
            player_choice = {"user_id": event.interaction.user.id, "username": event.interaction.user.username, "period": time, "activity": activity,
                             "timestamp": event.interaction.created_at}
            bot.d.current_actions.replace_one({"user_id": event.interaction.user.id, "period": time}, player_choice, upsert=True)

            activity = activity.replace("_", " ")

            await event.interaction.create_initial_response(
                hikari.ResponseType.MESSAGE_UPDATE,
                f"You will {activity} in the " + time + "! :3", components=[]
            )


@bot.listen()
async def on_starting(event: hikari.StartingEvent) -> None:
    bot.d.mongoClient = pymongo.MongoClient("mongodb://localhost:27017/")
    bot.d.db = bot.d.mongoClient["originalServer"]
    bot.d.current_actions = bot.d.db["currentActions"]


@bot.listen()
async def on_stopping(event: hikari.StoppingEvent) -> None:
    await bot.d.mongoClient.close()


# Run the bot
# Note that this is blocking meaning no code after this line will run
# until the bot is shut off
bot.run()
