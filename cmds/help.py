import discord
from discord.ext import commands  

class NoPrivateMessages(commands.CheckFailure):
    pass

def guild_only():
    async def predicate(ctx):
        if ctx.guild is None:
            raise NoPrivateMessages('Esse comando não pode ser usado em mensagens privadas!')
        return True
    return commands.check(predicate)

class Help(commands.Cog):

    def __init__(self, client):
        self.client = client

    @commands.Cog.listener()
    async def on_ready(self):
        print('Comando de Ajuda funcionando!    [√]')

    @guild_only()
    @commands.command(pass_context=True)
    @commands.has_permissions(add_reactions=True,embed_links=True)
    async def help(self,ctx,*cog):
    #"""Gets all cogs and commands of mine."""
        if not cog:
            #"""Cog listing.?"""
            halp=discord.Embed(title='Essa é a lista de categorias com comandos',
                               description='Use `.help *categoria*` para saber mais detalhes sobre a categoria!\n(A categoria deve começar com letra maiúscula.)')
            cogs_desc = ''
            for x in self.client.cogs:
                cogs_desc += ('{} - {}'.format(x,self.client.cogs[x].__doc__)+'\n')
            halp.add_field(name='Categorias de comandos',value=cogs_desc[0:len(cogs_desc)-1],inline=False)
            #cmds_desc = ''
            #for y in self.client.walk_commands():
            #    if not y.cog_name and not y.hidden:
            #        cmds_desc += ('{} - {}'.format(y.name,y.help)+'\n')
            #halp.add_field(name='Comandos não categorizados',value=cmds_desc[0:len(cmds_desc)-1],inline=False)
            await ctx.message.add_reaction(emoji='✉')
            await ctx.message.author.send('',embed=halp)
        else:
            #"""Helps me remind you if you pass too many args."""
            if len(cog) > 1:
                halp = discord.Embed(title='Opa!',description='Você colocou categorias demais!',color=discord.Color.red())
                await ctx.message.author.send('',embed=halp)
            else:
                #"""Command listing within a cog."""
                found = False
                for x in self.client.cogs:
                    for y in cog:
                        if x == y:
                            halp=discord.Embed(title='Mostrando a categoria '+cog[0],description=self.client.cogs[cog[0]].__doc__)
                            for c in self.client.get_cog(y).get_commands():
                                if not c.hidden:
                                    halp.add_field(name=c.name,value=c.help,inline=False)
                            found = True
                if not found:
                    #"""Reminds you if that cog doesn't exist."""
                    halp = discord.Embed(title='Opa!',description='A categoria "'+cog[0]+'" não existe.',color=discord.Color.red())
                else:
                    await ctx.message.add_reaction(emoji='✉')
                await ctx.message.author.send('',embed=halp)
    @help.error
    async def help_error(self, ctx, error):
        if isinstance(error, commands.UserInputError):
            await ctx.send("Foi mal, mas você não pode usar isso...")
        elif isinstance(error, commands.CheckFailure):
            return await ctx.send(error)
        
def setup(client):
    client.add_cog(Help(client))