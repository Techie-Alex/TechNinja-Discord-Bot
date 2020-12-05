from datetime import datetime
import inspect
from typing import Collection

import discord
from discord.ext import commands


class DevCog(commands.Cog, name='Dev', command_attrs=dict(hidden=True)):
    def __init__(self, bot):
        self.bot = bot

    temp1 = None
    temp2 = None
    temp3 = None

    @commands.command(name='eval', aliases=['e'])
    @commands.is_owner()
    async def _eval(self, ctx, *, ecode: str = "'Nothing'"):
        if ctx.author.id != self.bot.owner_id:
            return
        try:
            result = eval(ecode)
            if inspect.isawaitable(result):
                result = await result
            await ctx.send(embed=discord.Embed(
                colour=self.bot.api.colours['success'])
                .add_field(name='input', value=f'```python\n{ecode}```', inline=0)
                .add_field(name='output', value=f'```python\n{result}```', inline=0)
            )
        except Exception as e:
            await ctx.send(embed=discord.Embed(
                colour=self.bot.api.colours['error'])
                .add_field(name='input', value=f'```python\n{ecode}```', inline=0)
                .add_field(name='error output', value=f'```python\n{str(e)}```', inline=0)
            )

    @commands.command(name='evals', aliases=['es'])
    @commands.is_owner()
    async def _evals(self, ctx, *, ecode: str = "'Nothing'"):
        if ctx.author.id != self.bot.owner_id:
            return
        try:
            result = eval(ecode)
            if inspect.isawaitable(result):
                await result
            await ctx.message.add_reaction('✅')
        except Exception as e:
            await ctx.message.add_reaction('❌')

    @commands.command(name='evalm', aliases=['em'])
    @commands.is_owner()
    async def _evalm(self, ctx, *, ecode: str = "'Nothing'"):
        if ctx.author.id != self.bot.owner_id:
            return
        try:
            result = eval(ecode)
            if inspect.isawaitable(result):
                result = await result
            await ctx.send(result)
        except Exception as e:
            await ctx.message.add_reaction('❌')

    lastCog = None

    @commands.command(aliases=['r'], description='Reload files for development without stopping bot')
    @commands.is_owner()
    async def reload(self, ctx, *arg):
        if not (self.lastCog or arg):
            return await ctx.send(embed=self.bot.api.info_embed('Select a cog first'))
        self.lastCog = self.lastCog if self.lastCog and not arg else arg[0]
        try:
            self.bot.reload_extension(f'cogs.{self.lastCog}')
            if self.lastCog == '_api':
                self.bot.api = self.bot.get_cog('_API')
            await ctx.send(embed=self.bot.api.success_embed(f'Reloaded /cogs/{self.lastCog}.py'))
        except Exception as error:
            await ctx.send(embed=self.bot.api.error_embed(f'Failed to reload cog: {error}'))

    @commands.command(usage='<key or all> [data or delete] [data_type] [overwrite]',
                      aliases=['gd'])
    @commands.is_owner()
    @commands.guild_only()
    async def guilddata(self, ctx, key: str, data: str = None, data_type: str = 'str', overwrite: bool = True):
        if key == "all":
            rdata = await self.bot.api.get_guild_data(ctx.guild.id)
            return await ctx.send(f'getting all guild data:\n\n' + str("\n".join(map(lambda f: f'{f}', rdata))) or "None")
        if data and data == "delete":
            await self.bot.api.delete_guild_data(ctx.guild.id, key)
        elif data:
            await self.bot.api.set_guild_data(ctx.guild.id, key, data_type, data, overwrite)
        rdata = await self.bot.api.get_guild_data(ctx.guild.id, key)
        await ctx.send(f'data: type - {type(rdata)}\n{rdata or "None"}')


def setup(bot):
    bot.add_cog(DevCog(bot))
