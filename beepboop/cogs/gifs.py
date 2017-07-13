from discord.ext import commands
import giphypop
from beepboop import Base


class Gifs(Base):

    def __init__(self, bot):
        super().__init__()
        self.bot = bot
        self.giphy = giphypop.Giphy(api_key='06cd30fabde14aea88100bd363205073')

    @commands.command(pass_context=True, no_pm=True)
    async def cat(self, ctx):
        cat_gif = self.giphy.random_gif(tag="cute cat")
        await self.bot.say(cat_gif.url)

    @commands.command(pass_context=True, no_pm=True)
    async def come(self, ctx):
        come_gif = self.giphy.random_gif(tag="come over")
        await self.bot.say(come_gif.url)

    @commands.command(pass_context=True, no_pm=True)
    async def gif(self, ctx, *, tags=None):
        if tags is None:
            await self.bot.say("Gotta give some tags")
        else:
            tag_gif = self.giphy.random_gif(tag=tags)
            await self.bot.say(tag_gif.url)
