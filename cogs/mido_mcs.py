import discord
from discord.ext import commands

import os
from dotenv import load_dotenv
from lib import database, utils

#load .env
load_dotenv()

class mido_mcs(commands.Cog):

    def __init__(self, bot):
        self.bot = bot
        self.db = database.Database(
            host=os.environ["DBHOST"],
            port=int(os.environ["DBPORT"]),
            user=os.environ["DBUSER"],
            password=os.environ["DBPASSWORD"],
            db=os.environ["DB"]
        )

    #get_all_punish
    async def get_all_punish(self):
        result = []
        db = await self.db.fetchall("SELECT * FROM Punishments")

        if not db:
            return result
        return db

    #get_punish
    async def get_punish(self, target: str, type: str):
        db = await self.db.fetchone("SELECT * FROM Punishments WHERE name=%s AND punishmentType=%s", (target, type))
        if not db:
            db = await self.db.fetchone("SELECT * FROM Punishments WHERE uuid=%s AND punishmentType=%s", (target, type))
        return db

    #baninfo
    @utils.is_staff()
    @commands.command(name="baninfo", description="Banされているプレイヤーの情報を表示します")
    async def _baninfo(self, ctx, player: str=None):
        msg = await utils.reply_or_send(ctx, content="> 処理中...")

        if not player:
            return await msg.edit(content="> プレイヤーを指定してください")

        try:
            result = await self.get_punish(player, "BAN")
        except Exception as exc:
            return await msg.edit(content=f"> エラー \n```py\n{exc}\n```")
        else:
            if not result:
                return await msg.edit(content="> データが存在しません")

            e = discord.Embed(title=f"{result['name']} の情報", color=0xf172a3, timestamp=ctx.message.created_at)
            e.add_field(name="MCID", value=result["name"])
            e.add_field(name="UUID", value=result["uuid"])
            e.add_field(name="PunishmentID", value=str(result["id"]))
            e.add_field(name="PunishmentType", value=result["punishmentType"])
            e.add_field(name="Operator", value=result["operator"])
            e.add_field(name="Duration", value="無期限" if str(result["end"]) == "-1" else str(result["end"]))
            e.add_field(name="Reason", value=f"```\n{result['reason']}\n```", inline=False)
            return await msg.edit(content=None, embed=e)

    #banlist
    @utils.is_staff()
    @commands.command(name="banlist", description="Banされているプレイヤーを表示します")
    async def _banlist(self, ctx, player: str=None):
        msg = await utils.reply_or_send(ctx, content="> 処理中...")

        if not player:
            return await msg.edit(content="> プレイヤーを指定してください")

        try:
            result = await self.get_all_punish()
        except Exception as exc:
            return await msg.edit(content=f"> エラー \n```py\n{exc}\n```")
        else:
            if not result:
                return await msg.edit(content="> データが存在しません")

            result = [i for i in result if str(i["punishmentType"]) == "BAN"]
            e = discord.Embed(title=f"BanList", color=0xf172a3, timestamp=ctx.message.created_at)
            for i in result:
                e.add_field(name=f"{i['name']} ({i['uuid']})", value=f"```\n{i['reason']}\n```")
            return await msg.edit(content=None, embed=e)

async def setup(bot):
    await bot.add_cog(mido_mcs(bot))
