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
        await self._get_gif(ctx, "cute cat")

    @commands.command(pass_context=True, no_pm=True)
    async def come(self, ctx):
        await self._get_gif(ctx, "come over")

    @commands.command(pass_context=True, no_pm=True)
    async def gif(self, ctx, *, tags=None):
        if tags is None:
            await self.bot.say("Gotta give some tags")
        else:
            await self._get_gif(ctx, tags)

    async def _get_gif(self, ctx, tags: str):
        tag_gif = self.giphy.random_gif(tag=tags)
        await self.bot.say(tag_gif.url)


def setup(bot):
    bot.add_cog(Gifs(bot))
