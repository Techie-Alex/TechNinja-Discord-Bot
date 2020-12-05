import asyncio
import json
from os import name
import typing
from typing import Collection

import discord
from discord.channel import TextChannel
from discord.ext import commands


class SettingsCog(commands.Cog, name='Settings'):
    def __init__(self, bot):
        self.bot = bot

    @commands.group(invoke_without_command=True)
    @commands.guild_only()
    async def reactions(self, ctx):
        await ctx.send(embed=discord.Embed(
            title="Reactions sub-commands",
            colour=self.bot.api.colours['bot']
        ).add_field(name='add', value='Add a reaction role to any message. This allows anyone to react to that message and receive a role', inline=False)
            .add_field(name='list', value='List all the reaction roles you have set for this server', inline=False)
            .add_field(name='delete', value='Delete reaction roles based on ID from the list sub-command', inline=False)
            .set_footer(text=f'{ctx.prefix}reactions <sub-command>'))

    @reactions.command(usage='<msgLink or <channel> <messageid>> <emoji> <role>')
    @commands.guild_only()
    @commands.bot_has_guild_permissions(administrator=True)
    @commands.has_guild_permissions(administrator=True)
    async def add(self, ctx, channel: typing.Optional[discord.TextChannel], message: str, emoji: typing.Union[discord.Emoji, discord.PartialEmoji, str], *, role: discord.Role):
        if channel and message.isdigit():
            msg = await commands.MessageConverter().convert(ctx, f'{channel.id}-{message}')
        else:
            msg = await commands.MessageConverter().convert(ctx, message)
            channel = msg.channel
        r_data = await self.bot.api.get_guild_data(ctx.guild.id, 'reaction_roles') or {}
        eid = str(emoji if type(emoji) == str else emoji.id)
        cid = str(channel.id)
        mid = str(msg.id)
        r_data.setdefault(cid, {})
        r_data[cid].setdefault(mid, {})
        r_data[cid][mid][eid] = role.id
        await self.bot.api.set_guild_data(ctx.guild.id, 'reaction_roles', 'json', json.dumps(r_data))
        await ctx.send(embed=discord.Embed(
            title='Reaction Role added successfully',
            description=f'When members react to the message below with the {emoji} emoji, they will receive the {role.name} role',
            colour=self.bot.api.colours['success']
        ).add_field(name='Channel', value=f'<#{channel.id}>')
            .add_field(name='Message ID', value=f'[{msg.id}](https://discordapp.com/channels/{ctx.guild.id}/{channel.id}/{msg.id})')
            .add_field(name='Emoji', value=emoji)
            .add_field(name='Role', value=role.mention))
        try:
            await msg.add_reaction(emoji)
        except Exception as e:
            await ctx.send(embed=self.bot.api.warning_embed('I was unable to add the emoji to the message, the reaction role has been added successfully. Add the emoji above to the message for it to take effect'))

    @reactions.command()
    @commands.guild_only()
    @commands.bot_has_guild_permissions(administrator=True)
    @commands.has_guild_permissions(administrator=True)
    async def list(self, ctx):
        data = await self.bot.api.get_guild_data(ctx.guild.id, 'reaction_roles')
        readable_list = ""
        num = 0
        if data:
            readable_list += "ID » Channel Name » MessageID » Emoji: Role"
            for channel in data:
                num += 1
                readable_list += f"\n{num}. ㅤ<#{channel}>\n"
                for message in data[channel]:
                    num += 1
                    readable_list += f"{num}. ㅤ↳ [{message}](https://discordapp.com/channels/{ctx.guild.id}/{channel}/{message})\n"
                    for emoji in data[channel][message]:
                        num += 1
                        readable_list += f"{num}.ㅤㅤㅤ↳ {str(self.bot.get_emoji(int(emoji)) or emoji) if str(emoji).isdigit() else emoji}: <@&{data[channel][message][emoji]}>\n"
        if readable_list:
            await ctx.send(embed=discord.Embed(
                colour=self.bot.api.colours['bot'],
                description=readable_list)
                .set_footer(text='want to delete an reaction? use: delete <ID>')
                .set_author(name=f'Reaction Messages in {ctx.guild.name}', icon_url=ctx.guild.icon_url_as())
            )
        else:
            await ctx.send(embed=discord.Embed(
                colour=self.bot.api.colours['bot'],
                description=f'You don\'t have any reaction roles. You can create one with **{ctx.prefix}reactions add**')
            )

    @reactions.command(usage='<ID>\n\nGet ID from reactions list')
    @commands.guild_only()
    @commands.bot_has_guild_permissions(administrator=True)
    @commands.has_guild_permissions(administrator=True)
    async def delete(self, ctx, number: int):
        r_data = await self.bot.api.get_guild_data(ctx.guild.id, 'reaction_roles')
        if r_data:
            data = {"channel": None, "message": None,
                    "emoji": None, "msg": None}
            num = 0
            for channel in r_data:
                num += 1
                if num is number:
                    data["channel"] = channel
                    data["msg"] = f"**ALL** reactions in the channel:\n\n<#{channel}>"
                    break
                for message in r_data[channel]:
                    num += 1
                    if num is number:
                        data["channel"] = channel
                        data["message"] = message
                        data["msg"] = f"ALL reactions for message:\n\n<#{channel}> -> [{message}](https://discordapp.com/channels/{ctx.guild.id}/{channel}/{message})"
                        break
                    for emoji in r_data[channel][message]:
                        num += 1
                        if num is number:
                            data["channel"] = channel
                            data["message"] = message
                            data["emoji"] = emoji
                            break
            if data["channel"]:
                if data["emoji"]:
                    del r_data[data["channel"]][data["message"]][data["emoji"]]
                    await ctx.send(embed=self.bot.api.success_embed(f"Deleted Reaction Role: <#{data['channel']}> -> [{data['message']}](https://discordapp.com/channels/{ctx.guild.id}/{data['channel']}/{data['message']}) -> {str(self.bot.get_emoji(int(data['emoji'])) or data['emoji']) if str(data['emoji']).isdigit() else data['emoji']}"))
                else:
                    postMsg = await ctx.send(embed=discord.Embed(
                        description=f'Are you sure you want to delete {data["msg"]}?',
                        colour=self.bot.api.colours['bot']
                    ).set_footer(text='this expires in 15 seconds'))
                    await postMsg.add_reaction('✅')
                    await postMsg.add_reaction('🚫')
                    try:
                        reaction, user = await self.bot.wait_for('reaction_add', timeout=15.0, check=lambda reaction, user: user == ctx.author and str(reaction.emoji) in ('✅', '🚫'))
                    except asyncio.TimeoutError:
                        await postMsg.clear_reactions()
                        await postMsg.edit(embed=discord.Embed(
                            description=f'Did not delete any reactions, time ran out'
                        ))
                    else:
                        await postMsg.clear_reactions()
                        if (str(reaction.emoji) == '✅'):
                            if data["message"]:
                                del r_data[data["channel"]][data["message"]]
                            else:
                                del r_data[data["channel"]]
                            await postMsg.edit(embed=self.bot.api.success_embed(f'Deleted {data["msg"]}'))
                        else:
                            await postMsg.edit(embed=discord.Embed(
                                description=f'Cancelled deleting the reactions',
                                colour=self.bot.api.colours['bot']
                            ))
                if r_data == {}:
                    await self.bot.api.delete_guild_data(ctx.guild.id, 'reaction_roles')
                else:
                    await self.bot.api.set_guild_data(ctx.guild.id, 'reaction_roles', 'json', json.dumps(r_data))
        else:
            await ctx.send(embed=discord.Embed(
                colour=self.bot.api.colours['bot'],
                description=f'You don\'t have any reaction roles. You can create one with **{ctx.prefix}reactions add**')
            )

    @commands.group(invoke_without_command=True)
    @commands.guild_only()
    async def logs(self, ctx):
        await ctx.send(embed=discord.Embed(
            title="Logs sub-commands",
            colour=self.bot.api.colours['bot']
        ).add_field(name='join', value='Set the channel logs for members joining only', inline=False)
            .add_field(name='leave', value='Set the channel logs for members leaving only', inline=False)
            .add_field(name='joinleave', value='Set the channel logs for members joining/leaving', inline=False)
            .set_footer(text=f'{ctx.prefix}logs <sub-command>'))

    @logs.command(usage='<channel> or none')
    @commands.guild_only()
    @commands.bot_has_guild_permissions(manage_channels=True)
    @commands.has_guild_permissions(manage_channels=True)
    async def join(self, ctx, *, channel: typing.Union[discord.TextChannel, str]):
        if type(channel) is str:
            if channel.lower() == 'none':
                await self.bot.api.delete_guild_data(ctx.guild.id, 'join_log_channel')
                await ctx.channel.send('Deleted join logs channel')
            else:
                await ctx.channel.send('Unknown channel')
        else:
            await self.bot.api.set_guild_data(ctx.guild.id, 'join_log_channel', 'int', channel.id)
            await ctx.channel.send(f'Set to {channel.id}')

    @logs.command(usage='<channel> or none')
    @commands.guild_only()
    @commands.bot_has_guild_permissions(manage_channels=True)
    @commands.has_guild_permissions(manage_channels=True)
    async def leave(self, ctx, channel: typing.Union[discord.TextChannel, str]):
        if type(channel) is str:
            if channel.lower() == 'none':
                await self.bot.api.delete_guild_data(ctx.guild.id, 'leave_log_channel')
                await ctx.channel.send('Deleted leave logs channel')
            else:
                await ctx.channel.send('Unknown channel')
        else:
            await self.bot.api.set_guild_data(ctx.guild.id, 'leave_log_channel', 'int', channel.id)
            await ctx.channel.send(f'Set to {channel.id}')

    @logs.command(usage='<channel> or none')
    @commands.guild_only()
    @commands.bot_has_guild_permissions(manage_channels=True)
    @commands.has_guild_permissions(manage_channels=True)
    async def joinleave(self, ctx, channel: typing.Union[discord.TextChannel, str]):
        if type(channel) is str:
            if channel.lower() == 'none':
                await self.bot.api.delete_guild_data(ctx.guild.id, 'joinleave_log_channel')
                await ctx.channel.send('Deleted join-leave logs channel')
            else:
                await ctx.channel.send('Unknown channel')
        else:
            await self.bot.api.set_guild_data(ctx.guild.id, 'joinleave_log_channel', 'int', channel.id)
            await ctx.channel.send(f'Set to {channel.id}')

    @commands.command(usage='<mute role or none>')
    @commands.guild_only()
    @commands.cooldown(1, 3, type=commands.BucketType.guild)
    @commands.bot_has_guild_permissions(administrator=True)
    @commands.has_guild_permissions(administrator=True)
    async def setmuterole(self, ctx, *, role):
        if role == 'none':
            if not await self.bot.api.get_guild_data(ctx.guild.id, 'mute_role'):
                return await ctx.send(embed=self.bot.api.error_embed('There\'s not a mute role currently set'))
            await self.bot.api.delete_guild_data(ctx.guild.id, 'mute_role')
            return await ctx.send(embed=self.bot.api.success_embed('Removed the set mute role'))
        role = await commands.RoleConverter().convert(ctx, role)
        if ctx.author.id != ctx.guild.owner_id and ctx.author.top_role.position <= role.position:
            return await ctx.send(embed=self.bot.api.info_embed('You cannot set the mute role the same or higher than your top role. Owners bypass this'))
        await self.bot.api.set_guild_data(ctx.guild.id, 'mute_role', 'str', role.id)
        await ctx.send(embed=self.bot.api.success_embed(f'Set the mute role to {str(role.mention)}'))


def setup(bot):
    bot.add_cog(SettingsCog(bot))
