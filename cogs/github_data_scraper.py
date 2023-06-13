from discord.ext import commands

class GithubDataScraper(commands.Cog):
    def __init__(self, bot) -> None:
        self.bot = bot
    

    @commands.command()
    async def update_prs(self, ctx):
        return 
    
    @commands.command()
    async def update_issues(self, ctx):
        return 
    
    @commands.command()
    async def update_commits(self, ctx):
        return 
    
    




async def setup(bot):
    await bot.add_cog(GithubDataScraper(bot))