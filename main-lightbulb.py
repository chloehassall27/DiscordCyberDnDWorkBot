# Import the command handler

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


@bot.listen()
async def on_starting(event: hikari.StartingEvent) -> None:
    bot.d.mongoClient = pymongo.MongoClient("mongodb://localhost:27017/")
    bot.d.db = bot.d.mongoClient["originalServer"]
    bot.d.current_actions = bot.d.db["currentActions"]


@bot.listen()
async def on_stopping(event: hikari.StoppingEvent) -> None:
    await bot.d.mongoClient.close()


bot.load_extensions_from("./plugins/", must_exist=True)
# Run the bot
# Note that this is blocking meaning no code after this line will run
# until the bot is shut off
bot.run()
