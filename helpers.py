import discord

def lookForCollegeRoles(roles: [discord.Role]):
    college_roles = []
    for role in roles:
        if role.name.startswith('College:'):
            college_roles.append(role.name[len('College: '):])

    return college_roles

def lookForGenderRoles(roles: [discord.Role]):
    gender_roles = []
    for role in roles:
        if role.name in ['M', 'F', 'NB']:
            return role.name
    return None

