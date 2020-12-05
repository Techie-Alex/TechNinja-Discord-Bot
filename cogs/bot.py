import datetime

import discord
from discord.ext import commands


class BotCog(commands.Cog, name='Bot'):
    def __init__(self, bot):
        self.bot = bot
        self.durl = 'https://discord.gg/UTMSqJR'

    @commands.command(usage='[command]',
                      brief='Get a list of commands or help for a specific command')
    async def help(self, ctx, *, tcmd=None):
        burl = f'https://discordapp.com/oauth2/authorize?client_id={self.bot.user.id}&scope=bot&permissions=8'
        if tcmd:
            command = self.bot.get_command(tcmd)
            if command and ((command.enabled and not command.hidden) or ctx.author.id == self.bot.owner_id):
                embed = discord.Embed(
                    title=ctx.prefix + command.name + " " +
                    command.usage if command.usage else ctx.prefix + command.name,
                    colour=self.bot.api.colours['bot']
                )
                if command.brief:
                    embed.description = command.brief
                if command.cog.qualified_name:
                    embed.add_field(
                        name='Category', value=command.cog.qualified_name, inline=True)
                if command.aliases:
                    embed.add_field(name='Aliases', value=", ".join(command.aliases) if len(
                        command.aliases) > 2 else " or ".join(command.aliases), inline=True)
                if command.description:
                    embed.add_field(
                        name='Info', value=command.description, inline=False)
                return await ctx.send(embed=embed)
            else:
                return await ctx.send(embed=self.bot.api.info_embed('Command not found'))
        embed = discord.Embed(
            title='TechNinja Commands',
            colour=self.bot.api.colours['bot'],
            description=f'{ctx.prefix}help [command]')
        for name in self.bot.cogs:
            commands = self.bot.cogs[name].get_commands()
            commandCount = len(
                list(filter(lambda cmd: True if ctx.author.id == self.bot.owner_id else cmd.enabled and not cmd.hidden, commands)))
            if commandCount > 0:
                embed.add_field(name=name, value=', '.join(
                    map(lambda cmd: f'`{cmd.name}`', commands)), inline=False)
        embed.add_field(
            name='Useful Links', value=f'[Invite Bot]({burl}) | [Join Discord]({self.durl})', inline=False)
        await ctx.send(embed=embed)

    @commands.command()
    async def invite(self, ctx):
        burl = f'https://discordapp.com/oauth2/authorize?client_id={self.bot.user.id}&scope=bot&permissions=8'
        await ctx.send(embed=discord.Embed(
            colour=self.bot.api.colours['bot'],
            description=f'[{burl}]({burl})')
            .set_author(name='Click here to invite me!', url=burl))

    @ commands.command()
    async def discord(self, ctx):
        await ctx.send(embed=discord.Embed(colour=self.bot.api.colours['bot'], description=f'[{self.durl}]({self.durl})').set_author(name='Click here to join the bots support Discord server', url=self.durl))

    @ commands.command(usage='<your suggestion>',
                       aliases=('request',))
    @ commands.cooldown(1, 300, type=commands.BucketType.user)
    async def suggest(self, ctx, *, suggestion):
        sc = await self.bot.fetch_channel('743619380880998433')
        if sc:
            embed = discord.Embed(
                description=f'{ctx.author.mention} suggests: {suggestion}',
                colour=0xF7EB07,
                timestamp=datetime.datetime.now()
            ).set_footer(text=f'ID {ctx.author.id}').set_author(name=f'New suggestion from {ctx.author}', icon_url=ctx.author.avatar_url_as())
            if ctx.guild:
                embed.add_field(name='Sent in Guild',
                                value=f'{ctx.guild.id} - {ctx.guild.name}')
            msg = await sc.send(embed=embed)
            await msg.pin()
        await ctx.send(embed=self.bot.api.success_embed('Successfully submitted your suggestion!'))


def setup(bot):
    bot.add_cog(BotCog(bot))
