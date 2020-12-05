import asyncio

import discord
from discord.ext import commands

import cogs.bin.statistics as stats


class _Bote(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_command_error(self, ctx, error):
        try:
            if hasattr(ctx.command, 'on_error'):
                return
            if isinstance(error, commands.CommandNotFound) or isinstance(error, commands.NotOwner):
                msg = await ctx.send(embed=self.bot.api.info_embed(f'Command not found. Maybe try **{ctx.prefix}help**?'))
                await asyncio.sleep(5)
                await msg.delete()
            elif isinstance(error, commands.NoPrivateMessage):
                await ctx.send(embed=self.bot.api.info_embed(f'This command can only be ran in a guild. If you need one to test the bot with you can join here: **https://discord.gg/aTbjbCM**'))
            elif isinstance(error, commands.MissingRequiredArgument):
                await ctx.send(embed=discord.Embed(
                    title="Missing Arguments(s)",
                    description=f"{ctx.prefix}{f'{ctx.command.parent.name} {ctx.command.name}' if ctx.command.parent else ctx.command.name} **{ctx.command.usage}**" if ctx.command.usage else 'No command usage found for command',
                    colour=self.bot.api.colours['error']
                ).set_footer(text=f"need more help? try {ctx.prefix}help"))
            elif isinstance(error, commands.BadArgument):
                await ctx.send(embed=self.bot.api.info_embed(error))
            else:
                error_num = await stats.log_error("command_error", f"_bote -> on_command_error -> {ctx.command.name}", str(error))
                await ctx.send(embed=self.bot.api.error_embed(error).set_footer(text=f'error id {error_num}'))
        except Exception as e:
            await stats.log_error(
                "command_error", "_bote -> on_command_error -> Exception", str(e))


def setup(bot):
    bot.add_cog(_Bote(bot))
