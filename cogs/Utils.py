import discord
import json
import requests
from discord.ext import commands
import discord.utils
from discord.ext.commands.cooldowns import BucketType
from discord_components import DiscordComponents, ComponentsBot, Button, Select, SelectOption, ButtonStyle, Interaction
from bs4 import BeautifulSoup


from base.struct import Config


class NoPrivateMessages(commands.CheckFailure):
    pass


def guild_only():
    async def predicate(ctx):
        if ctx.guild is None:
            raise NoPrivateMessages(
                'Esse comando não pode ser usado em mensagens privadas!')
        return True
    return commands.check(predicate)

class Utils(commands.Cog, name='Utilidades'):

    def __init__(self, client):
        self.client = client
        with open('config.json', 'r', encoding='utf-8') as f:
            self.cfg = Config(json.loads(f.read()))

    async def sendEmb(self, user, author):
        try:
            # to author
            welcome = discord.Embed(title=f"{user.name}, meus parabéns por se tornar um autor da Kiniga!",
                                    description="\n Leia as informações abaixo sobre como publicar capítulos "
                                                "no site e à quem recorrer para você não ficar perdido caso precise de ajuda.",
                                    color=0x00ff33).set_author(name="Kiniga Brasil",
                                                               url='https://kiniga.com/',
                                                               icon_url='https://kiniga.com/wp-content/uploads/fbrfg/favicon-32x32.png').set_footer(text='Espero que seja muito produtivo escrevendo!')
            # creators
            creators = discord.Embed(title='Clique aqui para ir ao canal dos criadores.',
                                     description='Lá, você poderá encontrar, nas mensagens fixadas, todas as informações necessárias'
                                     ' para a publicação de novos capítulos.',
                                     url='https://discord.com/channels/667838471301365801/694308861699686420',
                                     color=0x00ff33)
            # tags
            tags = discord.Embed(title='Clique aqui para ir ao canal das tags.',
                                 description='Lá, você poderá criar uma tag com o nome da sua história. O passo a passo também '
                                 'está nas mensagens fixadas.',
                                 url='https://discord.com/channels/667838471301365801/831561655329751062',
                                 color=0x00ff33)
            #  dúvidas
            dúvidas = discord.Embed(title='Clique aqui para ir ao canal das Perguntas Frequentes.',
                                    description='Lá, você encontrará um link para o documento que lista e explica qualquer '
                                                'dúvida que você possa ter sobre a comunidade.',
                                    url='https://discord.com/channels/667838471301365801/855526372403445830',
                                    color=0x00ff33)
            #  passos para fixados
            fixados = discord.Embed(title='Não sabe como acessar as mensagens fixadas?',
                                    description='Siga os passos da imagem abaixo.',
                                    color=0x00ff33
                                    ).set_image(url='https://media4.giphy.com/media/pURSYHBjYBEUhr04XQ/giphy.gif?cid=790b7611ecb81458c0064e87d5413028a19bfe17a95ed280&rid=giphy.gif&ct=g')
            #  novo projeto
            newProject = discord.Embed(title='Não entendeu como criar uma tag?',
                                       description='Siga o passo a passo abaixo para entender como solicitar a criação de uma tag '
                                       'para a sua história.',
                                       color=0x00ff33).set_image(url='https://media0.giphy.com/media/1IY0E9XoHQ2iJeLNwx/giphy.gif?cid=790b7611ed4435131498a759f83547158e2d9029c5e9b083&rid=giphy.gif&ct=g')

            return [welcome, creators, tags, dúvidas, fixados, newProject]

        except Exception as e:
            await author.send("Não foi possível prosseguir por conta do seguinte erro: \n\n"
                              "```{}``` \n\nPor favor, fale com o Shuichi".format(e))

    async def checkRelease(self):
        try:
            channel = discord.utils.get(self.client.get_all_channels(),
                                        guild__name=self.cfg.guild,
                                        id=self.cfg.chat_release)
            messages = await channel.history(limit=1).flatten()
            messages.reverse()
            for i, message in enumerate(messages):
                # print(message.embeds[0].to_dict())
                return message.embeds[0] if len(message.embeds) >= 1 else message.content
        except Exception as i:
            raise i

    async def getRelease(self, author):
        soup = BeautifulSoup(requests.get("http://kiniga.com/").text, 'lxml')
        table = soup.find_all('div', attrs={'class': 'tab-content-wrap'})[3]
        novel_recente = table.find_all(
            'div', attrs={'class': 'page-item-detail'})[0]
        t = novel_recente.find_all('div', attrs={'class': 'item-summary'})[0]
        title = t.find('div', attrs={'class': 'post-title'})
        if title:
            try:
                for l in title.find_all('a', href=True):
                    try:
                        novel = BeautifulSoup(
                            requests.get(l['href']).text, 'lxml')
                        link = l['href']  # link
                        titulo = title.get_text()  # titulo da história
                        author = novel.find('div', attrs={'class': 'author-content'}
                                            ).find_all('a', href=True)[0]  # nome do autor
                        # sinopse da história
                        s = novel.find(
                            'div', attrs={'class': 'summary__content'})
                        sinopse = s.find('p').get_text()

                        i = novel.find('div', attrs={'class': 'summary_image'}
                                       ).find_all('img', {'class': 'img-responsive'})[0]  # img novel
                        img = i.get('data-src')

                        emb = discord.Embed(title="📢 NOVA OBRA PUBLICADA 📢", 
                                            url=link,
                                            color=discord.Color.green())
                        emb = emb.set_author(
                            name=author.get_text(),
                            url=author['href'],
                            icon_url="https://kiniga.com/wp-content/uploads/fbrfg/favicon-32x32.png"
                        )
                        emb = emb.set_thumbnail(
                            url="https://kiniga.com/wp-content/uploads/fbrfg/favicon-32x32.png"
                        )
                        emb = emb.add_field(
                            name="Nome:",
                            value=titulo,
                            inline=False
                        )
                        emb = emb.add_field(
                            name="Sinopse:",
                            value=sinopse,
                            inline=False
                        )
                        emb = emb.set_footer(
                            text="Kiniga.com - O limite é a sua imaginação"
                        )
                        emb = emb.set_image(
                            url=img
                        )
                        
                        try:
                            oldEmb = await self.checkRelease()
                            
                            # print("*" * 20)
                            # print( oldEmb.get('url') )
                            # print("*" * 20)
                            # print( emb.to_dict().get('url') )
                            try:
                                if emb.to_dict().get('url') == oldEmb.to_dict().get('url'):
                                    emb = discord.Embed(
                                            title="Ops",
                                            description="Essa história Já Foi Publicada!",
                                            color=0x00ff33).set_author(
                                            name="Kiniga Brasil",
                                            url='https://kiniga.com/',
                                            icon_url='https://kiniga.com/wp-content/uploads/fbrfg/favicon-32x32.png'
                                        ).set_footer(text='Qualquer coisa, marque o Shuichi! :D')
                                    
                            except:
                                pass
                              
                            return emb
                        except Exception as a:
                            
                            print(a)
                            return discord.Embed(title=f"Erro!",
                                                 description="\nUm erro ocorreu devido ao seguinte problema: \n\n{}.".format(
                                                     a),
                                                 color=0x00ff33).set_author(
                                                                    name="Kiniga Brasil",
                                                                    url='https://kiniga.com/',
                                                                    icon_url='https://kiniga.com/wp-content/uploads/fbrfg/favicon-32x32.png'
                                                                ).set_footer(text='Qualquer coisa, marque o Shuichi! :D')

                        # channel_cmds = discord.utils.get(self.client.get_all_channels(),
                        #                            guild__name=self.cfg.guild,
                        #                            id=self.cfg.chat_cmds)
                    except Exception as i:
                        await author.send("Não foi possível prosseguir por conta do seguinte erro: \n\n"
                                          "```{}``` \n\nPor favor, fale com o Shuichi".format(i))
            except Exception as u:
                await author.send("Não foi possível prosseguir por conta do seguinte erro: \n\n"
                                  "```{}``` \n\nPor favor, fale com o Shuichi".format(u))

    @guild_only()  # SEND NEW PROJECT #
    @commands.command(name='novo', help='Adiciona permissões para novos autores ao usar `.novo <id-do-discord>`'
                      ' __(campo de id do usuário é opcional, caso já seja autor ou autora)__ ')
    @commands.max_concurrency(1, per=BucketType.default, wait=False)
    @commands.has_any_role("Ajudante", "Equipe", "Administrador", "Editores")
    async def release(self, ctx, member: str = None):
        # author = await self.fetch_user(ctx.author.id)
        if not member:
            await ctx.message.delete()
            return await ctx.send('Você não adicionou um autor.', delete_after=5)

        user = ctx.guild.get_member_named(member)

        if not user:
            await ctx.message.delete()
            return await ctx.send(f'Não encontrei ninguém com o nome "{member}".', delete_after=5)

        try:
            autorRole = discord.utils.get(ctx.guild.roles,
                                          id=self.cfg.aut_role)
            creatorRole = discord.utils.get(ctx.guild.roles,
                                            id=self.cfg.creat_role)
            markAuthorRole = discord.utils.get(ctx.guild.roles,
                                               id=self.cfg.mark_role)
            eqpRole = discord.utils.get(ctx.guild.roles,
                                        id=self.cfg.eqp_role)
            channel = discord.utils.get(self.client.get_all_channels(),
                                        guild__name=self.cfg.guild,
                                        id=self.cfg.chat_release)

            embb = discord.Embed(title='Deseja lançar uma nova história?',
                                 description='O ideal seria aguardar alguns segundos após publicar, para que o bot possa identificar a nova história',
                                 color=discord.Color.green()).set_footer(text='Use a reação para confirmar.')

            msg = await ctx.message.author.send(embed=embb,
                                                components=[[
                                                    Button(
                                                        style=ButtonStyle.green, label="Sim", custom_id="Aceitar", emoji="👌"),
                                                    Button(
                                                        style=ButtonStyle.red, label="Não", custom_id="Negar", emoji="👎")
                                                ]])
            
            try:
                releaseMessage = await self.getRelease(author=ctx.message.author)
                userMessages = await self.sendEmb(user=user, author=ctx.message.author)
            except Exception as i:
                raise i 
            
            # eqpRole in i.user.roles and
            res = await self.client.wait_for("button_click", check=lambda i: i.message.id == msg.id)

            if res.component.label == "Sim":
                try:
                    if releaseMessage.title == "Ops":
                        await ctx.message.delete()
                        await msg.delete()
                        return await res.respond(embed=releaseMessage, components=[])
                    
                                                          
                    else:
                        await channel.send(embed=releaseMessage)

                        await user.add_roles(markAuthorRole, autorRole if not markAuthorRole in user.roles else autorRole)

                        await user.send(embeds=userMessages)
                        
                        releaseMessage = discord.Embed(
                            title=f"História Publicada!",
                            color=0x00ff33).set_author(
                            name="Kiniga Brasil",
                            url='https://kiniga.com/',
                            icon_url='https://kiniga.com/wp-content/uploads/fbrfg/favicon-32x32.png'
                        ).set_footer(text='Qualquer coisa, marque o Shuichi! :D')
                    
                        ## Fazer um doc de errors para embeds ##

                except Exception as u:
                    return await ctx.message.author.send(content=u)

                await res.respond(embed=releaseMessage, components=[])
                
            if res.component.label == "Não":
                emb = discord.Embed(
                    description='Certo!',
                    color=discord.Color.blue())
                await res.respond(embed=emb, components=[])
                try:
                    await user.remove_roles(markAuthorRole, autorRole, creatorRole
                                            if not markAuthorRole in user.roles
                                            else autorRole, creatorRole)
                except Exception as a:
                    await ctx.send("Não consegui finalizar por conta do seguinte erro: "
                                   "\n{} \n\n Marca o Jonathan aí.".format(a), delete_after=15)
        # Fim
        except Exception as e:
            await ctx.message.author.send(f"Ocorreu um erro \n ```{e}``` \n Tente novamente em alguns segundos.", delete_after=5)

        await ctx.message.delete()
        await msg.delete()


def setup(client):
    client.add_cog(Utils(client))
