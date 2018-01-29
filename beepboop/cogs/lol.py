import json
from discord.ext import commands
from discord import Embed
import cassiopeia
import datapipelines
from beepboop.base import Base, _CONFIG, _SUMMONERS


class Lol(Base):

    def __init__(self, bot):
        super().__init__()
        self.bot = bot
        self.cass = cassiopeia
        self.cass.apply_settings(_CONFIG['cassiopeia'])
        self.summoners = _SUMMONERS

    @commands.command(pass_context=True, no_pm=True)
    async def assign_summoner(self, ctx, *, name=None):
        """Assigns a summoner to your discord user"""
        if name is None:
            await self.bot.say("Gotta give me a summoner name")
        else:
            try:
                summoner = self.cass.Summoner(name=name, region="OCE")
            except datapipelines.common.NotFoundError:
                await self.bot.say("No Summoner found")
                return

            self.summoners['summoners'][ctx.message.author.id] = {"id": summoner.id, "accountId": summoner.account.id, "name": summoner.name}
            with open('summoners.json', 'w') as outfile:  
                json.dump(self.summoners, outfile)

            await self.bot.say("Assigned summoner %s to %s" % (summoner.name, ctx.message.author.name))


    @commands.command(pass_context=True, no_pm=True)
    async def summoner(self, ctx, *, name=None):
        """Sends summoner info"""
        if name is None and ctx.message.author.id not in self.summoners['summoners']:
            await self.bot.say("Gotta give me a summoner name or assign a summoner to yourself")
        else:
            if name is None:
                summoner = self.cass.Summoner(id=int(self.summoners['summoners'][ctx.message.author.id]["id"]), region="OCE")
            else:
                try:
                    summoner = self.cass.Summoner(name=name, region="OCE")
                except datapipelines.common.NotFoundError:
                    await self.bot.say("No Summoner found")
                    return

            if self.embed_perms(ctx.message):
                em = Embed(color=0xea7938)
                em.add_field(name='Name', value=summoner.name)
                em.add_field(name='Level', value=summoner.level)
                em.add_field(name='ID', value=summoner.id)
                em.add_field(name='Account ID', value=summoner.account.id)
                em.set_author(name='Summoner',
                            icon_url=summoner.profile_icon.url)
                em.set_thumbnail(url=summoner.profile_icon.url)
                await self.bot.send_message(ctx.message.channel, embed=em)
            else:
                msg = '**Summoner:** ```Name: %s\nLevel: %s\nID: %s\nAccount ID: %s\nProfile icon URL: %s```' % (
                    summoner.name, summoner.level, summoner.id, summoner.account.id, summoner.profile_icon.url)
                await self.bot.SAY(msg)


def setup(bot):
    bot.add_cog(Lol(bot))
