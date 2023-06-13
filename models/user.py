from utils.db import SupabaseInterface

class User:
    def __init__(self,userData):
        #self.name = userData["name"]
        self.discordId = userData["discordId"]
        self.discordUserName = userData("discordUserName")
        self.githubId = userData["githubId"]
    
    def exists(self, table):
        data = SupabaseInterface(table).read(query_key='discord_id', query_value=self.discordID)
        if len(data.data)>0:
            return True
        else:
            return False


class Contributor(User):
    def __init__(self, userData):
        super().__init__(userData)
        

class Mentor(User):
    def __init__(self, userData):
        super().__init__(userData)

class OrgMember(User):
    def __init__(self, userData):
        super().__init__(userData)

