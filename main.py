import discord, os, asyncio
from discord.ext import commands
import requests
from bs4 import BeautifulSoup
#from os.path import exists
#import sys
#import re
#import random

intents = discord.Intents().all()
intents.members = True

client = commands.Bot(command_prefix = ".", 
                      intents=intents, 
                      activity = discord.Activity(type=discord.ActivityType.watching, name="Kiniga.com"), 
                      status=discord.Status.online)
client.remove_command('help')

f = ''


@client.event
async def on_ready():
    try:
        print(f'Tudo perfeito!')
    except:
        print(f'Não foi possivel adicionar uma atividade.')
        return

@client.event
async def feed():
    await client.wait_until_ready()
    while not client.is_closed():
        soup = BeautifulSoup(requests.get("http://kiniga.com/").text,'lxml')
        table = soup.find('table', attrs={'class':'manga-chapters-listing'})
        titles = table.find_all('td', attrs={'class':'title'})[0]
        
        ##
        
        #if not os.path.exists('links'):
        #    os.mkdir('links')
        #    if not os.path.exists('links/r.txt'):
        #        with open('links/r.txt', 'a'):
        #            pass
        #    else:
        #        pass
        #else:
        #    pass
        ###
        
        #mode = 'r+' if os.path.exists("links/r.txt") else 'w+'
        #print(f'{mode}')
        for t in titles:
            try:
                links = table.find_all('td', attrs={'class':'release'})[0]
                for l in links.find_all('a', href=True):
                    try:
                        global f
                        if f == l['href']:
                            return await asyncio.sleep(300)
                        else:
                            channel = discord.utils.get(client.get_all_channels(), 
                                                        guild__name='Kiniga Brasil', 
                                                        name='✶⊷彡recentes')
                            await channel.send('Saiu o **{}** de **{}**!\n\n_**Leia agora**_! {}'.format(l.get_text(), 
                                                                                                         t.get_text(), 
                                                                                                         l['href']))
                            f = l['href']
                            await asyncio.sleep(300)
                    except: 
                        return await asyncio.sleep(30)
            except:
                return await asyncio.sleep(300)
@client.event
async def on_command_error(ctx, error):
    if isinstance(error, commands.CommandNotFound):
        await ctx.send('Olha, eu chuto que esse comando não exite...')
        await asyncio.sleep(1)
        return await ctx.channel.purge(limit=2)


for filename in os.listdir('./cmds'):
    if filename.endswith('.py'):
        client.load_extension(f'cmds.{filename[:-3]}')

@client.command()
@commands.is_owner()
async def load(self, ctx, extension):
    self.load_extension(f'cmds.{extension}')
    await ctx.send(f"I have loaded the command")

@client.command()
@commands.is_owner()
async def reload(self, ctx, extension):
    self.unload_extension(f'cmds.{extension}')
    self.load_extension(f'cmds.{extension}')
    await ctx.send("I have reloaded the command")

@client.command()
@commands.is_owner()
async def unload(self, ctx, extension):
    self.unload_extension(f'cmds.{extension}')
    await ctx.send("I have unloaded the command")
                
client.loop.create_task(feed())

client.run("")
