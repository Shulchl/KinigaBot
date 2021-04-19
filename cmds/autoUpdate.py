import discord, os, asyncio, shlex, subprocess
from discord.ext import commands
import discord.utils 
from discord.ext.commands.cooldowns import BucketType
from os.path import exists

class NoPrivateMessages(commands.CheckFailure):
    pass

def guild_only():
    async def predicate(ctx):
        if ctx.guild is None:
            raise NoPrivateMessages('Esse comando não pode ser usado em mensagens privadas!')
        return True
    return commands.check(predicate)

def launch_process(*args):
    return subprocess.Popen(
        ' '.join([shlex.quote(x) for x in args]),
        stdin=subprocess.PIPE,
        stdout=subprocess.PIPE,
        shell=True
    )

async def get_output(*args):
    process = launch_process(*args)
    data = (process.communicate())[0]
    if isinstance(data, bytes):
        return data.decode("UTF-8").strip() and print(data.strip())
    return data.strip()

class Autoupdate(commands.Cog, name='auto-update'):

    def __init__(self, client):
        super().__init__()
        #self.client = client
        self.dont_update = False
        asyncio.ensure_future(self.do_update())

    @guild_only()
    @commands.command()
    @commands.is_owner()
    async def update(self, ctx):
        await self._update()
        await ctx.send("👌")

    async def check_for_update(self):
        if not self.dont_update:
            asyncio.ensure_future(self.do_update())

    async def do_update(self):
        await self._update()
        asyncio.get_event_loop().call_later(900, self.check_for_update)

    async def _update(self):
        await get_output("git", "init")
        # 0) fetch latest commit
        if not os.path.exists('.git'):
            local_commit = await get_output("git", "remote", "add", "origin", "git@github.com:Shulchl/KinigaBot.git")
        else:
            pass
        ###
        
        #mode = 'r+' if os.path.exists("links/r.txt") else 'w+'
        #print(f'{mode}')
        
        #push_commit = await get_output("git", "fetch", "origin/master")
        # pull from the origin
        await get_output("git", "pull", "git@github.com:Shulchl/KinigaBot.git", "-f")
    @commands.Cog.listener()
    async def on_ready(self):
        print('Comando de update funcionando!    [√]')
        
def setup(client):
    client.add_cog(Autoupdate(client))