import hikari


def isAI(member: hikari.Member) -> bool:
    return any(role for role in member.get_roles() if role.name == "AI")


def isPlayer(member: hikari.Member) -> bool:
    return any(role for role in member.get_roles() if role.name == "Players")
