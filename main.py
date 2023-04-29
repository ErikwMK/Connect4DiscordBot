import discord
from discord.ext import commands

import json
import asyncio


with open("config.json") as f:
    config = json.load(f)


class MyBot(commands.Bot):

    def __init__(self):
        intents = discord.Intents.default()
        intents.members = True
        intents.message_content = True
        super().__init__(
            command_prefix="_",
            intents=intents,
            application_id=config["APPLICATION_ID"]
        )
        self.synced = True

    async def setup_hook(self):
        extensions = ['Administration', 'Help', 'Connect4']
        for extension in extensions:
            await self.load_extension(f"cogs.{extension}")
            print(f"Added cog '{extension}'")

    async def on_ready(self):
        print(f"Logged in as {self.user}!")

bot = MyBot()

class MyHelp(commands.HelpCommand):  # custom help command
    async def send_bot_help(self, mapping):
        channel = self.get_destination()
        await channel.send("Feature not finished yet!") # TODO

bot.help_command = MyHelp()


@bot.event
async def on_command_error(ctx, error):  # Errorhanding
    if isinstance(error, commands.CommandNotFound):
        return
    if isinstance(error, commands.MissingPermissions) or isinstance(error, discord.app_commands.errors.MissingPermissions):
        return await(await ctx.channel.send("You don't have permission to use this command!")).delete(delay=5)
    if isinstance(error, commands.MissingAnyRole) or isinstance(error, discord.app_commands.errors.MissingAnyRole):
        return await(await ctx.send("You need one of the following roles to use this command: `%s`" % (", ".join(error.missing_roles)))).delete(delay=8)
    if isinstance(error, discord.app_commands.errors.CommandOnCooldown):
        return await ctx.channel.send('This command has a cooldown, please try again in {:.0f} seconds'.format(error.retry_after)).delete(delay=8)
    if isinstance(error, commands.BotMissingPermissions) or isinstance(error, discord.app_commands.errors.BotMissingPermissions):
        return await(await ctx.send("I need the following permissions to use this command: %s" % ", ".join(error.missing_permissions))).delete(delay=8)
    if isinstance(error, commands.NoPrivateMessage) or isinstance(error, discord.app_commands.errors.NoPrivateMessage):
        return await(await ctx.send("You can't use this command in DMs!")).delete(delay=5)
    if isinstance(error, TimeoutError):
        return
    if isinstance(error, asyncio.exceptions.CancelledError):
        return
    if isinstance(error, discord.app_commands.errors.CommandInvokeError):
        return
    if isinstance(error, discord.errors.NotFound):
        return
    if isinstance(error, discord.errors.HTTPException):
        return
    return await(await ctx.channel.send(f"Unexpected error! Pls DM {config['CREATOR_NAME']} if this happens again")).delete(delay=5)

bot.run(config["TOKEN"])
