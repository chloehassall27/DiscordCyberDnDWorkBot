import os

import dotenv
import lightbulb
import pymongo
from hikari import StartingEvent, StoppingEvent, Intents

from util.db import initDbHelper

dotenv.load_dotenv()
intents = (
    Intents.ALL_UNPRIVILEGED |
    Intents.GUILD_MEMBERS
)
# Instantiate a Bot instance
bot = lightbulb.BotApp(token=os.getenv('DISCORD_TOKEN'), intents=intents)


@bot.listen()
async def on_starting(event: StartingEvent) -> None:
    bot.d.mongoClient = pymongo.MongoClient("mongodb://localhost:27017/")
    bot.d.db = bot.d.mongoClient["originalServer"]
    bot.d.current_actions = bot.d.db["currentActions"]
    bot.d.players = bot.d.db["players"]
    bot.d.logs = bot.d.db["logs"]
    initDbHelper(bot)
    bot.load_extensions_from("./plugins/", must_exist=True)


@bot.listen()
async def on_stopping(event: StoppingEvent) -> None:
    await bot.d.mongoClient.close()



# Run the bot
# Note that this is blocking meaning no code after this line will run
# until the bot is shut off
if __name__ == "__main__":
    bot.run()
