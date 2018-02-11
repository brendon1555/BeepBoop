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

        player_to_kick = utils.get(ctx.guild.members, name=name)

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


def setup(bot):
    bot.add_cog(Spyfall(bot))
