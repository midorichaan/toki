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
        usage="ticket [args]"
    )
    async def _ticket(self, ctx):
        if ctx.invoked_subcommand is None:
            return await utils.reply_or_send(ctx, content="> `.ticket help` でヘルプを参照してね！")

    #ticket help
    @_ticket.command(
        name="help",
        description="チケットのヘルプを表示するよ！"
        usage="ticket help [command]"
    )
    async def _help(self, ctx, command: str=None):
        m = await utils.reply_or_send(ctx, content="> 処理中...")
        e = discord.Embed(title="Ticket Help", timestamp=ctx.message.created_at)

        if command:
            ticket = self.bot.get_command("ticket")
            cmd = ticket.get_command(command)
            if cmd:
                e.title = f"Ticket help - {command}"
                e.add_field(name="使用法", value=cmd.usage or "なし")
                e.add_field(name="エイリアス", value=", ".join([f"`{row}`" for row in cmd.aliases]) or "なし")
                e.add_field(name="説明", value=f"```\n{cmd.description}\n```" or "```\n説明なし\n```", inline=False)
            else:
                return await m.edit(content=f"> `{command}` というコマンドは存在しないよ！")
        else:
            for i in ticket.commands:
                e.add_field(name=i.name, value=i.description or "説明なし")
        return await m.edit(content=None, embed=e)

async def setup(bot):
    await bot.add_cog(mido_ticket(bot))
