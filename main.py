import discord
import os
import aiohttp
import sys
import asyncio
import json
import logging

from os import listdir

from bs4 import BeautifulSoup

from base import log, cfg
from base.functions import cogs_manager
from discord.ext import commands, tasks

kiniga_headers = {
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_14_3) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/71.0.3578.98 Safari/537.36",
        "Accept": "text/html,application/xhtml+xml,application/xml; q=0.9,image/webp,image/apng,*/*;q=0.8"}

intents = discord.Intents().all()
intents.members = True

class KinigaBot(commands.Bot):
    def __init__(self, **kwargs) -> None:
        super().__init__(
            intents=kwargs.pop("intents"),
            command_prefix=commands.when_mentioned_or(kwargs.pop("prefix")),
            description=kwargs.pop("description"),
            activity=kwargs.pop("activity"),
            case_insensitive = True,
            config = kwargs.pop("config", cfg),
            **kwargs,
        )
        self.last_release = {}
        
    async def setup_hook(self) -> None:
        # discord.utils.setup_logging()
        log.info(f'Logado como {self.user} (ID: {self.user.id}) usando discord.py {discord.__version__}')
        #self.feed.start()

        cogs = [f"base.cmds.{filename[:-3]}" for filename in listdir("./base/cmds") if filename.endswith(".py")]
        await cogs_manager(self, "load", cogs)
        log.info(f"Cogs loaded ({len(cogs)}): {', '.join(cogs)}")

        # self.tree.copy_global_to(guild=TEST_GUILD)
        # await self.tree.sync(guild=TEST_GUILD)

    async def close(self) -> None:
        log.info("desligando o bot...")
        self.feed.stop()
        await super().close()
        await self.session.close()

    async def get_release(self):
        items = {}
        async with aiohttp.ClientSession(headers=kiniga_headers) as session:
            async with session.get("http://kiniga.com/") as resp:
                if resp.status == 200:
                    soup = BeautifulSoup(await resp.text(), 'lxml')
                    tbody = soup.find(
                        'table', attrs={'class':'manga-chapters-listing'}
                    ).find('tbody')
                    this_name = tbody.tr.td.next_sibling.next_sibling.a.get_text()
                    this_url = tbody.tr.td.next_sibling.next_sibling.next_sibling.next_sibling.a['href']
                    items[str(this_name)] = str(this_url)
                    json.dumps(items)

        if items == self.last_release:
            return "No_Changes"

        return items

    @tasks.loop(minutes = 5)
    async def feed(self):
        if self.config["config"]["feed_loop"] == False:
            return

        release = await self.get_release()
        
        if not release or type(release) == str:
            return
        
        channel = self.get_channel(self.config["config"]["chat_loop"])
        message = [message async for message in channel.history(limit=1) 
                    if message.author == self.user]
        msg = None
        for key, value in release.items():
            if not key in release:
                if not self.last_release:
                    return

                key, value = [(key, value) for x, z in self.last_release.items()]

            if value == self.last_release.get(key):
                return

            if value.startswith("https://www.kiniga.com/?chapter"):
                return

            if message:
                message.reverse()
                message = message[0].content.split(" | ")

                if len(message) == 3:
                    x, old_key, old_value = message
                elif len(message) == 2:
                    old_key, old_value = message

                old_key = old_key.strip("**")
                if old_key in release:
                    if release.get(old_key) == old_value:
                        return

                    release[old_key] = value

                json.dumps(release)

            emoji = self.get_emoji(769235205407637505)

            msg = '%s | **%s** | %s' % (
                emoji,
                key,
                value
            )
            break

        self.last_release = release

        if not msg:
            return

        member = channel.guild.get_member(741770490598653993)
        
        await channel.send(msg)

    @feed.before_loop
    async def get_ready(self):
        log.info("Aguardando inicialização...\n")
        await self.wait_until_ready()
        log.info("Inicialização completa.\n")

async def main() -> None:
    config = cfg
    bot = KinigaBot(
        config = config,
        prefix = config["config"]["bot_prefix"], 
        description = config["config"]["description"], 
        activity = discord.Activity(
            type=discord.ActivityType.watching, name="Kiniga"
        ),
        intents = discord.Intents.all())
    bot.config = config
    bot.log = log

    async with aiohttp.ClientSession() as session, bot:
        bot.session = session
        await bot.start(bot.config["config"]["bot_token"])


async def warn() -> None:
    return log.info("bot foi desligado usando ctrl+c no terminal!")

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        asyncio.run(warn())
