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