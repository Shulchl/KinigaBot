import discord, os, aiohttp, json
from discord.ext import commands, tasks
from bs4 import BeautifulSoup
from discord_components import DiscordComponents

from base.struct import Config

import logging
import logging.handlers

logger = logging.getLogger('discord')
logger.setLevel(logging.INFO)
#logging.getLogger('discord.http').setLevel(logging.INFO)

handler = logging.handlers.RotatingFileHandler(
    filename='discord.log',
    encoding='utf-8',
    maxBytes=32 * 1024 * 1024,  # 32 MiB
    backupCount=5,  # Rotate through 5 files
)
dt_fmt = '%Y-%m-%d %H:%M:%S'
formatter = logging.Formatter('[{asctime}] [{levelname:<8}] {name}: {message}', dt_fmt, style='{')
handler.setFormatter(formatter)
logger.addHandler(handler)


intents = discord.Intents().all()
intents.members = True

class Bot(commands.Bot):
    def __init__(self):
            
        super().__init__(
            intents=intents,
            command_prefix=commands.when_mentioned_or('.'),
            description='Bot da Kiniga Brasil.',
            activity=discord.Streaming(name="https://kiniga.com/", url='https://kiniga.com/')
            ),
        DiscordComponents(self),
        self.remove_command('help'),
        self.feed.start()
                                

        with open('config.json', 'r', encoding='utf-8') as f:
            self.cfg = Config(json.loads(f.read()))
        
        try:
            for filename in os.listdir('./cogs'):
                if filename.endswith('.py'):
                    try:
                        self.load_extension(f'cogs.{filename[:-3]}')
                        print(f'Cog "{filename}" foi carregada.')
                    except Exception as e:
                        print(f'Error occured while cog "{filename}" was loaded.\n{e}')
        except Exception as i:
            raise i

    def cog_unload(self):
      return self.feed.close()  
         
    def startup(self):
        self.run(self.cfg.bot_token)
        
    
    @tasks.loop(minutes = 5)
    async def feed(self):
        async with aiohttp.ClientSession() as session:
            async with session.get("http://kiniga.com/") as resp:
                soup = BeautifulSoup(await resp.text(), 'lxml')
                table = soup.find('table', attrs={'class':'manga-chapters-listing'})
                titles = table.find('td', attrs={'class':'title'})
                for t in titles:
                    try:
                        links = table.find_all('td', attrs={'class':'release'})[0]
                        for l in links.find_all('a', href=True):
                            try:
                                emoji = self.get_emoji(id=769235205407637505)
                                channel = discord.utils.get(self.get_all_channels(), 
                                                            guild__name=self.cfg.guild, 
                                                            id=self.cfg.chat_loop)
                                messages = await channel.history(limit=1).flatten()
                                messages.reverse()
                                cont = '{} | Saiu o **{}** de **{}**!\n{}'.format(emoji, l.get_text(),
                                                                            t.get_text(),
                                                                            l['href'])
                                member = channel.guild.get_member(741770490598653993)
                                webhooks = await channel.webhooks()
                                webhook = discord.utils.get(webhooks, name = "Capitulos Recentes")
                                
                                if webhook is None:
                                    webhook = await channel.create_webhook(name = "Capitulos Recentes")
                                
                                for i, message in enumerate(messages):
                                    message = message.content
                                    if message == cont:
                                        pass
                                    else:
                                        await webhook.send(cont, username = member.name, avatar_url = member.avatar_url)
                            except Exception as e: raise e
                        else: pass
                    except Exception as e: raise e
                else: pass
    
    @feed.before_loop  # wait for the bot before starting the task
    async def before_send(self):
        await self.wait_until_ready()
        return
        


if __name__ == '__main__':
    Bot().startup()