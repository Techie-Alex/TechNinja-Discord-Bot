import asyncio

import discord
from discord.ext import commands


class ModerationCog(commands.Cog, name='Moderation'):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(usage='<member> [reason]')
    @commands.guild_only()
    @commands.has_guild_permissions(ban_members=True)
    @commands.bot_has_guild_permissions(ban_members=True)
    async def ban(self, ctx, targetMember: discord.Member, *reason):
        if targetMember.id == ctx.guild.owner_id:
            return await ctx.send(embed=self.bot.api.error_embed('Ban ban ban! But wait! You can\'t ban the OWNER!'))
        targetHR = targetMember.top_role
        authorHR = ctx.author.top_role
        botHR = ctx.me.top_role
        aboveBotRole = discord.utils.get(
            ctx.guild.roles, position=botHR.position + 1)
        belowBotRole = discord.utils.get(
            ctx.guild.roles, position=botHR.position - 1)
        if (ctx.guild.owner_id != ctx.author.id and authorHR.position <= targetHR.position):
            return await ctx.send(embed=self.bot.api.error_embed('You do not have permission to ban this member as they are a higher role!'))
        if botHR.position <= targetHR.position:
            return await ctx.send(embed=self.bot.api.error_embed(f'Unable to ban member! You can fix this by moving the <@&{botHR.id}> role higher as shown below\n\n↱ \\*Move to here\\*\n⭡ <@&{targetHR.id}>\n⭡  ...\n⭡ <@&{aboveBotRole.id}>\n⬑ \\*<@&{botHR.id}>\\*\n­ ឵឵ ឵឵ ឵឵ ឵឵<@&{belowBotRole.id}>'))
        reason = ' '.join(reason) if reason else 'No reason provided'
        postMsg = await ctx.send(embed=discord.Embed(
            description=f'Are you sure you want to ban this member?\n\nMember\n`{str(targetMember)}`\n\nReason\n`{reason}`',
            colour=self.bot.api.colours['bot']
        ).set_footer(text='this expires in 15 seconds'))
        await postMsg.add_reaction('✅')
        await postMsg.add_reaction('🚫')
        try:
            reaction, user = await self.bot.wait_for('reaction_add', timeout=15.0, check=lambda reaction, user: user == ctx.author and str(reaction.emoji) in ('✅', '🚫'))
        except asyncio.TimeoutError:
            await postMsg.clear_reactions()
            await postMsg.edit(embed=discord.Embed(
                description=f'Did not ban `{str(targetMember)}` because time ran out',
                colour=self.bot.api.colours['warning']
            ))
        else:
            await postMsg.clear_reactions()
            if (str(reaction.emoji) == '✅'):
                try:
                    await targetMember.ban(reason=reason, delete_message_days=3)
                    await postMsg.edit(embed=self.bot.api.success_embed(f'Successfully banned `{str(targetMember)}` for `{reason}`'))
                except Exception as error:
                    await postMsg.edit(embed=self.bot.api.error_embed(f'There was an error banning this member: `{str(error.text)}`'))
            else:
                await postMsg.edit(embed=discord.Embed(
                    description=f'Cancelled banning `{str(targetMember)}` for `{reason}`',
                    colour=self.bot.api.colours['warning']
                ))

    @commands.command(usage='<member> [reason]')
    @commands.guild_only()
    @commands.has_guild_permissions(kick_members=True)
    @commands.bot_has_guild_permissions(kick_members=True)
    async def kick(self, ctx, targetMember: discord.Member, *reason):
        if targetMember.id == ctx.guild.owner_id:
            return await ctx.send(embed=self.bot.api.error_embed('Lol, you tried to kick the owner. Good try though'))
        targetHR = targetMember.top_role
        authorHR = ctx.author.top_role
        botHR = ctx.me.top_role
        aboveBotRole = discord.utils.get(
            ctx.guild.roles, position=botHR.position + 1)
        belowBotRole = discord.utils.get(
            ctx.guild.roles, position=botHR.position - 1)
        if (ctx.guild.owner_id != ctx.author.id and authorHR.position <= targetHR.position):
            return await ctx.send(embed=self.bot.api.error_embed('You do not have permission to kick this member as they are a higher role!'))
        if botHR.position <= targetHR.position:
            return await ctx.send(embed=self.bot.api.error_embed(f'Unable to kick member! You can fix this by moving the <@&{botHR.id}> role higher as shown below\n\n↱ \\*Move to here\\*\n⭡ <@&{targetHR.id}>\n⭡  ...\n⭡ <@&{aboveBotRole.id}>\n⬑ \\*<@&{botHR.id}>\\*\n­ ឵឵ ឵឵ ឵឵ ឵឵<@&{belowBotRole.id}>'))
        reason = ' '.join(reason) if reason else 'No reason provided'
        postMsg = await ctx.send(embed=discord.Embed(
            description=f'Are you sure you want to kick this member?\n\nMember\n`{str(targetMember)}`\n\nReason\n`{reason}`',
            colour=self.bot.api.colours['bot']
        ).set_footer(text='this expires in 15 seconds'))
        await postMsg.add_reaction('✅')
        await postMsg.add_reaction('🚫')
        try:
            reaction, user = await self.bot.wait_for('reaction_add', timeout=15.0, check=lambda reaction, user: user == ctx.author and str(reaction.emoji) in ('✅', '🚫'))
        except asyncio.TimeoutError:
            await postMsg.clear_reactions()
            await postMsg.edit(embed=discord.Embed(
                description=f'Did not kick `{str(targetMember)}` because time ran out',
                colour=self.bot.api.colours['warning']
            ))
        else:
            await postMsg.clear_reactions()
            if (str(reaction.emoji) == '✅'):
                try:
                    await targetMember.kick(reason=reason)
                    await postMsg.edit(embed=self.bot.api.success_embed(f'Successfully kicked `{str(targetMember)}` for `{reason}`'))
                except Exception as error:
                    await postMsg.edit(embed=self.bot.api.error_embed(f'There was an error kicking this member: `{str(error.text)}`'))
            else:
                await postMsg.edit(embed=discord.Embed(
                    description=f'Cancelled kicking `{str(targetMember)}` for `{reason}`',
                    colour=self.bot.api.colours['warning']
                ))

    @commands.command(usage='<amount of messages \*max 200\*>', aliases=('clear', 'cls'))
    @commands.guild_only()
    @commands.has_guild_permissions(manage_messages=True)
    @commands.bot_has_guild_permissions(manage_messages=True)
    @commands.cooldown(1, 5, type=commands.BucketType.channel)
    @commands.max_concurrency(1, per=commands.BucketType.channel, wait=False)
    async def purge(self, ctx, amount):
        if not amount.isdigit() or int(amount) < 2 or int(amount) > 200:
            return await ctx.send(embed=self.bot.api.info_embed('Amount must be between **2** and **200**'))
        await ctx.message.delete()
        await asyncio.sleep(0.5)
        try:
            deletedMsgs = await ctx.channel.purge(limit=int(amount))
            msg = await ctx.send(embed=self.bot.api.success_embed(f'Successfully cleared `{len(deletedMsgs)}` messages'))
            await asyncio.sleep(3.5)
            await msg.delete()
        except Exception as e:
            await ctx.send(embed=self.bot.api.error_embed(f'There was an error deleting {amount} messages:\n\n{e.text}'))

    @commands.command(usage='<member> [reason]')
    @commands.guild_only()
    @commands.has_guild_permissions(manage_roles=True)
    @commands.bot_has_guild_permissions(manage_roles=True)
    async def mute(self, ctx, targetMember: discord.Member, *, reason="Mute - No reason"):
        try:
            mute_role = await commands.RoleConverter().convert(ctx, await self.bot.api.get_guild_data(ctx.guild.id, 'mute_role') or 'Muted')
        except commands.BadArgument:
            return await ctx.send(embed=self.bot.api.info_embed('I was unable to find the muted role set in Settings or a role named `Muted`'))
        if mute_role in targetMember.roles:
            return await ctx.send(embed=self.bot.api.info_embed(f'{str(targetMember)} is already Muted'))
        try:
            await targetMember.add_roles(mute_role, reason=reason)
            return await ctx.send(embed=self.bot.api.success_embed(f'{str(targetMember)} was muted'))
        except Exception as e:
            return await ctx.send(embed=self.bot.api.error_embed(f'Failed to mute user: {str(e)}'))

    @commands.command(usage='<member> [reason]')
    @commands.guild_only()
    @commands.has_guild_permissions(manage_roles=True)
    @commands.bot_has_guild_permissions(manage_roles=True)
    async def unmute(self, ctx, targetMember: discord.Member, *, reason="Un-Mute - No reason"):
        try:
            mute_role = await commands.RoleConverter().convert(ctx, await self.bot.api.get_guild_data(ctx.guild.id, 'mute_role') or 'Muted')
        except commands.BadArgument:
            return await ctx.send(embed=self.bot.api.info_embed('I was unable to find the muted role set in Settings or a role named `Muted`'))
        if mute_role not in targetMember.roles:
            return await ctx.send(embed=self.bot.api.info_embed(f'{str(targetMember)} is not Muted'))
        try:
            await targetMember.remove_roles(mute_role, reason=reason)
            return await ctx.send(embed=self.bot.api.success_embed(f'{str(targetMember)} was un-muted'))
        except Exception as e:
            return await ctx.send(embed=self.bot.api.error_embed(f'Failed to un-mute user: {str(e)}'))


def setup(bot):
    bot.add_cog(ModerationCog(bot))
