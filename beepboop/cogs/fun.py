from discord.ext import commands
from random import choice, randint
from beepboop import Base
import discord


class Fun(Base):

    def __init__(self, bot):
        super().__init__()
        self.bot = bot
        self.ball = ['It is certain', 'It is decidedly so', 'Without a doubt', 'Yes definitely', 'You may rely on it',
                     'As I see it, yes', 'Most likely', 'Outlook good', 'Yes', 'Signs point to yes',
                     'Reply hazy try again',
                     'Ask again later', 'Better not tell you now', 'Cannot predict now', 'Concentrate and ask again',
                     'Don\'t count on it', 'My reply is no', 'My sources say no', 'Outlook not so good',
                     'Very doubtful']
        self.regionals = {'a': '\N{REGIONAL INDICATOR SYMBOL LETTER A}', 'b': '\N{REGIONAL INDICATOR SYMBOL LETTER B}',
                          'c': '\N{REGIONAL INDICATOR SYMBOL LETTER C}',
                          'd': '\N{REGIONAL INDICATOR SYMBOL LETTER D}', 'e': '\N{REGIONAL INDICATOR SYMBOL LETTER E}',
                          'f': '\N{REGIONAL INDICATOR SYMBOL LETTER F}',
                          'g': '\N{REGIONAL INDICATOR SYMBOL LETTER G}', 'h': '\N{REGIONAL INDICATOR SYMBOL LETTER H}',
                          'i': '\N{REGIONAL INDICATOR SYMBOL LETTER I}',
                          'j': '\N{REGIONAL INDICATOR SYMBOL LETTER J}', 'k': '\N{REGIONAL INDICATOR SYMBOL LETTER K}',
                          'l': '\N{REGIONAL INDICATOR SYMBOL LETTER L}',
                          'm': '\N{REGIONAL INDICATOR SYMBOL LETTER M}', 'n': '\N{REGIONAL INDICATOR SYMBOL LETTER N}',
                          'o': '\N{REGIONAL INDICATOR SYMBOL LETTER O}',
                          'p': '\N{REGIONAL INDICATOR SYMBOL LETTER P}', 'q': '\N{REGIONAL INDICATOR SYMBOL LETTER Q}',
                          'r': '\N{REGIONAL INDICATOR SYMBOL LETTER R}',
                          's': '\N{REGIONAL INDICATOR SYMBOL LETTER S}', 't': '\N{REGIONAL INDICATOR SYMBOL LETTER T}',
                          'u': '\N{REGIONAL INDICATOR SYMBOL LETTER U}',
                          'v': '\N{REGIONAL INDICATOR SYMBOL LETTER V}', 'w': '\N{REGIONAL INDICATOR SYMBOL LETTER W}',
                          'x': '\N{REGIONAL INDICATOR SYMBOL LETTER X}',
                          'y': '\N{REGIONAL INDICATOR SYMBOL LETTER Y}', 'z': '\N{REGIONAL INDICATOR SYMBOL LETTER Z}',
                          '0': '0⃣', '1': '1⃣', '2': '2⃣', '3': '3⃣',
                          '4': '4⃣', '5': '5⃣', '6': '6⃣', '7': '7⃣', '8': '8⃣', '9': '9⃣', '!': '\u2757',
                          '?': '\u2753'}

    @commands.command(pass_context=True, no_pm=True, aliases=['8ball'])
    async def ball8(self, ctx, *, msg: str):
        answer = randint(0, 19)
        if self.embed_perms(ctx.message):
            if answer < 10:
                colour = 0x008000
            elif 10 <= answer < 15:
                colour = 0xFFD700
            else:
                colour = 0xFF0000
            em = discord.Embed(color=colour)
            em.add_field(name='\u2753 Question', value=msg)
            em.add_field(name='\ud83c\udfb1 8ball', value=self.ball[answer], inline=False)
            await self.bot.say(embed=em)
        else:
            await self.bot.say('\ud83c\udfb1 ``{}``'.format(choice(self.ball)))

    @commands.command(pass_context=True, no_pm=True, aliases=['choose'])
    async def pick(self, ctx, *, msg: str):
        """Picks randomly from the options provided separated by |"""
        await self.bot.say('I choose: {}'.format(choice(msg.split("|"))))

    @commands.command(pass_context=True, no_pm=True)
    async def big(self, ctx, *, msg):
        """Replace letters with emojis"""
        msg = list(msg)
        regional_list = [self.regionals[x.lower()] if x.isalnum() or x == '!' or x == '?' else x for x in msg]
        regional_output = '  '.join(regional_list)
        await self.bot.send_message(ctx.message.channel, regional_output)


def setup(bot):
    bot.add_cog(Fun(bot))
