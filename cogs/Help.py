import discord
from discord.ext import commands

import json


with open("config.json") as f:
    config = json.load(f)


class PingHelp(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_message(self, ctx):
        if ctx.content == "<@926801089989333012>":
            pass
            # send bot help command TODO


async def setup(bot):
    await bot.add_cog(
        PingHelp(bot)
    )
