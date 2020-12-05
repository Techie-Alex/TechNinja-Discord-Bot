#!/usr/bin/python3
import os
import discord
from discord.ext import commands
from files.token import discord_token
bot = commands.Bot(
    owner_id=250425759452233729,
    command_prefix=commands.when_mentioned_or('t.', 'T.'),
    case_insensitive=True,
    help_command=None,
    intents=discord.Intents(reactions=True, messages=True, members=True, guilds=True)
)
for f in [f for f in os.listdir('./cogs') if f.endswith('.py')]:
    bot.load_extension(f'cogs.{os.path.splitext(f)[0]}')
bot.api = bot.get_cog('_API')
bot.run(discord_token, bot=True, reconnect=True)
