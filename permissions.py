import lightbulb

@lightbulb.Check
async def runOnOtherPlayers(ctx: lightbulb.Context) -> bool:
    caller = ctx.member
    target = ctx.options.target

    if target and caller and caller.id != target.id:
        for role in caller.get_roles():
            if role.name == "DMs":
                return True
        else:
            await ctx.respond("You do not have permission to run this command on another player.")
            return False

    return True
