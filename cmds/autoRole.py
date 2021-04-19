import discord, asyncio, re, sqlite3
from discord.ext import commands
import discord.utils 
from discord.utils import get
from discord.ext.commands.cooldowns import BucketType

class NoPrivateMessages(commands.CheckFailure):
    pass

def guild_only():
    async def predicate(ctx):
        if ctx.guild is None:
            raise NoPrivateMessages('Esse comando não pode ser usado em mensagens privadas!')
        return True
    return commands.check(predicate)


class Role(commands.Cog, name='Cargos'):

    def __init__(self, client):
        self.client = client

    @commands.Cog.listener()
    async def on_ready(self):
        print('Comando de Cargos funcionando!       [√]')

    @guild_only()
    @commands.command(name='projeto', help='Recebe um determinado cargo ao digitar `.projeto <história> <usuário>` __(campo usuário é opcional)__ ')
    @commands.max_concurrency(1, per=BucketType.default, wait=False)
    @commands.has_any_role("Autor(a)", "Criador(a)", "Ajudante", "Equipe")
    async def projeto(self, ctx, role: discord.Role, member: discord.Member = None):
        if ctx.message.channel == ctx.guild.get_channel(599736377441124353):
            member = member or ctx.author
            role_id = role.id
            autorRole = discord.utils.get(ctx.guild.roles, id=role_id)
            emb = discord.Embed(title='Opa!',description='O cargo **{}** já existe, deseja adicioná-lo?!'.format(autorRole.mention),color=discord.Color.orange()).set_footer(text='Use a reação para confirmar.')
            msg = await ctx.send('',embed=emb)
            await msg.add_reaction('✅')
            def check_ask(reaction, member):
                return member == ctx.author and str(reaction.emoji) == '✅'
                
            try:
                await self.client.wait_for('reaction_add',timeout=20.0, check=check_ask)
                aRole = []
                a_clean = []
                
                if role:
                    a = str(role)
                    a = a.replace('"', '')
                    a_clean = a
                    role_guild = discord.utils.get(ctx.guild.roles, name=a_clean)
                    if role_guild:
                        role_id = ctx.guild.get_role(int(role_guild.id))
                        aRole = role_id
                    else:
                        pass
                else:
                    await ctx.send("Você precisa digitar alguma coisa, meu querido.")
                    return
                    
                if aRole:
                    emb4 = discord.Embed(title='Opa!',description='Parece que {} já tem esse cargo.'.format(member.mention),color=discord.Color.green())
                    message = await ctx.send(embed=emb4)
                    await ctx.send(" ".join(message))
                    await asyncio.sleep(3)
                    await ctx.channel.purge(limit=2)
                    return
                else:
                    emb = discord.Embed(title='Certo!',description='O cargo **{}** será recebido assim que algum ademir reagir à essa mensagem! 1'.format(autorRole.mention),color=discord.Color.orange()).set_footer(text='Use a reação para confirmar.')
                    msg = await ctx.send('',embed=emb)
                    await msg.add_reaction('✅')
                    def check_add(reaction, member):
                        return member == ctx.guild.me.guild_permissions.manage_roles and str(reaction.emoji) == '✅'
                    
                    try:
                        await self.client.wait_for('reaction_add',timeout=60.0, check=check_add)
                        await member.add_roles(autorRole)
                        channel = discord.utils.get(self.client.get_all_channels(), guild__name='Testando bot', name='regras')
                        emb4 = discord.Embed(title='Adicionado!',description='O cargo {} foi adicionado, e agora você é autor! \n Leia o canal {}.'.format(autorRole.mention, channel),color=discord.Color.green()).set_footer(text='Espero que seja muito produtivo escrevendo!')
                        await ctx.send('',embed=emb4)
                    except asyncio.TimeoutError:
                        emb5 = discord.Embed(title='Hum...',description='Eu não recebi uma confirmação de nenhum ademir, que tal tentar de novo?',color=discord.Color.blurple())
                        await ctx.send('',embed=emb5)
                        await asyncio.sleep(3)
                        await ctx.channel.purge(limit=2)
            except asyncio.TimeoutError:
                emb5 = discord.Embed(title='Hum...',description='Eu não recebi uma confirmação, que tal tentar de novo?.',color=discord.Color.blurple())
                await ctx.send('',embed=emb5)
                await asyncio.sleep(3)
                await ctx.channel.purge(limit=2)
        else:
            return
            
    @projeto.error
    async def projeto_error(self, ctx, error):
        if isinstance(error, commands.RoleNotFound):
            
            #split the message into words
            string = str(ctx.message.content)
            temp = string.split()
            
            del temp[0] #Deleta cmd
            
            text = ' '.join(word for word in temp if not word.startswith('.') and not word.startswith('<')) #Cargo
            
            string_1 = str(ctx.message.content)
            temp_1 = string_1.split()
            
            del temp_1[0] #Deleta cmd2
            
            user = ' '.join(word for word in temp_1 if word.startswith('<')) #user
            
            member = []
            
            if user:
                a = str(user)
                a = a.replace("<","")
                a = a.replace(">","")
                a = a.replace("@","")
                a = a.replace("!","")
                user_guild = ctx.guild.get_member(int(a))
                member = user_guild
            else:
                member = ctx.author
                pass
            
            aRole = []
            a_clean = []
            
            if text:
                a = str(text)
                a = a.replace('"', '')
                a_clean = a
                role_guild = discord.utils.get(ctx.guild.roles, name=a_clean)
                if role_guild:
                    role_id = ctx.guild.get_role(int(role_guild.id))
                    aRole = role_id
                else:
                    pass
            else:
                await ctx.send("Você precisa digitar alguma coisa, meu querido.")
                return
                
            emb = discord.Embed(title='Opa!',description='O cargo **{}** será criado assim que algum ademir reagir à essa mensagem!'.format(a_clean),color=discord.Color.orange()).set_footer(text='Use a reação para confirmar.')
            msg = await ctx.send('',embed=emb)
            await msg.add_reaction('✅')
            await asyncio.sleep(1)
            def check_create(reaction, member):
                return member.guild_permissions.manage_channels and reaction.message.id == msg.id and str(reaction.emoji) == '✅'
            try:
                await self.client.wait_for('reaction_add',timeout=60.0, check=check_create)
                if user:
                    if aRole:
                        emb = discord.Embed(title='Opa!',description='O cargo **{}** já existe, deseja adicioná-lo?!'.format(aRole),color=discord.Color.orange()).set_footer(text='Use a reação para confirmar.')
                        msg = await ctx.send('',embed=emb)
                        await msg.add_reaction('✅')
                        def check_ask(reaction, member):
                            return member == ctx.author and str(reaction.emoji) == '✅'
                            
                        try:
                            await self.client.wait_for('reaction_add',timeout=20.0, check=check_ask)
                            role_id = aRole.id
                            for role_id in member.roles:
                                emb4 = discord.Embed(title='Opa!',description='Parece que {} já tem esse cargo.'.format(member.mention),color=discord.Color.green())
                                message = await ctx.send(embed=emb4)
                                await ctx.send(" ".join(message))
                                await asyncio.sleep(3)
                                await ctx.channel.purge(limit=2)
                                return
                            else:
                                emb = discord.Embed(title='Certo!',description='O cargo **{}** será recebido assim que algum ademir reagir à essa mensagem! 1'.format(aRole),color=discord.Color.orange()).set_footer(text='Use a reação para confirmar.')
                                msg = await ctx.send('',embed=emb)
                                await msg.add_reaction('✅')
                                def check_add(reaction, member):
                                    return member == ctx.guild.me.guild_permissions.manage_roles and str(reaction.emoji) == '✅'
                                
                                try:
                                    await self.client.wait_for('reaction_add',timeout=60.0, check=check_add)
                                    await member.add_roles(aRole)
                                    channel = discord.utils.get(self.client.get_all_channels(), guild__name='Testando bot', name='regras')
                                    emb4 = discord.Embed(title='Adicionado!',description='O cargo {} foi adicionado, e agora você é autor! \n Leia o canal {}.'.format(aRole, channel),color=discord.Color.green()).set_footer(text='Espero que seja muito produtivo escrevendo!')
                                    await ctx.send('',embed=emb4)
                                except asyncio.TimeoutError:
                                    emb5 = discord.Embed(title='Hum...',description='Eu não recebi uma confirmação de nenhum ademir, que tal tentar de novo?',color=discord.Color.blurple())
                                    await ctx.send('',embed=emb5)
                                    await asyncio.sleep(3)
                                    await ctx.channel.purge(limit=2)
                        except asyncio.TimeoutError:
                            emb5 = discord.Embed(title='Hum...',description='Eu não recebi uma confirmação, que tal tentar de novo?.',color=discord.Color.blurple())
                            await ctx.send('',embed=emb5)
                            await asyncio.sleep(3)
                            return await ctx.channel.purge(limit=2)
                    else:
                        nRole = await ctx.guild.create_role(name=a_clean, reason="Nova história!")
                        await member.add_roles(nRole)
                        channel = discord.utils.get(self.client.get_all_channels(), guild__name='Testando bot', name='regras')
                        emb6 = discord.Embed(title='Criado!',description='{}, o cargo **{}** foi criado, e agora você é autor! \n Leia o canal {} para saber mais.'.format(member.mention, nRole.mention, channel.mention),color=discord.Color.green()).set_footer(text='Espero que seja muito produtivo escrevendo!')
                        return await ctx.send('',embed=emb6)
                else:
                    if aRole:
                        emb = discord.Embed(title='Opa!',description='O cargo **{}** já existe, deseja adicioná-lo?!'.format(aRole),color=discord.Color.orange()).set_footer(text='Use a reação para confirmar.')
                        msg = await ctx.send('',embed=emb)
                        await msg.add_reaction('✅')
                        def check_ask(reaction, member):
                            return member == ctx.author and str(reaction.emoji) == '✅'
                            
                        try:
                            await self.client.wait_for('reaction_add',timeout=20.0, check=check_ask)
                            for role_id in member.roles:
                                emb4 = discord.Embed(title='Opa!',description='Parece que {} já tem esse cargo.'.format(member.mention),color=discord.Color.green())
                                await ctx.send(embed=emb4)
                                await asyncio.sleep(3)
                                return await ctx.channel.purge(limit=2)
                            else:
                                emb = discord.Embed(title='Certo!',description='O cargo **{}** será recebido assim que algum ademir reagir à essa mensagem! 1'.format(aRole),color=discord.Color.orange()).set_footer(text='Use a reação para confirmar.')
                                msg = await ctx.send('',embed=emb)
                                await msg.add_reaction('✅')
                                def check_add(reaction, member):
                                    return member == ctx.guild.me.guild_permissions.manage_roles and str(reaction.emoji) == '✅'
                                
                                try:
                                    await self.client.wait_for('reaction_add',timeout=60.0, check=check_add)
                                    await member.add_roles(aRole)
                                    channel = discord.utils.get(self.client.get_all_channels(), guild__name='Testando bot', name='regras')
                                    emb4 = discord.Embed(title='Adicionado!',description='O cargo {} foi adicionado, e agora você é autor! \n Leia o canal {}.'.format(aRole, channel),color=discord.Color.green()).set_footer(text='Espero que seja muito produtivo escrevendo!')
                                    await ctx.send('',embed=emb4)
                                except asyncio.TimeoutError:
                                    emb5 = discord.Embed(title='Hum...',description='Eu não recebi uma confirmação de nenhum ademir, que tal tentar de novo?',color=discord.Color.blurple())
                                    await ctx.send('',embed=emb5)
                                    await asyncio.sleep(3)
                                    await ctx.channel.purge(limit=2)
                        except asyncio.TimeoutError:
                            emb5 = discord.Embed(title='Hum...',description='Eu não recebi uma confirmação, que tal tentar de novo?.',color=discord.Color.blurple())
                            await ctx.send('',embed=emb5)
                            await asyncio.sleep(3)
                            return await ctx.channel.purge(limit=2)
                    else:
                        nRole = await ctx.guild.create_role(name=a_clean, reason="Nova história!")
                        await ctx.author.add_roles(nRole)
                        channel = discord.utils.get(self.client.get_all_channels(), guild__name='Testando bot', name='regras')
                        emb6 = discord.Embed(title='Criado!',description='{}, o cargo **{}** foi criado, e agora você é autor! \n Leia o canal {} para saber mais.'.format(ctx.author.mention, nRole.mention, channel.mention),color=discord.Color.green()).set_footer(text='Espero que seja muito produtivo escrevendo!')
                        await ctx.send('',embed=emb6)
                        
            except asyncio.TimeoutError:
                emb5 = discord.Embed(title='Hum...',description='Eu não recebi uma confirmação de nenhum ademir, que tal tentar de novo?',color=discord.Color.blurple())
                await ctx.send('',embed=emb5)
                await asyncio.sleep(3)
                return await ctx.channel.purge(limit=2)
                
        elif isinstance(error, commands.MaxConcurrencyReached):
            await ctx.send("Já tem uma história na fila, você deve aguardar a sua vez.")
            await asyncio.sleep(2)
            return await ctx.channel.purge(limit=2)
        elif isinstance(error, commands.BotMissingPermissions):
            await ctx.send("Parece que eu não tenho permissão para isso!")
            await asyncio.sleep(2)
            return await ctx.channel.purge(limit=2)
        elif isinstance(error, commands.MissingPermissions):
            await ctx.send("Parece que você não tenho permissão para isso!")
            await asyncio.sleep(2)
            return await ctx.channel.purge(limit=2)
        elif isinstance(error, commands.CheckFailure):
            return await ctx.send(error)
            
    @guild_only()         
    @commands.command(name='r', help='Deletar história ao digitar `.r <cargo> <usuário>` __(campo usuário é opcional)__ ')
    @commands.has_permissions(manage_roles=True)
    async def r(self, ctx, role: discord.Role, member: discord.Member = None, reason=None):
        member = member or ctx.author
        
        aRole = []
        a_clean = []
        
        if role:
            a = str(role)
            a = a.replace('"', '')
            a_clean = a
            role_guild = discord.utils.get(ctx.guild.roles, name=a_clean)
            if role_guild:
                role_id = ctx.guild.get_role(int(role_guild.id))
                aRole = role_id
            else:
                pass
        else:
            await ctx.send("Você precisa digitar alguma coisa, meu querido.")
            return
        #nomeRole = discord.utils.get(ctx.guild.roles, name=role)
        emb = discord.Embed(title='Tem certeza?',description='Deseja realmente remover de {}?'.format(member.mention),color=discord.Color.orange()).set_footer(text='Use a reação para confirmar')
        msg = await ctx.send('',embed=emb)
        await msg.add_reaction('✅')
        
        def check(reaction, member):
            return member == ctx.author and str(reaction.emoji) == '✅'
            
        try:
            await self.client.wait_for('reaction_add',timeout=20.0, check=check)
            if aRole:
                await member.remove_roles(role)
                emb = discord.Embed(title='?!',description='Deseja remover completamente? \nEssa ação não pode ser desfeita!',color=discord.Color.red()).set_footer(text='Use a reação para confirmar ou não reaja para cancelar.')
                msg = await ctx.send('',embed=emb)
                await msg.add_reaction('✅')
                
                def check_delete(reaction, member):
                    return member == ctx.author and str(reaction.emoji) == '✅'
                
                try:
                    await self.client.wait_for('reaction_add',timeout=10.0, check=check_delete)
                    await aRole.delete(reason="Hitória removida.")
                    await ctx.channel.purge(limit=4)
                    await asyncio.sleep(2)
                    emb2 = discord.Embed(title='História removida!',description='Espero que não se arrependa...',color=discord.Color.green())
                    return await ctx.send('',embed=emb2)
                    
                except asyncio.TimeoutError:
                    emb3 = discord.Embed(title='Certo!',description='O cargo foi removido do usuário, mas não será removido completamente do servidor.',color=discord.Color.green())
                    await ctx.send('',embed=emb3)
                    await asyncio.sleep(5)
                    await ctx.channel.purge(limit=2)
            else:
                emb = discord.Embed(title='Hum...',description='Parece que o usuário não tem esse cargo.',color=discord.Color.blurple())
                await ctx.send('',embed=emb)
                await asyncio.sleep(3)
                return await ctx.channel.purge(limit=2)
        except asyncio.TimeoutError:
            await ctx.send("Eu não recebi uma confirmação, que tal tentar de novo?")
            await asyncio.sleep(3)
            return await ctx.channel.purge(limit=2)
    
    @r.error
    async def r_error(self, ctx, error):
        if isinstance(error, commands.MissingPermissions):
            await ctx.send("Você não tem permissão para usar este comando!")
            await asyncio.sleep(2)
            return await ctx.channel.purge(limit=2)
        elif isinstance(error, commands.BadArgument):
            await ctx.send("Parece que essa história não existe!")
            await asyncio.sleep(2)
            return await ctx.channel.purge(limit=2)
        elif isinstance(error, commands.BotMissingPermissions):
            await ctx.send("Parece que eu não tenho permissão para isso!")
            await asyncio.sleep(2)
            return await ctx.channel.purge(limit=2)
        elif isinstance(error, commands.CheckFailure):
            return await ctx.send(error)
        

def setup(client):
    client.add_cog(Role(client))