import discord
from discord.ext import commands

from lib import utils, ticketutils

class mido_ticket(commands.Cog):

    def __init__(self, bot):
        self.bot = bot
        self.ticketutil = ticketutils.TicketUtils(bot)

    #_check_permission
    def _chech_permission(self, member: discord.Member) -> bool:
        perms = dict(member.guild_permissions)
        val = True

        if not perms.manage_channels:
            val = False
        if not perms.manage_messages:
            val = False
        if not perms.manage_permissions:
            val = False
        return val

    #ticket
    @commands.group(
        name="ticket",
        description="チケット関連のコマンドです",
        usage="ticket [args]"
    )
    async def _ticket(self, ctx):
        if ctx.invoked_subcommand is None:
            return await utils.reply_or_send(ctx, content="> `.ticket help` でヘルプを参照してね！")

    #ticket help
    @_ticket.command(
        name="help",
        description="チケットのヘルプを表示するよ！",
        usage="ticket help [command]"
    )
    async def _help(self, ctx, command: str=None):
        m = await utils.reply_or_send(ctx, content="> 処理中...")
        e = discord.Embed(title="Ticket Help", timestamp=ctx.message.created_at)

        ticket = self.bot.get_command("ticket")
        if command:
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

    #ticket create
    @_ticket.command(
        name="create",
        description="チケットを作成します。",
        usage="ticket create [reason]"
    )
    async def _create(self, ctx, *, reason: str=None):
        m = await utils.reply_or_send(ctx, content="> 処理中...")

        cp = self._check_permission(ctx.guild.me)
        if not cp:
            return await m.edit(content="> Botの権限が不足しているよ！")

        try:
            channel = await self.ticketutil.create_ticket_channel(
                ctx.guild.id, ctx.author.id
            )
            await self.ticketutil.create_ticket(
                channel, panel[0], panel[1]
            )
        except Exception as exc:
            if ctx.author.id in self.bot.owner_ids:
                return await m.edit(
                    content=f"> エラー \n```py\n{exc}\n```"
                )
            else:
                return await m.edit(
                    content="> チケット作成中にエラーが発生しました。"
                )
        else:
            return await m.edit(
                content=f"> チケットを作成しました！ \n→ {channel.mention}"
            )

async def setup(bot):
    await bot.add_cog(mido_ticket(bot))
