from discord import Role


def lookForChapterRoles(roles: [Role]):
    chapter_roles = []
    for role in roles:
        if role.name.startswith("College:"):
            chapter_roles.append(role.name[len("College: ") :])
        elif role.name.startswith("Corporate:"):
            chapter_roles.append(role).name[len("Corporate: ") :]
    return chapter_roles


def lookForGenderRoles(roles: [Role]):
    gender_roles = []
    for role in roles:
        if role.name in ["M", "F", "NB"]:
            return role.name
    return None
