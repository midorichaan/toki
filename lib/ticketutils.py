import discord
from functools import wraps

class TicketUtils:

    def __init__(self, bot):
        self.bot = bot
        self.emoji_dict = {
            "x": "❌",
            "mail": "📩"
        }

    """
    データベース構造
    - tickets : チケットチャンネルの情報
      - ticket_id : チケットチャンネルID, プライマリキー, int
      - ticket_panel_id : チケットパネルID, int
      - guild_id : ギルドID, int
      - author_id : 作成者ID, int
      - created_at : 作成日, strのtimestamp
      - status : チケットステータス, int

    - ticketconfig : チケット関連の設定
      - guild_id : ギルドID, プライマリキー, int
      - open_category_id : チケットを作成するカテゴリID, int
      - close_category_id : クローズチケットを移動するカテゴリID, int
      - auto_archive : 自動チケットアーカイブ, int
      - auto_delete : 自動チケット削除, int
      - mention_created : チケット作成時にメンションするか, int

    - ticketpanels : チケットパネルの情報
      - panel_id : パネルのID, プライマリキー, int
      - guild_id : ギルドID, int
      - channel_id : チャンネルID, int
      - created_at : 作成日, strのtimestamp
    """

    #create_ticket_panel
    def create_ticket_panel(
        self, *, title: str="Ticket Panel", description: str="リアクションをクリックするとチケットが作成されます", color: int=None
    ) -> discord.Embed:
        embed = discord.Embed(title=title, description=description, color=color)
        return embed

    #create_control_panel
    def create_control_panel(self, *, status: int=0, color: int=None, reason: str=None) -> discord.Embed:
        embed = discord.Embed(title=f"Ticket - {author}", color=color)

        if status == 0:
            embed.add_field(name="ステータス / Status", value="```\n理由入力待ち / Waiting for input reason \n```", inline=False)
            embed.add_field(name="作成理由 / Reason", value="```\n理由入力待ち / Waiting for input reason \n```", inline=False)
        elif status == 1:
            embed.add_field(name="ステータス / Status", value="```\nオープン / Open \n```", inline=False)
            embed.add_field(name="作成理由 / Reason", value=f"```\n{reason} \n```", inline=False)
        elif status == 2:
            embed.add_field(name="ステータス / Status", value="```\nクローズ / Close \n```", inline=False)
            embed.add_field(name="作成理由 / Reason", value=f"```\n*** クローズ / Closed *** \n```", inline=False)
        return embed

    #create_panel
    async def create_panel(
        self, channel: discord.TextChannel, title: str=None, description: str=None, color: int=None
    ) -> discord.Message:
        embed = self.create_ticket_panel(title, description, color)
        msg = await channel.send(embed=embed)

        await self.bot.execute(
            "INSERT INTO ticketpanels VALUES(%s, %s, %s, %s)",
            (msg.id, channel.guild.id, channel.id, str(msg.created_at))
        )
        return msg

    #create_ticket
    async def create_ticket(
        self, ticket: discord.TextChannel, author: int=None, status: int=0, reason: str=None
    ) -> discord.Message:
        embed = self.create_control_panel(status=status, reason=reason)
        panel = await ticket.send(embed=embed)
        await panel.add_reaction(self.emoji_dict["x"])

        await self.bot.execute(
            "INSERT INTO tickets(%s, %s, %s, %s, %s, %s)", 
            (ticket.id, panel.id, ticket.guild.id, author.id, str(ticket.created_at), 0)
        )
        return panel

    #delete_panel
    async def delete_panel(self, panel_id: int) -> None:
        db = await self.bot.db.fetchone("SELECT * FROM ticketpanels WHERE panel_id=%s", (panel_id,))
        if db:
            await self.bot.db.execute("DELETE FROM ticketpanels WHERE panel_id=%s", (panel_id,))

            try:
                msg = await self.bot.get_channel(db["channel_id"]).fetch_message(panel_id)
                await msg.delete()
            except:
                return

    #delete_ticket
    async def delete_ticket(self, ticket_id: int) -> None:
        db = await self.bot.db.fetchone("SELECT * FROM tickets WHERE ticket_id=%s", (ticket_id,))
        if db:
            await self.bot.db.execute("DELETE FROM tickets WHERE ticket_id=%s", (ticket_id,))

            try:
                await self.bot.get_channel(db["channel_id"]).delete()
            except:
                return

    #archive_ticket
    async def archive_ticket(self, ticket_id: int, guild_id: int) -> None:
        db = await self.bot.db.fetchone("SELECT * FROM tickets WHERE ticket_id=%s", (ticket_id,))
        if db:
            config = await self.bot.db.fetchone("SELECT * FROM ticketconfig WHERE guild_id=%s", (guild_id,))
            channel = self.bot.get_channel(config["close_category_id"])
            ticket = self.bot.get_channel(ticket_id)
            if channel and isinstance(channel, discord.CategoryChannel):
                try:
                    await ticket.edit(category=channel)
                except:
                    return

    #refresh_panel
    async def refresh_panel(
        self, panel_id: int, title: str=None, description: str=None, color: int=None
    ) -> discord.Message:
        db = await self.bot.db.fetchone("SELECT * FROM ticketpanels WHERE panel_id=%s", (panel_id,))
        if db:
            embed = self.create_ticket_panel(title, description, color)

            try:
                msg = await self.bot.get_channel(db["channel_id"]).fetch_message(panel_id)
                await msg.edit(embed=embed)
            except:
                return

    #init_database
    async def init_database(self) -> None:
        query = [
            "CREATE TABLE IF NOT EXISTS tickets(ticket_id BIGINT PRIMARY KEY NOT NULL, ticket_panel_id BIGINT, guild_id BIGINT, author_id BIGINT, created_at TEXT, status INTEGER)",
            "CREATE TABLE IF NOT EXISTS ticketconfig(guild_id BIGINT PRIMARY KEY NOT NULL, open_category_id BIGINT, close_category_id BIGINT, auto_archive INTEGER, auto_delete INTEGER, mention_created INTEGER)",
            "CREATE TABLE IF NOT EXISTS ticketpanels(panel_id BIGINT PRIMARY KEY NOT NULL, guild_id BIGINT, channel_id BIGINT, created_at TEXT)"
        ]

        for i in query:
            try:
                await self.bot.db.execute(i)
            except Exception as exc:
                pass