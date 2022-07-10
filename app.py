import os

import dotenv
import hikari
import lightbulb
import pymongo

from util.db import initDbHelper

dotenv.load_dotenv()
# Instantiate a Bot instance
bot = lightbulb.BotApp(token=os.getenv('DISCORD_TOKEN'))


@bot.listen()
async def on_starting(event: hikari.StartingEvent) -> None:
    bot.d.mongoClient = pymongo.MongoClient("mongodb://localhost:27017/")
    bot.d.db = bot.d.mongoClient["originalServer"]
    bot.d.current_actions = bot.d.db["currentActions"]
    bot.d.players = bot.d.db["players"]
    bot.d.logs = bot.d.db["logs"]
    initDbHelper(bot)
    bot.load_extensions_from("./plugins/", must_exist=True)


@bot.listen()
async def on_stopping(event: hikari.StoppingEvent) -> None:
    await bot.d.mongoClient.close()



# Run the bot
# Note that this is blocking meaning no code after this line will run
# until the bot is shut off
if __name__ == "__main__":
    bot.run()
