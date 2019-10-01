from discord.ext import commands
import giphypop
from beepboop.base import Base


class Gifs(Base):

    def __init__(self, bot):
        super().__init__()
        self.bot = bot
        self.giphy = giphypop.Giphy(api_key=self.bot.config['giphy_api_key'])

    @commands.command()
    async def cat(self, ctx):
        """Sends a random 'cute cat' gif"""
        await self._get_gif(ctx, "cute cat")

    @commands.command()
    async def come(self, ctx):
        """Sends a random 'come over' gif"""
        await self._get_gif(ctx, "come over")

    @commands.command()
    async def gif(self, ctx, *, tags=None):
        """Sends a random gif for the given tags"""
        if tags is None:
            await ctx.send("Gotta give me some tags")
        else:
            await self._get_gif(ctx, tags)

    async def _get_gif(self, ctx, tags: str):
        tag_gif = self.giphy.random_gif(tag=tags)
        await ctx.send(tag_gif.url)

    # async def _translate_gif(self, ctx, phrase: str):
    #     translated_gif = self.giphy.translate(phrase=phrase)
    #     await ctx.send(translated_gif.url)

def setup(bot):
    bot.add_cog(Gifs(bot))
