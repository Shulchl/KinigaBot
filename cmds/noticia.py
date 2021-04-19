import discord, asyncio
from discord.ext import commands  

class Noticia(commands.Cog):

    def __init__(self, client):
        self.client = client

    @commands.Cog.listener()
    async def on_ready(self):
        print('Comando de notícias funcionando!    [√]')

    @commands.command(pass_context=True)
    @commands.has_permissions(administrator=True)
    async def noticia(self, ctx, channel: discord.TextChannel, message):
        
        ### Get text ###
        msg = []
        titulo = []
        msg = ctx.message.content.split()
        del msg[0]
        del msg[0]
        a = ' '.join(msg)
        a = str(a)
        a = a.strip('"')
        conteudo = a
        
        ### Get channel ###
        channel_name = ctx.message.content.split()
        del channel_name[0]
        a = ' '.join(channel_name)
        a = str(channel_name[0])
        a = a.strip('<')
        a = a.strip('>')
        a = a.strip('#')
        channel_id = a        
        channel_name = (channel for channel in self.client.get_all_channels() if channel.id == channel_id)
        
        ### Start the magic ###
        emb = discord.Embed(title='Certo!',description=f'Deseja usar "**{conteudo}**" como conteúdo da notícia?',color=discord.Color.orange()).set_footer(text='Para cancelar, basta aguardar.')
        msg = await ctx.send('',embed=emb)
        await msg.add_reaction('✅')
        await asyncio.sleep(1)
        def check(reaction, member):
            return member == ctx.author and str(reaction.emoji) == '✅'
        try:
            await self.client.wait_for('reaction_add',timeout=30.0, check=check)
            emb2 = discord.Embed(title='Digite o título!',description='*Cri, cri...*',color=discord.Color.orange()).set_footer(text='Para cancelar, basta aguardar.')
            await ctx.send('',embed=emb2)
            def check_2(message):
                return message.author.id == ctx.author.id and message.author.id != self.client.user.id
            try:
                titulo = await self.client.wait_for('message',timeout=30.0, check=check_2)
                titulo = titulo.content
                emb3 = discord.Embed(title='Certo!', description="Deseja usar\n\n**{}**\n\n... como título da notícia?".format(titulo), color=discord.Color.orange()).set_footer(text='Para cancelar, basta aguardar.')
                msg3 = await ctx.send('',embed=emb3)
                await msg3.add_reaction('✅')
                await asyncio.sleep(1)
                def check_3(reaction, member):
                    return reaction.message.id == msg3.id and str(reaction.emoji) == '✅'
                try:
                    await self.client.wait_for('reaction_add',timeout=10.0, check=check_3)
                    await asyncio.sleep(1)
                    await ctx.channel.purge(limit=4)
                    emb5 = discord.Embed(title='{}'.format(titulo),description='{}'.format(conteudo),color=discord.Color.green())
                    await channel.send('',embed=emb5)
                    return await ctx.send('A notícia foi enviada com sucesso')
                except asyncio.TimeoutError:
                    emb5 = discord.Embed(title='Hum...',description='Eu não recebi uma confirmação, que tal tentar de novo?.',color=discord.Color.orange())
                    await ctx.send('',embed=emb5)
                    await asyncio.sleep(3)
                    return await ctx.channel.purge(limit=2)
            except asyncio.TimeoutError:
                emb5 = discord.Embed(title='Hum...',description='Eu não recebi uma confirmação, que tal tentar de novo?.',color=discord.Color.orange())
                await ctx.send('',embed=emb5)
                await asyncio.sleep(3)
                return await ctx.channel.purge(limit=2)
        except asyncio.TimeoutError:
            emb5 = discord.Embed(title='Hum...',description='Eu não recebi uma confirmação, que tal tentar de novo?.',color=discord.Color.orange())
            await ctx.send('',embed=emb5)
            await asyncio.sleep(3)
            return await ctx.channel.purge(limit=2)
        else:
            emb5 = discord.Embed(title='Hum...',description='Você precisa marcar um canal válido. Esse eu não achei :c',color=discord.Color.red())
            await ctx.send('',embed=emb5)
            await asyncio.sleep(3)
            return ctx.channel.purge(limit=2)

def setup(client):
    client.add_cog(Noticia(client))