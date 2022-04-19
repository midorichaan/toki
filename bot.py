import discord
from discord.ext import commands, tasks

import aiohttp
import asyncio
import datetime
import json
import os
import traceback

from logging import basicConfig, getLogger, INFO
from dotenv import load_dotenv
from lib import utils

#logger
basicConfig(
    level=INFO, 
    format="%(asctime)s - %(name)s - [%(levelname)s]: %(message)s"
)

#load .env
load_dotenv()

class TokiHanasaki(commands.Bot):

    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)

        self.owner_ids = [546682137240403984, 780033257046802453, 385746925040828418, 352395944139948033]
        self.owner_id = None
        self.logger = getLogger("discord")
        self._cogs = [
            "cogs.mido_mcs", "cogs.mido_admins", "jishaku"
        ]

    #run
    def run(self, token: str=None) -> None:
        if not token:
            self.logger.critical("token was not provided")
        else:
            try:
                super().run(token)
            except Exception as exc:
                self.logger.critical(exc)
            else:
                self.logger.info("enabling...")

    #on_ready
    async def on_ready(self) -> None:
        self.logger.info(f"Logged in as {self.user}")

        for i in self._cogs:
            try:
                await self.load_extension(i)
            except Exception as exc:
                self.logger.error(exc)
            else:
                self.logger.info(f"Successfully loaded {i}")

        try:
            await self.change_presence(
                status=discord.Status.online,
                activity=discord.Game(
                    "のんびりさーばー監視ちう..."
                )
            )
        except Exception as exc:
            self.logger.error(exc)
        else:
            self.logger.info("Successfully updated presence")

        self.logger.info("on_ready!")

    #on_command
    async def on_command(self, ctx) -> None:
        if isinstance(ctx.channel, discord.DMChannel):
            format = f"COMMAND: {ctx.author} ({ctx.author.id}) -> {ctx.message.content} @DM"
            self.logger.info(format)
        else:
            format = f"COMMAND: {ctx.author} ({ctx.author.id}) -> {ctx.message.content} @{ctx.channel} ({ctx.channel.id}) - {ctx.guild} ({ctx.guild.id})"
            self.logger.info(format)

    #on_command_error
    async def on_command_error(self, ctx, exc) -> None:
        traceback_exc = ''.join(
            traceback.TracebackException.from_exception(exc).format()
        )
        format = ""

        if isinstance(ctx.channel, discord.DMChannel):
            format = f"ERROR: {ctx.author} ({ctx.author.id}) -> {exc} @DM"
        else:
            format = f"ERROR: {ctx.author} ({ctx.author.id}) -> {exc} @{ctx.channel} ({ctx.channel.id}) - {ctx.guild} ({ctx.guild.id})"

        self.logger.warning(format)
        await utils.reply_or_send(
            ctx,
            content=f"> エラー \n```py\n{exc}\n```"
        )

#get_token from environ
def get_token(value: str) -> str:
    return os.environ.get(value, None)

if __name__ == "__main__":
    intents = discord.Intents.all()
    bot = TokiHanasaki(
        intents=intents, 
        command_prefix=".",
        status=discord.Status.idle
    )
    token = get_token("TOKEN")
    bot.run(token)
