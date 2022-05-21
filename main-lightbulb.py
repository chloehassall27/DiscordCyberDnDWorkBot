# Import the command handler
from datetime import datetime

import hikari
import lightbulb

# Instantiate a Bot instance
bot = lightbulb.BotApp(token="OTc1NDQyNzAzMTIwNzUyNzEw.G8hwPr.gL73M-AKdfkdA8rolgCC7dt19tg5UVM8KhivZM", prefix="+")


# Register the command to the bot
@bot.command
# Use the command decorator to convert the function into a command
@lightbulb.command("ping", "checks the bot is alive")
# Define the command type(s) that this command implements
@lightbulb.implements(lightbulb.PrefixCommand)
# Define the command's callback. The callback should take a single argument which will be
# an instance of a subclass of lightbulb.context.Context when passed in
async def ping(ctx: lightbulb.Context) -> None:
    # Send a message to the channel the command was used in
    await ctx.respond("Pong!")


# Register the command to the bot
@bot.command
# Use the command decorator to convert the function into a command
@lightbulb.option(
    "target", "The member to get information about.", hikari.User, required=False
)
@lightbulb.command("changeSchedule", "presents every player the options on what to do with their day")
# Define the command type(s) that this command implements
@lightbulb.implements(lightbulb.PrefixCommand)
# Define the command's callback. The callback should take a single argument which will be
# an instance of a subclass of lightbulb.context.Context when passed in
async def startDay(ctx: lightbulb.Context) -> None:
    guild = ctx.get_guild()
    target = caller = guild.get_member(ctx.user)

    # TURN THIS INTO A FUNCTION
    if ctx.options.target and caller != ctx.options.target:
        for role in caller.get_roles():
            if role.name == "DMs":
                print("DM!")
                target = guild.get_member(ctx.options.target)
                break
        else:
            await ctx.respond("You do not have permission to run this command on another player.")
            return

        if not target:
            await ctx.respond("That user is not in the server.")
            return

    created_at = int(target.created_at.timestamp())
    joined_at = int(target.joined_at.timestamp())

    roles = (await target.fetch_roles())[1:]  # All but @everyone

    embed = (
        hikari.Embed(
            title=f"User Info - {target.display_name}",
            description=f"ID: `{target.id}`",
            colour=0x3B9DFF,
            timestamp=datetime.now().astimezone(),
        )
            .set_footer(
            text=f"Requested by {ctx.member.display_name}",
            icon=ctx.member.avatar_url or ctx.member.default_avatar_url,
        )
            .set_thumbnail(target.avatar_url or target.default_avatar_url)
            .add_field(
            "Bot?",
            str(target.is_bot),
            inline=True,
        )
            .add_field(
            "Created account on",
            f"<t:{created_at}:d>\n(<t:{created_at}:R>)",
            inline=True,
        )
            .add_field(
            "Joined server on",
            f"<t:{joined_at}:d>\n(<t:{joined_at}:R>)",
            inline=True,
        )
            .add_field(
            "Roles",
            ", ".join(r.mention for r in roles),
            inline=False,
        )
    )

    await ctx.respond(embed)


# Run the bot
# Note that this is blocking meaning no code after this line will run
# until the bot is shut off
bot.run()
