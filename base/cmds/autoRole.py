import discord, asyncio, json
from discord.ext import commands
import discord.utils
from discord.ext.commands.cooldowns import BucketType

from base.struct import Config

from base.views import defaultViewButton

class NoPrivateMessages(commands.CheckFailure):
    pass

def guild_only():
    async def predicate(ctx):
        if ctx.guild is None:
            raise NoPrivateMessages('Esse comando não pode ser usado em mensagens privadas!')
        return True
    return commands.check(predicate)


class Role(commands.Cog, name='Cargos'):

    def __init__(self, bot: commands.Bot):
        self.bot = bot
        with open('config.json', 'r', encoding='utf-8') as f:
            self.cfg = Config(json.loads(f.read()))

    @guild_only() # EDIT ROLE COLOR #
    @commands.command(name='editar', help='Edita um determinado cargo ao digitar `.editar <história> <usuário>` __(campo usuário é opcional)__ ')
    @commands.max_concurrency(1, per=BucketType.default, wait=False)
    @commands.has_any_role("Autor(a)", "Criador(a)", "Ajudante", "Equipe")
    async def editar(self, ctx, role: discord.Role, colour: discord.Colour = None, *, name = None):
        autorRole = discord.utils.get(ctx.guild.roles, id=role.id)
        markAuthorRole = discord.utils.get(ctx.guild.roles, id=self.cfg.mark_role)
        if autorRole:
            if not autorRole.is_default() and autorRole.position < markAuthorRole.position:
                await autorRole.edit(colour = colour)
                if name != None:
                    content = ("").join(name)
                    await autorRole.edit(name = content)

                embed = discord.Embed(
                    description = (f'As mudanças em {autorRole.mention} foram aplicadas.'),
                    colour = colour
                )
                await ctx.send('', embed=embed)
            else:
                await ctx.send("Você não pode editar um cargo superior ao seu.", delete_after=5)
    
    @editar.error
    async def editar_error(self, ctx, error):
        if isinstance(error, commands.BadColourArgument):
            role = [i for i in ctx.message.content.split()]
            
            try:
                if role[3]:
                    name = role[3]
                else:
                    name=  None
            except: name = None
                
            await ctx.send(f"O correto seria: \n\n.projeto **#**{error.argument} {name if name != None else ''}", delete_after=10)

    @guild_only() # GET PROJECT ROLE #
    @commands.command(name='projeto', help='Recebe um determinado cargo ao digitar `.projeto <história> <usuário>` __(campo usuário é opcional)__ ')
    @commands.max_concurrency(1, per=BucketType.default, wait=False)
    @commands.has_any_role("Autor(a)", "Criador(a)", "Ajudante", "Equipe")
    async def projeto(self, ctx, role: discord.Role, member: discord.Member = None):
        channel = ctx.guild.get_channel(self.cfg.chat_cmds)
        markAuthorRole = discord.utils.get(ctx.guild.roles, id=self.cfg.mark_role)
        if ctx.message.channel == channel:
            member = member or ctx.author
            role_id = role.id
            autorRole = discord.utils.get(ctx.guild.roles, id=role_id)
            eqpRole = discord.utils.get(ctx.guild.roles, id=self.cfg.eqp_role)
            emb = discord.Embed(
                description='O cargo %s já existe, deseja adicioná-lo?!' % (autorRole.mention),
                color=discord.Color.blue()
            )

            view = defaultViewButton()
            await ctx.send(embed=emb, view=view)
            await view.wait()
            #await msg.add_reaction('✅')
            await ctx.message.delete()
            if view.value == "sim":
                if role in member.roles:
                    emb4 = discord.Embed(
                        description='Parece que {} já tem esse cargo.'.format(member.mention),
                        color=discord.Color.orange()
                    )
                    await ctx.send(embed=emb4)
                else:
                    emb = discord.Embed(
                        description='O cargo %s será recebido assim que alguém da equipe reagir à essa mensagem!' % (autorRole.mention),
                    )
                    await ctx.send(embed=emb,view=view)

                    view  = await self.bot.wait_for("button_click", check = lambda i: eqpRole in i.user.roles)
                    if view.value == "sim":
                        if markAuthorRole in member.roles:
                            await member.add_roles(autorRole)
                        else:
                            await member.add_roles(autorRole, markAuthorRole)
                        emb4 = discord.Embed(
                            description='O cargo **{}** foi adicionado, e agora você é autor!'.format(autorRole.mention),color=discord.Color.dark_blue()
                        )
                        await view.respond(embed=emb4)
                    if view.value == "nao":
                        await ctx.send("História recusada.")
            if view.component.label == "Não":
                await ctx.send("Tudo bem!")

    @projeto.error
    async def projeto_error(self, ctx, error):
        if isinstance(error, commands.RoleNotFound):
            if ctx.message.channel == ctx.guild.get_channel(self.cfg.chat_cmds):
                eqpRole = discord.utils.get(ctx.guild.roles, id=self.cfg.eqp_role)
                markAuthorRole = discord.utils.get(ctx.guild.roles, id=self.cfg.mark_role)
                channel = discord.utils.get(
                            self.bot.get_all_channels(), 
                            guild__name=self.cfg.guild, 
                            id=self.cfg.chat_creators)
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

                aRole = []
                a_clean = []

                if text:
                    a = str(text)
                    a = a.replace('"', '')
                    a = a.replace("projeto", "")
                    a_clean = a
                    role_guild = discord.utils.get(ctx.guild.roles, name=a_clean)
                    if role_guild:
                        aRole = ctx.guild.get_role(int(role_guild.id))
                    else:
                        pass
                else:
                    await ctx.send("Você precisa digitar alguma coisa, meu querido.", delete_after=5)
                await ctx.message.delete()
                emb = discord.Embed(
                    description='%s, o cargo %s será criado assim que '
                    'alguém da equipe reagir à essa mensagem!' % (member.mention, a_clean),
                    color=discord.Color.blue())
                await view.wait()
                msg = await ctx.send(embed=emb,)
                if view.value == "sim":
                    if aRole:
                        emb = discord.Embed(
                            description='O cargo **{}** já existe, deseja adicioná-lo?!'.format(aRole),
                            color=discord.Color.dark_blue()).set_footer(text='Use a reação para confirmar.')
                        await ctx.send(embed=emb)
                        await view.wait()
                        if view.value == "sim":
                            if aRole in member.roles:
                                emb4 = discord.Embed(
                                    description='Parece que {} já tem esse cargo.'.format(member.mention)
                                )
                                return await ctx.send(embed=emb4)
                            else:
    
                                emb = discord.Embed(
                                    description='{}, o cargo **{}** será recebido assim que alguém da equipe reagir à essa mensagem!'.format(member, aRole)
                                )
                                await ctx.send(embed=emb)
                                res  = await self.bot.wait_for("button_click", check = lambda i: eqpRole in i.user.roles)
                                if view.value == "sim":
                                    if markAuthorRole in member.roles:
                                        await member.add_roles(aRole)
                                    else:
                                        await member.add_roles(aRole, markAuthorRole)
                                    emb4 = discord.Embed(
                                        description='{} foi criado(a), e agora você é autor(a)!\nQualquer dúvida, leia o canal {}.'.format(aRole, channel.mention),
                                        color=discord.Color.green()
                                        ).set_footer(text='Espero que seja muito produtivo escrevendo!')
                                    await ctx.send(embed=emb4)
                                if view.value == "nao":
                                    await ctx.send("Tudo bem!")
                        if view.value == "nao":
                            await ctx.send("Tudo bem!")
                    else:
                        nRole = await ctx.guild.create_role(name=a_clean.title(), reason="Nova história!", mentionable=True)
                        if markAuthorRole in member.roles:
                            await member.add_roles(nRole)
                        else:
                            await member.add_roles(nRole, markAuthorRole)
                        emb6 = discord.Embed(
                            description='{} foi criado(a), e agora você é autor(a)! \nQualquer dúvida, leia o canal {}'.format(nRole.mention, channel.mention),
                            color=discord.Color.green()
                            ).set_footer(text='Espero que seja muito produtivo escrevendo!')
                        await ctx.send(embed=emb6)
                if view.value == "Não":
                    await ctx.send("História recusada.")

                await msg.delete()

        elif isinstance(error, commands.MaxConcurrencyReached):
            await ctx.send("Já tem uma história na fila, você deve aguardar a sua vez.", delete_after=5)
        elif isinstance(error, commands.BotMissingPermissions):
            await ctx.send("Parece que eu não tenho permissão para isso!", delete_after=5)
        elif isinstance(error, commands.MissingPermissions):
            await ctx.send("Parece que você não tenho permissão para isso!", delete_after=5)
        elif isinstance(error, commands.CheckFailure):
            await ctx.send(error) 

    @guild_only() # REMOVE PROJECT ROLE #
    @commands.command(name='r', help='Deletar história ao digitar `.r <cargo> <usuário>` __(campo usuário é opcional)__ ')
    @commands.has_permissions(manage_roles=True)
    async def r(self, ctx, role: discord.Role = None, member: discord.Member = None, reason=None):
        channel = ctx.guild.get_channel(self.cfg.chat_cmds)
        autorRole = discord.utils.get(ctx.guild.roles, id=role.id)
        eqprole = discord.utils.get(ctx.guild.roles, id=self.cfg.eqp_role)
        #autorRole = discord.utils.get(ctx.guild.roles, id=self.cfg.mark_role)
        if ctx.message.channel == channel:
            member = member or ctx.author

            if not autorRole:
                return await ctx.send("Você precisa digitar o nome ou marcar algum cargo!", delete_after=5)

            emb = discord.Embed(
                description='Deseja remover de {}?'.format(member.mention),
                color=discord.Color.red()).set_footer(text='Use a reação para confirmar')
            view = defaultViewButton()
            msg = await ctx.send(embed=emb, view=view)
            await ctx.message.delete()
            if view.value == "Sim":
                try:
                    await member.remove_roles(autorRole)
                except Exception as e:
                    await ctx.send('Ocorreu um erro. \n %s', e)
                    await ctx.send(e)
                if eqprole in member.roles:
                    emb = discord.Embed(
                        description='Deseja remover do servidor? \nEssa ação não pode ser desfeita!',
                        color=discord.Color.red()
                    )
                    if view.value == "sim":
                        await autorRole.delete(reason="Hitória removida.")
                        emb2 = discord.Embed(
                            title='História removida!',
                            description='Espero que não se arrependa...',
                            color=discord.Color.dark_blue()
                        )
                        await ctx.send(embed=emb2)

                    if view.value == "nao":
                        emb3 = discord.Embed(
                            description='O cargo foi removido do usuário, mas não será removido completamente do servidor.',
                            color=discord.Color.blue())
                        await res.send(embed=emb3)
            if view.value == "nao":
                emb = discord.Embed(
                    description='Certo!',
                    color=discord.Color.blue()
                    )
                await ctx.send(embed=emb, delete_after=2)
            await msg.delete()


    @r.error
    async def r_error(self, ctx, error):
        if isinstance(error, commands.MissingPermissions):
            await ctx.send("Você não tem permissão para usar este comando!", delete_after=5)
        elif isinstance(error, commands.BadArgument):
            await ctx.send("Parece que essa história não existe!", delete_after=5)
        elif isinstance(error, commands.BotMissingPermissions):
            await ctx.send("Parece que eu não tenho permissão para isso!", delete_after=5)
        elif isinstance(error, commands.CheckFailure):
            await ctx.send(error)


async def setup(bot: commands.Bot) -> None:
    # , guilds=[ discord.Object(id=943170102759686174), discord.Object(id=1010183521907789977)]
    await bot.add_cog(Role(bot))