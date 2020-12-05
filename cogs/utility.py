import datetime
import random
import typing

import discord
from discord.ext import commands

keyPermissions = ('KICK_MEMBERS', 'BAN_MEMBERS', 'ADMINISTRATOR', 'MANAGE_CHANNELS', 'MANAGE_GUILD', 'VIEW_AUDIT_LOG',
                  'MANAGE_MESSAGES', 'MENTION_EVERYONE', 'MANAGE_EMOJIS', 'MANAGE_ROLES', 'MANAGE_NICKNAMES', 'MANAGE_WEBHOOKS', 'MOVE_MEMBERS')


class UtilityCog(commands.Cog, name='Utilities'):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(aliases=['ru'],
                      brief='Chooses a random member in the server. Does not include bots')
    @commands.guild_only()
    @commands.cooldown(1, 1, type=commands.BucketType.channel)
    async def randomuser(self, ctx):
        m = random.choice([m for m in ctx.guild.members if not m.bot])
        await ctx.send(embed=discord.Embed(
            colour=m.colour.value or self.bot.api.colours['bot'],
            description=f'{m.mention} was randomly selected')
            .set_author(name=str(m), icon_url=m.avatar_url_as())
        )

    @commands.command(usage='<member>',
                      aliases=['av'],
                      brief='Returns the Avatar of a member')
    @commands.guild_only()
    async def avatar(self, ctx, *, target: commands.MemberConverter = None):
        tm = target or ctx.author
        await ctx.send(embed=discord.Embed(
            title=f'{tm.display_name}\'s Avatar',
            colour=tm.colour.value or self.bot.api.colours['bot'])
            .set_image(url=tm.avatar_url_as())
        )

    @commands.command(usage='<member or join position>',
                      aliases=['wi', 'profile'],
                      brief='Shows information about a member')
    @commands.guild_only()
    async def whois(self, ctx, *, target=None):
        if target and str(target).isdigit() and int(target) > 0 and int(target) <= ctx.guild.member_count:
            tm = sorted(ctx.guild.members, key=lambda m: m.joined_at)[
                int(target) - 1]
        else:
            tm = await commands.MemberConverter().convert(ctx, target) if target else ctx.author
        tm_roles = sorted(tm.roles, key=lambda r: r.position, reverse=True)
        tm_roles.pop()
        joinPosition = tuple(map(lambda m: m.joined_at, sorted(
            ctx.guild.members, key=lambda m: m.joined_at))).index(tm.joined_at) + 1
        roles = map(lambda r: r.mention, tm_roles)
        tm_permissions = list(filter(lambda p: p in keyPermissions, map(
            lambda p: p[0].upper(), filter(lambda p: p[1], list(tm.guild_permissions)))))
        tm_perms = 'ADMINISTRATOR' if 'ADMINISTRATOR' in tm_permissions else ", ".join(
            tm_permissions)
        embed = (discord.Embed(
            colour=tm.color.value or self.bot.api.colours['bot'],
            timestamp=datetime.datetime.now(),
            description=f'ID {tm.id} - {tm.mention}{" " + str(self.bot.get_emoji(739577978979090453)) if tm.bot else ""}'
        ).set_author(name=str(tm), icon_url=tm.avatar_url_as())
            .add_field(name='Joined guild', value=str(tm.joined_at.strftime('%m/%d/%Y, %H:%M:%S')), inline=True)
            .add_field(name='Account created', value=str(tm.created_at.strftime('%m/%d/%Y, %H:%M:%S')),  inline=True)
            .add_field(name='Join position', value=f'{joinPosition}/{ctx.guild.member_count}', inline=True)
            .add_field(name=f'Roles [{len(tm_roles)}]', value='\n'.join(roles)  or "User doesn't have any roles" if len(tm_roles) <= 25 else '\n'.join(list(roles)[:25]) + f'\n...and {len(tm_roles) - 25} more roles')
            .set_thumbnail(url=tm.avatar_url_as())
            .set_footer(text=f'{ctx.prefix}help whois'))
        if tm_permissions:
            embed.add_field(name=f'Key Permissions',
                            value=tm_perms, inline=False)
        await ctx.send(embed=embed)

    @commands.command(usage='<discord emoji>',
                      aliases=('enlarge',),
                      brief='Make an Emoji bigger')
    async def emoji(self, ctx, emoji: typing.Union[discord.Emoji, discord.PartialEmoji, str]):
        if type(emoji) is str:
            return await ctx.send(embed=self.bot.api.error_embed('I can only show emojis from Discord servers'))
        await ctx.send(embed=discord.Embed(
            title=f':{emoji.name}:',
            description=emoji.id,
            colour=self.bot.api.colours['bot']
        ).set_image(url=emoji.url))

    @commands.command(aliases=('mc',),
                      brief='Get the total member count in a server')
    @commands.guild_only()
    async def membercount(self, ctx):
        await ctx.send(embed=discord.Embed(colour=self.bot.api.colours['bot']).set_author(name=f'{ctx.guild.name} has {ctx.guild.member_count} members', icon_url=ctx.guild.icon_url_as()))

    @commands.command(usage='<discord emoji>',
                      brief='Steals an emoji provided and adds it to the server')
    @commands.guild_only()
    @commands.has_guild_permissions(manage_emojis=True)
    @commands.bot_has_guild_permissions(manage_emojis=True)
    async def stealemoji(self, ctx, emoji: typing.Union[discord.Emoji, discord.PartialEmoji, str]):
        if type(emoji) is str:
            return await ctx.send(embed=self.bot.api.error_embed('I can only add custom emojis from other Discord servers'))
        cemoji = await ctx.guild.create_custom_emoji(name=emoji.name, image=bytes(await emoji.url.read()), reason='Emoji added from command')
        await ctx.send(embed=discord.Embed(
            title=f'Added :{cemoji.name}: emoji!',
            description=f'ID {cemoji.id}',
            colour=self.bot.api.colours['success']
        ).set_image(url=cemoji.url))


def setup(bot):
    bot.add_cog(UtilityCog(bot))
