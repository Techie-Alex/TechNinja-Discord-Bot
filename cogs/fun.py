import asyncio
import random

import discord
from discord.ext import commands

ers = {
    "normal": {
        "name": 'The 8ball',
        "thinkingGif": 'https://media.giphy.com/media/2seaKlqqoGglLcPH2Q/giphy.gif',
        "responses": [
            ['It is certain', 'It is decidedly so', 'Without a doubt', 'Yes definitely', 'You may rely on it',
             'As I see it, yes', 'Most likely', 'Outlook good', 'Yes', 'Signs point to yes'],
            ['Reply hazy try again', 'Ask again later', 'Better not tell you now',
             'Cannot predict now', 'Concentrate and ask again'],
            ['Don\'t count on it', 'My reply is no', 'My sources say no',
             'Outlook not so good', 'Very doubtful']
        ],
        "colors": [0x00E676, 0xF9A825, 0xFF5252],
        "gifs": [
            ['https://media.giphy.com/media/3o7abKhOpu0NwenH3O/giphy.gif',
             'https://media.giphy.com/media/S3Ot3hZ5bcy8o/giphy.gif'],
            ['https://media.giphy.com/media/Jt4sQOFEh29Ob8KAxg/giphy.gif',
             'https://media.giphy.com/media/W1f2ZkNPv3m8P60xvd/giphy.gif'],
            ['https://media.giphy.com/media/gnE4FFhtFoLKM/giphy.gif', 'https://media.giphy.com/media/d10dMmzqCYqQ0/giphy.gif',
             'https://media.giphy.com/media/TfS8MAR9ucLHW/giphy.gif']
        ]
    },
    "trump": {
        "name": 'Trump',
        "thinkingGif": 'https://media.giphy.com/media/wJNGA01o1Zxp6/giphy.gif',
        "responses": [
            ['I will make America great again! (Yes)', 'I would build a great wall (Yes)',
             'I think I am a nice person (Yes)', 'I beat China all the time (Yes)'],
            ['Will Mexico pay for the wall? (Try Again)', 'Bing bing bong bong (Try Again)',
             'I\'m really rich (Try Again)', 'La La La La (Try Again)', 'Here\'s an idea (Try Again)'],
            ['Over the wall for you (No)', 'You\'re fired (No)', 'The American dream is dead (No)',
             'Nobody builds walls better than me (No)', 'Very stupid people (No)']
        ],
        "colors": [0x00E676, 0xF9A825, 0xFF5252],
        "gifs": [
            ['https://media.giphy.com/media/l2JhIUyUs8KDCCf3W/giphy.gif',
             'https://media.giphy.com/media/z48aJruaX0Jsk/giphy.gif', 'https://media.giphy.com/media/rzKSHEMN0lVkc/giphy.gif'],
            ['https://media.giphy.com/media/ASzK5wWjMtc6A/giphy.gif', 'https://media.giphy.com/media/xT8qBvVrX0wuuItpFm/giphy.gif',
             'https://media.giphy.com/media/jSB2l4zJ82Rvq/giphy.gif', 'https://media.giphy.com/media/ySFtYLc51D3pK/giphy.gif'],
            ['https://media.giphy.com/media/3o7TKWDGfvUWb9FMZi/giphy.gif', 'https://media.giphy.com/media/SvuRLwWT0EoeErwPvB/giphy.gif',
             'https://media.giphy.com/media/3o7TKJgfPhqcck8elO/giphy.gif', 'https://media.giphy.com/media/3NbTERnmPrcoE/giphy.gif']
        ]
    },
    "cat": {
        "name": 'An Cat',
        "thinkingGif": 'https://media1.tenor.com/images/e4d613ee59e79b93e38ec2521cce19e4/tenor.gif?itemid=5751430',
        "responses": [
            ['Meow'],
            ['Meow'],
            ['Meow']
        ],
        "colors": [0x00E676, 0xF9A825, 0xFF5252],
        "gifs": [
            ['https://media.giphy.com/media/14xfuigYwofmYo/giphy.gif',
             'https://media.giphy.com/media/Qo6Jvmp6kZD2g/giphy.gif'],
            ['https://media.giphy.com/media/5LU6ZcEGBbhVS/giphy.gif',
             'https://media.giphy.com/media/eJcP1uIEyDKmc/giphy.gif'],
            ['https://media.giphy.com/media/3oEduZp1fVTtaOuTyU/giphy.gif',
             'https://media.giphy.com/media/rCxogJBzaeZuU/giphy.gif']
        ]
    }
}


class FunCog(commands.Cog, name='Fun'):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name='8ball',
                      usage='[type or "types"] <question>',
                      aliases=('ami', 'ask'),
                      description='Types: ' + ", ".join(ers.keys()),
                      brief='Ask the magic 8ball a question and find out the answer to your future')
    @commands.cooldown(1, 2, type=commands.BucketType.channel)
    @commands.max_concurrency(1, per=commands.BucketType.user, wait=False)
    async def eightball(self, ctx, rtype, *question):
        if (rtype == 'types'):
            return await ctx.send(embed=self.bot.api.info_embed(f'Types: {", ".join(ers.keys())}'))
        question = " ".join(
            question) if rtype in ers else f'{rtype} {" ".join(question)}'
        category = rtype if rtype in ers else "normal"
        decision = random.randint(0, 2)
        answer = ers[category]["responses"][decision][random.randint(
            0, len(ers[category]['responses'][decision]) - 1)]
        colour = ers[category]["colors"][decision]
        think_gif = ers[category]["thinkingGif"]
        gif = ers[category]["gifs"][decision][random.randint(
            0, len(ers[category]['gifs'][decision]) - 1)]
        who = ers[category]["name"]
        msg = await ctx.send(embed=discord.Embed(
            description=f'{question}\n\n{who} is thinking...',
            colour=self.bot.api.colours["bot"])
            .set_author(name=f'{str(ctx.author)} asks', icon_url=ctx.author.avatar_url_as())
            .set_image(url=think_gif))
        await asyncio.sleep(2.5)
        await msg.edit(embed=discord.Embed(
            description=f'{question}\n\n{who} says: {answer}',
            colour=colour)
            .set_author(name=f'{str(ctx.author)} asks', icon_url=ctx.author.avatar_url_as())
            .set_image(url=gif))



def setup(bot):
    bot.add_cog(FunCog(bot))
