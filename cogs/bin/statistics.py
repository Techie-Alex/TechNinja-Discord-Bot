import aiosqlite
from datetime import datetime
database_path = "files/stats.db"


async def log_command(ctx):
    try:
        time = datetime.now().timestamp()
        async with aiosqlite.connect(database_path) as db:
            await db.execute("INSERT INTO commands (cmd_name, timestamp, guild_id, channel_id, author_id, message) VALUES (?, ?, ?, ?, ?, ?)",
                             (ctx.command.name, time, str({"id": ctx.guild.id, "name": ctx.guild.name, "members": ctx.guild.member_count}) if ctx.guild else "DMs", str({"id": ctx.channel.id, "name": ctx.channel.name}) if ctx.guild else "DMs", str({"id": ctx.author.id, "name": str(ctx.author)}), ctx.message.content))
            await db.commit()
    except Exception as e:
        print(
            f'=-=-=-= Error with statistics -> log_command -> {e}\n\nCommand: {ctx.command.name}')


async def log_error(log_type, location, data):
    try:
        print(f'=- Error -> {location} -> {data}')
        time = datetime.now().timestamp()
        async with aiosqlite.connect(database_path) as db:
            async with db.execute("INSERT INTO logs (type, timestamp, location, data) VALUES (?, ?, ?, ?)", (log_type, time, location, str(data))) as cursor:
                error_id = cursor.lastrowid
            await db.commit()
            return error_id
    except Exception as e:
        print(
            f'=-=-=-= Error with statistics -> log_error -> {e}\n\nOriginal Error: {location} -> {data}')
        return 0


async def log_guild(action, guild):
    try:
        time = datetime.now().timestamp()
        async with aiosqlite.connect(database_path) as db:
            await db.execute("INSERT INTO guilds (action, guild_name, guild_id, timestamp, users, bots, member_count) VALUES (?, ?, ?, ?, ?, ?, ?)", (action, guild.name, guild.id, time, None, None, guild.member_count))
            await db.commit()
    except Exception as e:
        print(f'=-=-=-= Error with statistics -> log_guild -> {e}')
