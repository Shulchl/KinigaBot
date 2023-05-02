import discord
import os
import aiohttp
import sys
import asyncio
import json

from discord.ext import commands, tasks
from bs4 import BeautifulSoup

from base import log, cfg

intents = discord.Intents().all()
intents.members = True

class KinigaBot(commands.Bot):
    def __init__(self ) -> None:
        intents = discord.Intents.all()
        atividade = discord.Activity(
            type=discord.ActivityType.watching,
            name="Kiniga")

        super().__init__(
            intents=intents,
            command_prefix=commands.when_mentioned_or(cfg.bot_prefix),
            description='Kiniga Brasil',
            activity=atividade
        )
        self.last_release = {}
        

    async def load_cogs(self) -> None:
        for filename in os.listdir('./base/cmds'):
            if filename.endswith('.py'):
                try:
                    await self.load_extension(f'base.cmds.{filename[:-3]}')
                except Exception as e:
                    log.error(f'Ocorreu um erro enquanto a cog "{filename}" carregava.\n{e}')

    async def setup_hook(self) -> None:
        # discord.utils.setup_logging()
        log.info(f'Logado como {self.user} (ID: {self.user.id}) usando discord.py {discord.__version__}')
        self.feed.start()
        await self.load_cogs()
        # self.tree.copy_global_to(guild=TEST_GUILD)
        # await self.tree.sync(guild=TEST_GUILD)

    async def close(self) -> None:
        log.info("desligando o bot...")
        self.feed.stop()
        await super().close()
        await self.session.close()

    async def get_release(self):
        items = {}
        async with aiohttp.ClientSession() as session:
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
        if cfg.feed_loop == False:
            return

        release = await self.get_release()
        
        if not release or type(release) == str:
            return
        
        channel = self.get_channel(406996662997745674)

        sys.stdout.write(str(channel))
        sys.stdout.flush()

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

            if message:
                message.reverse()
                message = message[0].content.split(" | ")

                log.info(message)
                if len(message) == 3:
                    x, old_key, old_value = message
                elif len(message) == 2:
                    old_key, old_value = message

                old_key = old_key.strip("**")
                log.info((old_key + '\n' + old_value))
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

        member = channel.guild.get_member(737086135037329540)
        
        await channel.send(msg)

    @feed.before_loop
    async def get_ready(self):
        sys.stdout.write("Aguardando inicialização...\n")
        sys.stdout.flush()
        await self.wait_until_ready()
        sys.stdout.write("Inicialização completa.\n")
        sys.stdout.flush()

async def main() -> None:
    bot = KinigaBot()
    async with aiohttp.ClientSession() as session, bot:
        bot.session = session
        await bot.start(cfg.bot_token)


async def warn() -> None:
    return log.info("bot foi desligado usando ctrl+c no terminal!")

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        asyncio.run(warn())