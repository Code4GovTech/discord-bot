from discord import Role

def lookForRoles(roles: [Role]):
    predefined_roles = {
        "country": ["India", "Asia (Outside India)", "Europe", "Africa", "North America", "South America", "Australia"],
        "city": ["Delhi", "Bangalore", "Mumbai", "Pune", "Hyderabad", "Chennai", "Kochi"],
        "experience": [
            "Tech Freshman", 
            "Tech Sophomore", 
            "Tech Junior", 
            "Tech Senior", 
            "Junior Developer", 
            "Senior Developer", 
            "Super Senior Developer", 
            "Champion Developer"
        ],
        "gender": ["M", "F", "NB"]
    }
    chapter_roles = []
    gender = None
    country = None
    city = None
    experience = None
    for role in roles:
        if role.name.startswith("College:"):
            chapter_roles.append(role.name[len("College: ") :])
        elif role.name.startswith("Corporate:"):
            chapter_roles.append(role).name[len("Corporate: ") :]
    
    #gender
    for role in roles:
        if role.name in predefined_roles["gender"]:
            gender =  role.name
            break

    #country
    for role in roles:
        if role.name in predefined_roles["country"]:
            country =  role.name
            break
        
    #city
    for role in roles:
        if role.name in predefined_roles["city"]:
            city = role.name
            break

    #experience
    for role in roles:
        if role.name in predefined_roles["experience"]:
            experience = role.name
            break
    
    user_roles = {
        "chapter_roles": chapter_roles,
        "gender": gender,
        "country": country,
        "city": city,
        "experience": experience
    }
    return user_roles
    

# def lookForChapterRoles(roles: [Role]):
#     chapter_roles = []
#     for role in roles:
#         if role.name.startswith("College:"):
#             chapter_roles.append(role.name[len("College: ") :])
#         elif role.name.startswith("Corporate:"):
#             chapter_roles.append(role).name[len("Corporate: ") :]
#     return chapter_roles


# def lookForGenderRoles(roles: [Role]):
#     for role in roles:
#         if role.name in ["M", "F", "NB"]:
#             return role.name
#     return None

# def lookForCountryRoles(roles: [Role]):
#     for role in roles:
#         if role.name in ["India", "Asia (Outside India)", "Europe", "Africa", "North America", "South America", "Australia"]:
#             return role.name
#     return None
    
# def lookForCityRoles(roles: [Role]):
#     for role in roles:
#         if role.name in ["Delhi", "Bangalore", "Mumbai", "Pune", "Hyderabad", "Chennai", "Kochi"]:
#             return role.name
#     return None
    
# def lookForExperienceRoles(roles: [Role]):
#     for role in roles:
#         if role.name in ["Tech Freshman", "Tech Sophomore", "Tech Junior", "Tech Senior", "Junior Developer", "Senior Developer", "Super Senior Developer", "Champion Developer"]:
#             return role.name
#     return None
