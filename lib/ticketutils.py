import discord
from functools import wraps

class TicketUtils:

    def __init__(self, bot):
        self.bot = bot
        self.emoji_dict = {
            "x": "â",
            "mail": "ð©"
        }

    """
    ãã¼ã¿ãã¼ã¹æ§é 
    - tickets : ãã±ãããã£ã³ãã«ã®æå ±
      - ticket_id : ãã±ãããã£ã³ãã«ID, ãã©ã¤ããªã­ã¼, int
      - ticket_panel_id : ãã±ããããã«ID, int
      - guild_id : ã®ã«ãID, int
      - author_id : ä½æèID, int
      - created_at : ä½ææ¥, strã®timestamp
      - status : ãã±ããã¹ãã¼ã¿ã¹, int

    - ticketconfig : ãã±ããé¢é£ã®è¨­å®
      - guild_id : ã®ã«ãID, ãã©ã¤ããªã­ã¼, int
      - open_category_id : ãã±ãããä½æããã«ãã´ãªID, int
      - close_category_id : ã¯ã­ã¼ãºãã±ãããç§»åããã«ãã´ãªID, int
      - auto_archive : èªåãã±ããã¢ã¼ã«ã¤ã, int
      - auto_delete : èªåãã±ããåé¤, int
      - mention_created : ãã±ããä½ææã«ã¡ã³ã·ã§ã³ããã, int
      - panel_title : ããã«ã®ã¿ã¤ãã«
      - panel_description : ããã«ã®èª¬æ

    - mentionable_roles : ã¡ã³ã·ã§ã³ããã­ã¼ã«
      - guild_id : ã®ã«ãID, ãã©ã¤ããªã­ã¼, int
      - role_id : ã­ã¼ã«ID, int

    - ticketpanels : ãã±ããããã«ã®æå ±
      - panel_id : ããã«ã®ID, ãã©ã¤ããªã­ã¼, int
      - guild_id : ã®ã«ãID, int
      - channel_id : ãã£ã³ãã«ID, int
      - created_at : ä½ææ¥, strã®timestamp
    """

    #create_ticket_panel
    def create_ticket_panel(
        self, *, title: str="Ticket Panel", description: str="ãªã¢ã¯ã·ã§ã³ãã¯ãªãã¯ããã¨ãã±ãããä½æããã¾ã", color: int=None
    ) -> discord.Embed:
        embed = discord.Embed(title=title, description=description, color=color)
        return embed

    #create_control_panel
    def create_control_panel(self, *, status: int=0, color: int=None, reason: str=None) -> discord.Embed:
        embed = discord.Embed(title=f"Ticket - {author}", color=color)

        if status == 0:
            embed.add_field(name="ã¹ãã¼ã¿ã¹ / Status", value="```\nçç±å¥åå¾ã¡ / Waiting for input reason \n```", inline=False)
            embed.add_field(name="ä½æçç± / Reason", value="```\nçç±å¥åå¾ã¡ / Waiting for input reason \n```", inline=False)
        elif status == 1:
            embed.add_field(name="ã¹ãã¼ã¿ã¹ / Status", value="```\nãªã¼ãã³ / Open \n```", inline=False)
            embed.add_field(name="ä½æçç± / Reason", value=f"```\n{reason} \n```", inline=False)
        elif status == 2:
            embed.add_field(name="ã¹ãã¼ã¿ã¹ / Status", value="```\nã¯ã­ã¼ãº / Close \n```", inline=False)
            embed.add_field(name="ä½æçç± / Reason", value=f"```\n*** ã¯ã­ã¼ãº / Closed *** \n```", inline=False)
        return embed

    #get_mentionable_roles
    async def get_mentionable_roles(self, guild_id: int) -> discord.Role:
        db = await self.bot.db.fetchall(
            "SELECT * FROM mentionable_roles WHERE guild_id=%s",
            (guild_id,)
        )
        guild = self.bot.get_guild(guild_id)
        if db:
            l = list()
            for i in db:
                role = guild.get_role(i["role_id"])
                if role:
                    l.append(role)
            return l

    #crate_ticket_channel
    async def create_ticket_channel(
        self, guild_id: int, author_id: int
    ) -> discord.TextChannel:
        guild = self.bot.get_guild(guild_id)
        db = await self.bot.db.fetchone(
            "SELECT * FROM ticketconfig WHERE guild_id=%s",
            (guild_id,)
        )
        ow = {
            guild.default_role: discord.PermissionOverwrite(
                read_messages=False,
                send_messages=False,
                read_message_history=False
            ),
            guild.me: discord.PermissionOverwrite(
                read_messages=True,
                send_messages=True,
                read_message_history=True,
                manage_channels=True,
                add_reactions=True,
                manage_messages=True,
                embed_links=True,
                attach_files=True,
                external_emojis=True,
                manage_permissions=True,
                external_stickers=True
            ),
            guild.get_member(author_id): discord.PermissionOverwrite(
                read_messages=True,
                send_messages=True,
                read_message_history=True,
                add_reactions=True,
                embed_links=True,
                attach_files=True,
                external_emojis=True,
                external_stickers=True
            )
        }

        if db:
            category = self.bot.get_channel(db["open_category_id"])
            if category and isinstance(category, discord.CategoryChannel):
                channel = await category.create_text_channel(
                    f"ticket-{author_id}",
                    overwrites=ow,
                    reason=f"Ticket Channel created by {author_id}"
                )
                return channel

    #get_panel_info
    async def get_panel_info(self, guild_id: int) -> str:
        db = await self.bot.db.fetchone(
            "SELECT * FROM ticketconfig WHERE guild_id=%s",
            (guild_id,)
        )
        val = [None, None]

        if db:
            val[0] = db["panel_title"]
            val[1] = db["panel_description"]
        return val

    #create_panel
    async def create_panel(
        self, channel: discord.TextChannel, title: str=None, description: str=None, color: int=None
    ) -> discord.Message:
        embed = self.create_ticket_panel(title, description, color)
        mention = await self.get_mentionable_roles(channel.guild.id)
        config = await self.bot.db.fetchone(
            "SELECT * FROM ticketconfig WHERE guild_id=%s",
            (channel.guild.id,)
        )
        mentionable = None

        if config:
            if config["mention_created"] == 1:
                mentionable = "@everyone"
            if config["mention_created"] == 2:
                mentionable = " ".join([i.mention for i in mention])
        msg = await channel.send(content=mentionable, embed=embed)

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
            "CREATE TABLE IF NOT EXISTS ticketconfig(guild_id BIGINT PRIMARY KEY NOT NULL, open_category_id BIGINT, close_category_id BIGINT, auto_archive INTEGER, auto_delete INTEGER, mention_created INTEGER, panel_title TEXT, panel_description TEXT)",
            "CREATE TABLE IF NOT EXISTS ticketpanels(panel_id BIGINT PRIMARY KEY NOT NULL, guild_id BIGINT, channel_id BIGINT, created_at TEXT)",
            "CREATE TABLE IF NOT EXISTS mentionable_roles(role_id BIGINT PRIMARY KEY NOT NULL, role_id BIGINT)"
        ]

        for i in query:
            try:
                await self.bot.db.execute(i)
            except Exception as exc:
                pass
