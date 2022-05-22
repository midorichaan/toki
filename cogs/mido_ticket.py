import discord
from discord.ext import commands

from lib import utils, ticketutils

class mido_ticket(commands.Cog):

    def __init__(self, bot):
        self.bot = bot
        self.ticketutil = ticketutils.TicketUtils(bot)

    #ticket
    @commands.group(
        name="ticket",
        description="チケット関連のコマンドです"
    )
    async def _ticket(self, ctx):
        pass

async def setup(bot):
    await bot.add_cog(mido_ticket(bot))
