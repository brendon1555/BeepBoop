import os
import json
import math
import random
import asyncio
import copy
from datetime import datetime
from discord.ext import commands
from discord import Embed, utils
from beepboop.base import Base, Checks


class Spyfall(Base):

    def __init__(self, bot):
        super().__init__()
        self.bot = bot
        self.locations_file = "spyfall_locations.json"
        self.players = {}
        self.votes = {}
        self.spy = None
        self.location = None
        self._game_data = None
        self.location_list = []
        self.game_running = False
        self.start_time = None
        self.channel = None

        self._load_data()

    @property
    def majority(self):
        return math.floor(len(self.players)/2)+1

    def _load_data(self):
        """Step one
        """
        locations_file_path = os.path.join(self.text_directory, self.locations_file)
        if os.path.exists(locations_file_path):
            with open(locations_file_path, 'r') as locations_file:
                self._game_data = json.load(locations_file)
        else:
            print("Shits broke")

    def _assign_location(self):
        """Step two
        """
        self.location = random.choice(list(self._game_data.keys()))
    
    async def _assign_roles(self):
        """Step three
        """
        self.spy = random.choice(list(self.players.keys()))
        role_list_clone = copy.copy(list(self._game_data[self.location]))
        for player in self.players.keys():
            if player is not self.spy:
                if len(role_list_clone) == 0:
                    role_list_clone = copy.copy(list(self._game_data[self.location]))
                role = role_list_clone.pop(random.randint(0,len(role_list_clone)-1))
                self.players[player]["role"] = role
                await player.send("Location: {}\nRole: {}\nTo get the full list of locations send: !!sf locations".format(
                                self.location, role))
            else:
                self.players[player]["role"] = "Spy"
                await player.send("You are the spy!\nTo get the full list of locations send: !!sf locations")

    def get_locations(self):
        del self.location_list[:]
        for i in range(len(self._game_data['locations'])):
            self.location_list.append(self._game_data['locations'][i]['Location'])

    def purge(self):
        self.players = {}
        self.votes = {}
        self.location = None
        self.spy = None

        if self.game_timer:
            self.game_timer.cancel()

    
    @commands.group()
    async def sf(self, ctx):
        if ctx.invoked_subcommand is None:
            await ctx.send('Invalid Spyfall command')

    @sf.command(name='status')
    async def status(self, ctx):
        current_players = "Current Players {}.\n{}".format(len(self.players),
                          ", ".join([player.display_name for player in self.players.keys()]))
        if self.game_running:
            await ctx.send("Game is active. {}".format(current_players))
        else:
            await ctx.send("Game is not active. {}".format(current_players))

    @sf.command(name='start')
    async def start_game(self, ctx, time: int = None):
        if len(self.players) < 1:
            await ctx.send("Cannot start with less than 3 players!")
            return

        self.start_time = datetime.now()
        self.channel = ctx.channel
        starting_player = random.choice(list(self.players.keys()))
        await ctx.send("Attention {} !".format(" ".join([player.mention for player in self.players.keys()])))
        await ctx.send("Starting game with {} players! Majority is {} votes.\nFirst Up: {}.".format(
                           len(self.players), self.majority, starting_player.mention))

        self._assign_location()
        await self._assign_roles()
        self.game_running = True
        if time is None:
            time = 15
        self.game_timer = self.bot.loop.call_later(time*60, lambda: asyncio.ensure_future(ctx.invoke(self.end_game), loop=self.bot.loop))


    @sf.command(name='end')
    async def end_game(self, ctx):
        if self.game_running:
            end_time = datetime.now()
            await ctx.send("Game ended! Game lasted {} minutes.".format(math.floor((end_time-self.start_time).seconds/60)))
            await ctx.send(f"{self.spy.mention} was the Spy!")
            self.game_running = False
            self.purge()
        else:
            await ctx.send("Game has not started!")

    @commands.check(Checks.is_owner)
    @sf.command(name='clear')
    async def clear_game(self, ctx):
        if not self.game_running:
            self.purge()
            await ctx.send("Game purged")
        else:
            await ctx.send("Game is running!")

    @sf.command(name='join')
    async def join_player(self, ctx):
        if self.game_running:
            await ctx.send("Cannot join game. Game already started.")
            return
        if ctx.author in self.players.keys():
            await ctx.send(f"{ctx.author.mention}, you have already joined.")
            return

        self.players[ctx.author] = {}
        await ctx.send(f"{ctx.author.mention} has joined the game.")

    @sf.command(name='leave')
    async def leave_player(self, ctx):
        if self.game_running:
            await ctx.send("Cannot leave an active game")
        
        if ctx.author not in self.players:
            await ctx.send("You're not in the game!")
            return
        
        self.players.pop(ctx.author, None)
        await ctx.send("Removed {} from the game!".format(ctx.author.mention))

    @commands.has_any_role("Moderator", "Admin")
    @sf.command(name='kick')
    async def kick_player(self, ctx, name):
        if self.game_running:
            await ctx.send("Cannot kick from an active game")
            return

        player_to_kick = utils.get(ctx.guild.members, mention=name)

        if player_to_kick is None:
            await ctx.send(f"{name} is not a valid User.")
            return
        
        if player_to_kick not in self.players:
            await ctx.send("That user is not in the game!")
            return

        self.players.pop(player_to_kick, None)
        await ctx.send(f"Removed {player_to_kick.mention} from the game!")

    @sf.command(name='locations')
    async def locations(self, ctx):
        await ctx.send("Locations:\n{}".format("\n".join(self._game_data.keys())))


    @sf.command(name='vote')
    async def vote(self, ctx, name):
        if not self.game_running:
            await ctx.send("Cannot vote when no game is active!")
            return

        if ctx.author not in self.players.keys():
            await ctx.send(f"{ctx.author.mention}, you're not even playing...")
            return

        await ctx.invoke(self.unvote)

        player_to_vote_for = utils.get(ctx.guild.members, mention=name)

        voted = next(p for p in self.players if p == player_to_vote_for)

        if voted:
            try:
                self.votes[voted].append(ctx.author)
            except KeyError:
                self.votes[voted] = []
                self.votes[voted].append(ctx.author)
            
            voted_msg = f"{ctx.author.mention} has voted for {voted.mention}"

            if len(self.votes[voted]) >= self.majority:
                if voted is self.spy:
                    await ctx.send(f"{voted_msg}\nThey were the spy!")
                else:
                    await ctx.send(f"{voted_msg}\nNope, they weren't the spy. Everyone but {self.spy.mention} loses!")

                await ctx.invoke(self.end_game)
            else:
                await ctx.send(f"{voted_msg} (That makes {len(self.votes[voted])} votes! {self.majority - len(self.votes[voted])} till majority)")
            
    @sf.command(name='unvote')
    async def unvote(self, ctx, name):
        if not self.game_running:
            await ctx.send("Cannot vote when no game is active!")
            return

        if ctx.author not in self.players.keys():
            await ctx.send(f"{ctx.author.mention}, you're not even playing...")
            return

        current_vote = None
        for voted in self.votes.keys():
            try:
                idx = self.votes[voted].index(ctx.author)
                self.votes[voted].pop(idx)
                current_vote = voted
                break
            except ValueError:
                pass

        if current_vote:
            await ctx.send(f"{ctx.author.mention} is no longer voting for {voted.mention}")
        else:
            await ctx.send(f"Cannot unvote, {ctx.author.mention} are not voting for anyone")

    @sf.command(name='votes')
    async def get_votes(self, ctx):
        if not self.game_running:
            await ctx.send("Game not started, cannot get votes")
            return

        text = f"Current Votes (Majority is {self.majority}):\n"
        for player in sorted(self.votes.keys(), key=lambda x: len(self.votes[x]), reverse=True):
            if len(self.votes[player]) > 0:
                player_names = ",".join([p.username for p in self.votes[player]])
                text += f"{player.mention} ({len(self.votes[player])}): {player_names}\n"
        await ctx.send(text)

    @sf.command(name='location')
    async def declare_location(self, ctx, *, location):
        if not location:
            await ctx.send("Need to provide a location name")

        if ctx.author != self.spy:
            await ctx.author.send("You're not even the spy.")
        else:
            if self.location.lower() == location.lower():
                await self.channel.send(f"{ctx.author.mention} was the spy. They have correctly declared the location as {self.location}\nThey win!")
            else:
                await self.channel.send(f"{ctx.author.mention} was the spy but they have incorrectly declared the location as {location}\nThey lose!")
            await ctx.invoke(self.end_game)
        

def setup(bot):
    bot.add_cog(Spyfall(bot))
