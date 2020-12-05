import json

import aiosqlite
import discord
from discord.ext import commands


class _API(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.dbl = 'files/database.db'

    colours = {
        "bot": 0x3498DB,
        "error": 0xEF5350,
        "warning": 0xFF9100,
        "success": 0x00E676
    }

    async def get_guild_data(self, guild_id: int, key=None):
        async with aiosqlite.connect(self.dbl) as db:
            if key:
                async with db.execute('SELECT data_type, data FROM guild_data WHERE guild_id=? AND key=?;', (guild_id, str(key))) as cursor:
                    row = await cursor.fetchone()
                    return self.return_object(row[0], row[1]) if row else None
            else:
                async with db.execute('SELECT key, data_type, data FROM guild_data WHERE guild_id=?;', (guild_id, )) as cursor:
                    rows = await cursor.fetchall()
                    return rows or None

    async def set_guild_data(self, guild_id: int, key: str, data_type: str, data, overwrite: bool = True):
        async with aiosqlite.connect(self.dbl) as db:
            if await self.get_guild_data(guild_id, key):
                if overwrite:
                    await db.execute("UPDATE guild_data SET data_type=?, data=? WHERE guild_id=? AND key=?", (data_type, data, guild_id, key))
                else:
                    return False
            else:
                await db.execute("INSERT INTO guild_data (guild_id, key, data_type, data) VALUES (?, ?, ?, ?)", (guild_id, key, data_type, data))
            await db.commit()

    async def delete_guild_data(self, guild_id: int, key: str, confirmation: bool = False):
        async with aiosqlite.connect(self.dbl) as db:
            if confirmation and not key:
                await db.execute("DELETE FROM guild_data WHERE guild_id=?", (guild_id))
            else:
                await db.execute("DELETE FROM guild_data WHERE guild_id=? AND key=?", (guild_id, key))
            await db.commit()

    def return_object(self, data_type: str, data: str):
        if data_type == 'int':
            return int(data)  # 123
        elif data_type == 'str':
            return str(data)  # '123'
        elif data_type == 'tuple':
            return tuple(data)  # (1, 2, 3)
        elif data_type == 'dict' or data_type == 'json':
            return json.loads(data)  # {'numbers': '123'}
        elif data_type == 'float':
            return float(data)  # 1.23
        return None

    def error_embed(self, msg):
        return discord.Embed(
            colour=self.colours['error'],
            description=f'{str(self.bot.get_emoji(736803450226212956))}  {str(msg)}'
        )

    def info_embed(self, msg):
        return discord.Embed(
            colour=self.colours['bot'],
            description=str(msg)
        )

    def warning_embed(self, msg):
        return discord.Embed(
            colour=self.colours['warning'],
            description=str(msg)
        )

    def success_embed(self, msg):
        return discord.Embed(
            colour=self.colours['success'],
            description=f'{str(self.bot.get_emoji(739314513626660904))}  {str(msg)}'
        )


def setup(bot):
    bot.add_cog(_API(bot))
