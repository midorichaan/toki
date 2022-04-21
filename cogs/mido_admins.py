import discord
from discord.ext import commands

import asyncio
import io
import os
import psutil
import sys
import textwrap
import traceback
from contextlib import redirect_stdout

from lib import utils

class mido_admins(commands.Cog):

    def __init__(self, bot):
        self.bot = bot
        self._ = None
        self.success = "✅"
        self.failed = "❌"

    #status
    @utils.is_staff()
    @commands.command(name="status", description="サーバーのステータスを表示します")
    async def _status(self, ctx):
        msg = await utils.reply_or_send(ctx, content="> 処理中...")
        e = discord.Embed(title="VPS Status", description="", color=0xf172a1, timestamp=ctx.message.created_at)

        memory = psutil.virtual_memory()
        cpuper = psutil.cpu_percent()
        cpucore = psutil.cpu_count(logical=False)
        swapmemory = psutil.swap_memory()
        disk = psutil.disk_usage(path="/")
        text = f"""
        > __**CPU Status**__
          Core(s): {cpucore}
          Percent: {cpuper}%

        > __**Memory Status**__
          Percent: {memory.percent}%
          Total: {memory.total / (1024.0 ** 3)}GB
          Used: {memory.used / (1024.0 ** 3)}GB
          Free: {memory.available / (1024.0 ** 3)}GB
        
        > __**Swap Memory Status**__
          Percent: {swapmemory.percent}%
          Total: {swapmemory.total / (1024.0 ** 3)}GB
          Used: {swapmemory.used / (1024.0 ** 3)}GB
          Free:: {swapmemory.free / (1024.0 ** 3)}GB
        
        > __**Disk Status**__
          Percent: {disk.percent}%
          Total: {disk.total / (1024.0 ** 3)}GB
          Used: {disk.used / (1024.0 ** 3)}GB
          Free: {disk.free / (1024.0 ** 3)}GB
        """
        e.description = text
        return await msg.edit(content=None, embed=e)

    #eval
    @commands.is_owner()
    @commands.command(name="eval", usage="eval <code>", description="Pythonのコードを評価します")
    async def _eval(self, ctx, *, code: str=None):
        if not code:
            await ctx.message.add_reaction(self.failed)
            return await utils.reply_or_send(ctx, content=f"> body is a required arugment that is missing")

        env = {
            'bot': self.bot,
            'ctx': ctx,
            'self': self,
            '_': self._
        }

        env.update(globals())
        code = utils.cleanup_code(code)
        stdout = io.StringIO()
        to_compile = f'async def func():\n{textwrap.indent(code, "  ")}'

        try:
            exec(to_compile, env)
        except Exception as exc:
            await ctx.message.add_reaction(self.failed)
            return await utils.reply_or_send(ctx, content=f"```py\n{exc.__class__.__name__}: {exc}\n```")

        func = env['func']
        try:
            with redirect_stdout(stdout):
                ret = await func()
        except Exception as exc:
            await ctx.message.add_reaction(self.failed)
            value = stdout.getvalue()
            return await utils.reply_or_send(ctx, content=f'```py\n{value}{traceback.format_exc()}\n```')
        else:
            value = stdout.getvalue()
            await ctx.message.add_reaction(self.success)

            if ret is None:
                if value:
                    await utils.reply_or_send(ctx, content=f'```py\n{value}\n```')
            else:
                self._ = ret
                await utils.reply_or_send(ctx, content=f'```py\n{value}{ret}\n```')

    #shell
    @commands.is_owner()
    @commands.command(name="shell", aliases=["sh"], usage="shell <command>", description="シェルコマンドを実行します")
    async def shell(self, ctx, *, command=None):
        if not command:
            await ctx.message.add_reaction(self.failed)
            return await utils.reply_or_send(ctx, content=f"> command is a required argument that is missing")

        stdout, stderr = await utils.run_process(ctx, command)
        if stderr:
            text = f"```\nstdout: \n{stdout} \n\nstderr: \n{stderr}\n```"
        else:
            text = f"```\nstdout: \n{stdout} \n\nstderr: \nnone\n```"

        try:
            await ctx.message.add_reaction(self.success)
            return await utils.reply_or_send(ctx, content=text)   
        except Exception as exc:
            await ctx.message.add_reaction(self.failed)
            return await utils.reply_or_send(ctx, content=f"```py\n{exc}\n```")

    #sync
    @commands.is_owner()
    @commands.command(name="sync", usage="sync", description="GitHub上のコードと同期します")
    async def sync(self, ctx):
        stdout, stderr = await utils.run_process(ctx, "sudo -g midorichan -u midorichan git pull")
        if stderr:
            text = f"```\nstdout: \n{stdout} \n\nstderr: \n{stderr}\n```"
        else:
            text = f"```\nstdout: \n{stdout} \n\nstderr: \nnone\n```"

        try:
            await utils.reply_or_send(ctx, content=text)
            return await ctx.message.add_reaction(self.success)
        except Exception as exc:
            await ctx.message.add_reaction(self.failed)
            return await utils.reply_or_send(ctx, content=text)

async def setup(bot):
    await bot.add_cog(mido_admins(bot))
