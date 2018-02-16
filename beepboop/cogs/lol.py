import json
from itertools import islice
from discord.ext import commands
from discord import Embed
import cassiopeia
from cassiopeia.data import Queue
import datapipelines
from beepboop.base import typing, Base, _CONFIG, _SUMMONERS


CHAMPION_EMOJIS, SPELL_EMOJIS, BDT_EMOJIS = {}, {}, {}
UNKNOWN_EMOJI = ":grey_question:"

QueueStrings = {
    Queue.ranked_solo_fives: "Ranked Solo", 
    Queue.ranked_flex_fives: "Ranked Flex", 
    Queue.normal_draft_fives: "Draft", 
    Queue.blind_fives: "Blind", 
    Queue.depreciated_blind_fives: "Blind", 
    Queue.depreciated_draft_fives: "Draft", 
    Queue.depreciated_ranked_solo_fives: "Ranked Solo", 
    Queue.depreciated_ranked_premade_fives: "Ranked Premade", 
    Queue.depreciated_ranked_team_fives: "Ranked Team",
    Queue.depreciated_team_builder_fives: "Ranked Team Builder",
    Queue.depreciated_ranked_fives: "Ranked"
}


class Lol(Base):

    def __init__(self, bot):
        super().__init__()
        self.bot = bot
        self.cass = cassiopeia
        self.cass.apply_settings(_CONFIG['cassiopeia'])
        self.summoners = _SUMMONERS

        for key, value in _CONFIG['emojis']['champions']['id'].items():
            CHAMPION_EMOJIS[int(key)] = value
        for key, value in _CONFIG['emojis']['spells']['id'].items():
            SPELL_EMOJIS[int(key)] = value
        for color, symbols in _CONFIG['emojis']['bdt'].items():
            for symbol, value in symbols.items():
                BDT_EMOJIS[color[0] + symbol[0]] = value

    @commands.group()
    async def lol(self, ctx):
        if ctx.invoked_subcommand is None:
            await ctx.send('Invalid lol command')

    @lol.command()
    @typing
    async def status(self, ctx):
        lol_status = self.cass.get_status(region="OCE")
        em = Embed(color=0xea7938)
        em.add_field(name='Name', value=lol_status.name, inline=False)
        for service in lol_status.services:
            em.add_field(name=service.name, value=service.status)
        await ctx.send(embed=em)


    @lol.command()
    @typing
    async def champions(self, ctx):
        champions = self.cass.Champions(region="OCE")
        champions_text = '\n'.join([
            '{}'.format(champion.name)
            for champion in champions
        ])
        await ctx.send('Valid Champion names:```\n{}```'.format(champions_text))


    @lol.command()
    @typing
    async def assign_summoner(self, ctx, *, name=None):
        """Assigns a summoner to your discord user"""
        if name is None:
            await ctx.send("Gotta give me a summoner name")
        else:
            try:
                summoner = self.cass.Summoner(name=name, region="OCE")
            except datapipelines.common.NotFoundError:
                await ctx.send("No Summoner found")
                return

            self.summoners['summoners'][str(ctx.message.author.id)] = {"id": summoner.id, "accountId": summoner.account.id, "name": summoner.name}
            with open('summoners.json', 'w') as outfile:  
                json.dump(self.summoners, outfile)

            await ctx.send("Assigned summoner %s to %s" % (summoner.name, ctx.message.author.name))


    @lol.command()
    @typing
    async def summoner(self, ctx, *, name=None):
        """Sends summoner info"""
        if name is None and str(ctx.message.author.id) not in self.summoners['summoners']:
            await ctx.send("Gotta give me a summoner name or assign a summoner to yourself")
        else:
            if name is None:
                summoner = self.cass.Summoner(id=int(self.summoners['summoners'][str(ctx.message.author.id)]["id"]), region="OCE")
            else:
                try:
                    summoner = self.cass.Summoner(name=name, region="OCE")
                except datapipelines.common.NotFoundError:
                    await ctx.send("No Summoner found")
                    return

            mastery_list = [[mastery.champion.id, mastery.champion.name, mastery.level] for mastery in islice(sorted(summoner.champion_masteries, key=lambda mastery: mastery.points, reverse=True), 3)]
            top_champions_text = '\n'.join([
                '{} {} (Level: {})'.format(
                    CHAMPION_EMOJIS.get(mastery[0], UNKNOWN_EMOJI), mastery[1], mastery[2])
                for mastery in mastery_list
            ])

            em = Embed(color=0xea7938)
            em.set_author(name='Summoner Profile: %s' % summoner.name,
                        icon_url=summoner.profile_icon.url)
            em.add_field(name='Level', value=summoner.level)
            em.add_field(name='Top Champions', value=top_champions_text)
            em.set_thumbnail(url=summoner.profile_icon.url)
            await ctx.send(embed=em)
    
    @lol.command()
    @typing
    async def kda(self, ctx, *, champion_name=None):
        if str(ctx.message.author.id) not in self.summoners['summoners']:
            await ctx.send("Gotta assign a summoner to yourself before you can use this command (!!lol assign_summoner SUMMONER_NAME)")
            return

        queues = {
            Queue.ranked_solo_fives, 
            Queue.ranked_flex_fives, 
            Queue.normal_draft_fives, 
            Queue.blind_fives, 
            Queue.depreciated_blind_fives, 
            Queue.depreciated_draft_fives, 
            Queue.depreciated_ranked_solo_fives, 
            Queue.depreciated_ranked_premade_fives, 
            Queue.depreciated_ranked_team_fives,
            Queue.depreciated_team_builder_fives,
            Queue.depreciated_ranked_fives
        }

        # Overall last 10 games
        summoner = self.cass.Summoner(id=int(self.summoners['summoners'][str(ctx.message.author.id)]["id"]), region="OCE")
        if champion_name is None:
            history = self.cass.get_match_history(summoner=summoner, queues=queues, end_index=10)
        else:
            try:
                champion = self.cass.Champion(name=champion_name, region="OCE")
            except datapipelines.common.NotFoundError:
                await ctx.send("No Champion found. Try `!!lol champions`")
                return

            try:
                history = self.cass.get_match_history(summoner=summoner, champions={champion}, queues=queues, end_index=10)
            except datapipelines.common.NotFoundError:
                await ctx.send("No Champion found. Try `!!lol champions`")
                return

        if len(history) == 0:
            await ctx.send("No match history")
            return

        kills = 0
        assists = 0
        deaths = 0

        champs = []

        for match in history:

            kills += match.participants[summoner.name].stats.kills
            assists += match.participants[summoner.name].stats.assists
            deaths += match.participants[summoner.name].stats.deaths

            champ = [match.participants[summoner.name].champion, match.participants[summoner.name].stats, match]
            champs.append(champ)

        if(deaths != 0):
            kda = (kills + assists) / deaths
        else:
            kda = kills + assists


        champion_text = '\n'.join([
            '{} {} ({})'.format(
                CHAMPION_EMOJIS.get(champion_stats[0].id, UNKNOWN_EMOJI), champion_stats[0].name, QueueStrings[champion_stats[2].queue])
            for champion_stats in champs
        ])

        kda_text = '\n'.join([
            ':skull_crossbones: {}|{}|{} ({})'.format(
                champion_stats[1].kills,  champion_stats[1].deaths, champion_stats[1].assists, round(champion_stats[1].kda, 2))
            for champion_stats in champs
        ])

        em = Embed(color=0xea7938)
        em.set_author(name='KDA: %s' % summoner.name,
                    icon_url=summoner.profile_icon.url)
        em.add_field(name='Champion', value=champion_text)
        em.add_field(name='Game KDA', value=kda_text)
        em.add_field(name='Overall KDA', value=round(kda, 2),)
        em.set_thumbnail(url=summoner.profile_icon.url)
        await ctx.send(embed=em)

    
    @lol.command()
    @typing
    async def ftp(self, ctx):
        champions = self.cass.Champions(region="OCE").search(True)
        champions_text = '\n'.join([
            '{}'.format(champion.name)
            for champion in champions
        ])
        await ctx.send('Free to play:```\n{}```'.format(champions_text))


def setup(bot):
    bot.add_cog(Lol(bot))
