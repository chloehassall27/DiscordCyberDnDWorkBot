import hikari

bot = hikari.GatewayBot(token="OTc1NDQyNzAzMTIwNzUyNzEw.G8hwPr.gL73M-AKdfkdA8rolgCC7dt19tg5UVM8KhivZM")

@bot.listen()
async def ping(event: hikari.GuildMessageCreateEvent) -> None:
    # If a non-bot user sends a message "hk.ping", respond with "Pong!"
    # We check there is actually content first, if no message content exists,
    # we would get `None' here.
    if event.is_bot or not event.content:
        return

    if event.content.startswith("hk.ping"):
        await event.message.respond("Pong!")

bot.run()