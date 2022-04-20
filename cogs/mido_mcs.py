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
    async def _banlist(self, ctx):
        msg = await utils.reply_or_send(ctx, content="> 処理中...")

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

    #mc
    @commands.group(name="mc", description="Minecraft関連のコマンドです")
    async def _mc(self, ctx):
        if ctx.invoked_subcommand is None:
            return await utils.reply_or_send(
                ctx,
                content="> サブコマンドが指定されていないか、存在しないコマンドです"
            )

    #mc register
    @_mc.command(name="register", description="MCIDを登録します")
    async def _register(self, ctx, type: utils.MinecraftTypeConverter=None, *, mcid: str=None):
        msg = await utils.reply_or_send(ctx, content="> 処理中...")

        if not type:
            return await msg.edit(content="> JavaかBEか指定してね！")
        if not mcid:
            return await msg.edit(content="> MCIDを指定してね！")

        _ = None
        if type == 1:
            #Java Edition
            try:
                _ = await utils.MinecraftConverter().convert(ctx, str(mcid))
            except:
                return await msg.edit(content="> ユーザーが見つからなかったか、検証中にエラーが発生したよ！")

            try:
                data = await self.db.fetchone("SELECT * FROM mcids WHERE mcid=%s AND type=%s", (mcid, 1))
            except Exception as exc:
                return await msg.edit(content=f"> エラー \n```py\n{exc}\n```")
            else:
                if not data:
                    await self.db.execute("INSERT INTO mcids VALUES(%s, %s, %s, %s)", (ctx.author.id, 1, _, mcid))
                    return await msg.edit(content=f"> MCIDを `{mcid}` で登録したよ！")
                else:
                    await self.db.execute("UPDATE mcids SET mcid=%s, uuid=%s WHERE user_id=%s AND type=%s", (mcid, _, ctx.author.id, 1))
                    return await msg.edit(content=f"> MCIDを `{mcid}` に変更したよ！")
        elif type == 2:
            #Bedrock Edition
            try:
                data = await self.db.fetchone("SELECT * FROM mcids WHERE mcid=%s AND type=%s", (mcid, 2))
            except Exception as exc:
                return await msg.edit(content=f"> エラー \n```py\n{exc}\n```")
            else:
                if not data:
                    await self.db.execute("INSERT INTO mcids VALUES(%s, %s, %s, %s)", (ctx.author.id, 2, _, mcid))
                    return await msg.edit(content=f"> MCIDを `{mcid}` で登録したよ！")
                else:
                    await self.db.execute("UPDATE mcids SET mcid=%s WHERE user_id=%s AND type=%s", (mcid, ctx.author.id, 2))
                    return await msg.edit(content=f"> MCIDを `{mcid}` に変更したよ！")

    #mc mcid
    @_mc.command(name="mcid", description="指定ユーザーまたは自分のMCIDを表示します")
    async def _mcid(self, ctx, target: utils.FetchUserConverter=None):
        msg = await utils.reply_or_send(ctx, content="> 処理中...")

        if not target:
            target = ctx.author

        try:
            db = await self.db.fetchall("SELECT * FROM mcids WHERE user_id=%s", (target.id,))
        except:
            return await msg.edit(content="> データベース検索中にエラーが発生しました")
        else:
            if not db:
                return await msg.edit(content="> データが見つかりませんでした")

            e = discord.Embed(title=f"{target} ({target.id}) のMCID", description="", color=0xf172a3, timestamp=ctx.message.created_at)
            for i in db:
                type = "Java" if i["type"] == 1 else "BE"
                e.add_field(name=type, value=f"{i['mcid']} ({i.get('uuid', 'uuidなし')})")
            return await msg.edit(content=None, embed=e)

async def setup(bot):
    await bot.add_cog(mido_mcs(bot))
