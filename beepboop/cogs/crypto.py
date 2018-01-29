from discord.ext import commands
from discord import Embed
from coinmarketcap import Market
from beepboop.base import Base

class Crypto(Base):

    def __init__(self, bot):
        super().__init__()
        self.bot = bot
        self.market = Market()

    @commands.command(pass_context=True, no_pm=True)
    async def crypto(self, ctx, *, currency=None):
        """Sends a random gif for the given tags"""
        if currency is None:
            await self.bot.say("Gotta give me a currency")
        else:
            try:
                await self._get_currency(ctx, currency)
            except KeyError:
                await self.bot.say("Not a valid crypto")

    async def _get_currency(self, ctx, currency: str):
        ticker = self.market.ticker(currency, convert='AUD')
        # await self.bot.say(ticker[0]['price_aud'])
        if self.embed_perms(ctx.message):
            em = Embed(color=0xea7938)
            em.add_field(name='Currency', value=ticker[0]['name'])
            em.add_field(name='Symbol', value=ticker[0]['symbol'], inline=False)
            em.add_field(name='Change 1h', value="{}%".format(ticker[0]['percent_change_1h']))
            em.add_field(name='Change 24h', value="{}%".format(ticker[0]['percent_change_24h']))
            em.add_field(name='Change 7d', value="{}%".format(ticker[0]['percent_change_7d']))
            em.add_field(name='Price AUD', value="${}".format(ticker[0]['price_aud']), inline=False)
            em.set_author(name='Crypto',
                          icon_url='https://i.imgur.com/RHagTDg.png')
            em.set_footer(text='Provided by: https://coinmarketcap.com')
            await self.bot.send_message(ctx.message.channel, embed=em)
        else:
            msg = '**Crypto:** ```Currency: %s\nSymbol: %s\nChange 1h: %s%%\nChange 24h: %s%%\nChange 7d: %s%%\nPrice AUD: $%s```' % (
                ticker[0]['name'], ticker[0]['symbol'], ticker[0]['percent_change_1h'], ticker[0]['percent_change_24h'], ticker[0]['percent_change_7d'], ticker[0]['price_aud'])
            await self.bot.say(msg)

    # async def _translate_gif(self, ctx, phrase: str):
    #     translated_gif = self.giphy.translate(phrase=phrase)
    #     await self.bot.say(translated_gif.url)

def setup(bot):
    bot.add_cog(Crypto(bot))
