import discord
from discord.ext import commands
from beepboop.cogs.music import Music
from beepboop.cogs.jokes import Jokes
from beepboop.cogs.gifs import Gifs
from beepboop.cogs.utils import Utils

bot = commands.Bot(command_prefix=commands.when_mentioned_or('!!'), description='Beep Boop')
bot.add_cog(Music(bot))
bot.add_cog(Jokes(bot))
bot.add_cog(Gifs(bot))
bot.add_cog(Utils(bot))

@bot.event
async def on_ready():
    print('Logged in as:\n{0} (ID: {0.id})'.format(bot.user))
    await bot.change_presence(game=discord.Game(name='[Alpha 0.0.3]'))


@bot.event
async def on_member_join(member):
    server = member.server
    fmt = '@{} who dis?!'
    await bot.send_message(server, fmt.format(member))

if __name__ == "__main__":
    bot.run('MTkwNDI0OTM0ODc3NjI2MzY4.DEJOyw.h33o0TCgJFZjpIV7b_Tg5FxLYdA')
