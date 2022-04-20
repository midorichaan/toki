import asyncio
import subprocess
import uuid
from discord.ext import commands

#minecraft converter
class MinecraftConverter(commands.Converter):
    async def convert(self, ctx, value):
        data = None
        try:
            id = uuid.UUID(value)
        except:
            async with ctx.bot.session.get(f"https://api.mojang.com/users/profiles/minecraft/{value}") as resp:
                if resp.status == 204:
                    raise ValueError("ユーザーが見つかりませんでした")
                elif resp.status == 200:
                    js = await resp.json()
                    data = js["id"]
                else:
                    raise ValueError("ユーザー名の検証中にエラーが発生しました")
        else:
            async with ctx.bot.session.get(f"https://api.mojang.com/user/profile/{id.hex}") as resp:
                if resp.status == 204:
                    raise ValueError("UUIDが見つかりません")
                elif resp.status == 200:
                    js = await resp.json()
                    data = js["id"]
                else:
                    raise ValueError("UUIDの検証中にエラーが発生しました")
        return data

#get_status
def get_status(member):
    status = str(member.status)
    if status == "online":
        return f"💚オンライン"
    elif status == "idle":
        return f"🧡退席中"
    elif status == "dnd":
        return f"❤取り込み中"
    elif status == "offline":
        return f"🖤オフライン"
    else:
        return f"💔不明"

#reply_or_send
async def reply_or_send(ctx, *args, **kwargs):
    try:
        return await ctx.reply(*args, **kwargs)
    except:
        try:
            return await ctx.send(*args, **kwargs)
        except:
            try:
                return await ctx.author.send(*args, **kwargs)
            except:
                pass

#remove ```
def cleanup_code(content):
    if content.startswith('```') and content.endswith('```'):
        return '\n'.join(content.split('\n')[1:-1])

    return content.strip('` \n')

#create shell process
async def run_process(ctx, command):
    try:
        process = await asyncio.create_subprocess_shell(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        result = await process.communicate()
    except NotImplementedError:
        process = subprocess.Popen(command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        result = await ctx.bot.loop.run_in_executor(None, process.communicate)

    return [output.decode() for output in result]

#is_staff
def is_staff():
    async def predicate(ctx):
        if not ctx.guild:
            return ctx.author.id in ctx.bot.owner_ids
        roles = [i.id for i in ctx.author.roles]
        if 965613844997226556 in roles:
            return True
        elif 965613765523542046 in roles:
            return True
        return False
    return commands.check(predicate)
