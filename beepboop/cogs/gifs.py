from discord.ext import commands
import giphypop
from beepboop.base import Base, _CONFIG


class Gifs(Base):

    def __init__(self, bot):
        super().__init__()
        self.bot = bot
        self.giphy = giphypop.Giphy(api_key=_CONFIG['giphy_api_key'])

    @commands.command(pass_context=True, no_pm=True)
    async def cat(self, ctx):
        """Sends a random 'cute cat' gif"""
        await self._get_gif(ctx, "cute cat")

    @commands.command(pass_context=True, no_pm=True)
    async def come(self, ctx):
        """Sends a random 'come over' gif"""
        await self._get_gif(ctx, "come over")

    @commands.command(pass_context=True, no_pm=True)
    async def gif(self, ctx, *, tags=None):
        """Sends a random gif for the given tags"""
        if tags is None:
            await self.bot.say("Gotta give me some tags")
        else:
            await self._get_gif(ctx, tags)

    async def _get_gif(self, ctx, tags: str):
        tag_gif = self.giphy.random_gif(tag=tags)
        await self.bot.say(tag_gif.url)

    # async def _translate_gif(self, ctx, phrase: str):
    #     translated_gif = self.giphy.translate(phrase=phrase)
    #     await self.bot.say(translated_gif.url)

def setup(bot):
    bot.add_cog(Gifs(bot))
