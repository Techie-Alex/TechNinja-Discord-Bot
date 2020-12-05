import re

import discord
from datetime import datetime
from discord.ext import commands, tasks

import cogs.bin.statistics as stats


class _Events(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.serversIn = 0
        self.presence.start()

    def cog_unload(self):
        self.presence.cancel()

    @tasks.loop(seconds=60)
    async def presence(self):
        await self.bot.wait_until_ready()
        try:
            if self.serversIn != len(self.bot.guilds):
                self.serversIn = len(self.bot.guilds)
                await self.bot.change_presence(activity=discord.Activity(name=f'tb.help - in {self.serversIn} servers', type=discord.ActivityType.listening), status=discord.Status.online)
        except Exception as e:
            print(e)

    @commands.Cog.listener()
    async def on_ready(self):
        print(f'{self.bot.user} is ready')

    @commands.Cog.listener()
    async def on_command(self, ctx):
        await stats.log_command(ctx)

    @commands.Cog.listener()
    async def on_error(self, event, error):
        await stats.log_error("error", f"_bote -> on_error -> {event}", error)

    @commands.Cog.listener()
    async def on_member_join(self, member):
        channel_id = await self.bot.api.get_guild_data(member.guild.id, 'joinleave_log_channel') or await self.bot.api.get_guild_data(member.guild.id, 'join_log_channel')
        if not channel_id:
            return
        channel = member.guild.get_channel(channel_id)
        if not channel:
            return
        await channel.send(embed=self.joinleave_embed(member, 'joined', 'success'))

    @commands.Cog.listener()
    async def on_member_remove(self, member):
        channel_id = await self.bot.api.get_guild_data(member.guild.id, 'joinleave_log_channel') or await self.bot.api.get_guild_data(member.guild.id, 'leave_log_channel')
        if not channel_id:
            return
        channel = member.guild.get_channel(channel_id)
        if not channel:
            return
        await channel.send(embed=self.joinleave_embed(member, 'left', 'error'))

    @commands.Cog.listener()
    async def on_guild_join(self, guild):
        await stats.log_guild("join", guild)

    @commands.Cog.listener()
    async def on_guild_remove(self, guild):
        await stats.log_guild("remove", guild)

    @commands.Cog.listener()
    async def on_raw_reaction_add(self, reaction):
        await self.reaction_role(reaction, 'add')

    @commands.Cog.listener()
    async def on_raw_reaction_remove(self, reaction):
        await self.reaction_role(reaction, 'remove')

    @commands.Cog.listener()
    async def on_message(self, message):
        if re.match(r"^<@!?{0}> ?$".format(self.bot.user.id), message.content):
            await message.channel.send(embed=discord.Embed(
                description=f'Hi! I am a bot. My prefix is: `t.` Need help? Try `t.help`',
                colour=self.bot.api.colours['bot']
            ).set_footer(text=f'bot coded by {str(self.bot.get_user(self.bot.owner_id))}', icon_url=self.bot.get_user(self.bot.owner_id).avatar_url_as()))

    async def reaction_role(self, reaction, action: str):
        try:
            if not reaction.guild_id:
                return
            rd = await self.bot.api.get_guild_data(reaction.guild_id, "reaction_roles")
            if not rd:
                return
            cid = str(reaction.channel_id)
            mid = str(reaction.message_id)
            emoji = str(reaction.emoji.id or reaction.emoji)
            if cid in rd and mid in rd[cid] and emoji in rd[cid][mid]:
                rid = int(rd[cid][mid][emoji])
                gm = self.bot.get_guild(
                    reaction.guild_id).get_member(reaction.user_id)
                tgr = gm.guild.get_role(rid)
                if not tgr or gm.bot:
                    return
                if action == "add":
                    if not (tgr in gm.roles):
                        await gm.add_roles(tgr, reason='Added role automatically from Reaction Roles')
                elif action == "remove":
                    if tgr in gm.roles:
                        await gm.remove_roles(tgr, reason='Removed role automatically from Reaction Roles')

        except Exception as e:
            print(f'Reaction Error: {e}')

    def joinleave_embed(self, member: discord.Member, action: str, colour: str):
        return discord.Embed(
            colour=self.bot.api.colours[colour],
            timestamp=datetime.now(),
            description=f'{member.mention}{" " + str(self.bot.get_emoji(739577978979090453)) if member.bot else ""} {action} the server'
        ).set_author(name=str(member) + (" [BOT]" if member.bot else ""), icon_url=member.avatar_url_as())


def setup(bot):
    bot.add_cog(_Events(bot))
