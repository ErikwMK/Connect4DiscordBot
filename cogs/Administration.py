import discord
from discord.ext import commands

class Administration(commands.Cog):
    def __init__(self, bot):
        self.bot = bot


    @commands.Cog.listener()
    async def on_message(self, ctx):
        if (ctx.author.id not in [807602307369271306]) or (not isinstance(ctx.channel, discord.DMChannel)):
            return
        if ctx.content.lower() == "botstats":
            server_count = len(self.bot.guilds)
            servers = ""
            count = 1
            for server in self.bot.guilds:
                servers = servers + f"`{count}.` **{server}**, Server Owner is: {self.bot.get_user(int(server.owner.id))}\n"
                count += 1
            await ctx.channel.send(f"FRZ Bot is at the moment in **{server_count} servers**\nHere is a list of all servers:\n{servers}")
            return

        elif ctx.content.lower() in ["synccommandtree", "sync", "sct"]:
            await self.bot.tree.sync()
            print("The command tree was synced")
            await ctx.channel.send("Done!")

        elif ctx.content.lower() == "shutdown":
            exit(f"Shut down by {ctx.author.name}")

        return

async def setup(bot):
    await bot.add_cog(
        Administration(bot)
    )
