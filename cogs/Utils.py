import discord, asyncio, json, requests
from discord.ext import commands
import discord.utils
from discord.ext.commands.cooldowns import BucketType
from discord_components import DiscordComponents, ComponentsBot, Button, Select, SelectOption, ButtonStyle, Interaction
from bs4 import BeautifulSoup


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

class NoPrivateMessages(commands.CheckFailure):
    pass

def guild_only():
    async def predicate(ctx):
        if ctx.guild is None:
            raise NoPrivateMessages('Esse comando não pode ser usado em mensagens privadas!')
        return True
    return commands.check(predicate)


class Utils(commands.Cog, name='Utilidades'):

    def __init__(self, client):
        self.client = client
        with open('config.json', 'r', encoding='utf-8') as f:
            self.cfg = Config(json.loads(f.read()))

    @guild_only() # EDIT ROLE COLOR #
    @commands.command(name='novo', help='Adiciona permissões para novos autores ao usar `.novo <id-do-discord>`'
                                            ' __(campo de id do usuário é opcional, caso já seja autor ou autora)__ ')
    @commands.max_concurrency(1, per=BucketType.default, wait=False)
    @commands.has_any_role("Ajudante", "Equipe", "Administrador")
    async def release(self, ctx, member: str):
        if not member:
            return await ctx.send('Você não adicionou um autor.', delete_after=10)
        
        user = ctx.guild.get_member_named(member)
        await ctx.message.delete()
        
        if not user:
            return await ctx.send(f'Não encontrei ninguém com o nome "{member}".', delete_after=10)
        
        try:
            autorRole = discord.utils.get(ctx.guild.roles, id=self.cfg.aut_role)
            creatorRole = discord.utils.get(ctx.guild.roles, id=self.cfg.creat_role)
            markAuthorRole = discord.utils.get(ctx.guild.roles, id=self.cfg.mark_role)
            await user.add_roles(markAuthorRole, autorRole if not markAuthorRole in user.roles else autorRole)
            
            emb = discord.Embed(
                                    title='Deseja lançar uma nova história?',
                                    description='O ideal seria aguardar alguns segundos após publicar, para que o bot possa identificar a nova história',
                                    color=discord.Color.green()).set_footer(text='Use a reação para confirmar.')
            msg = await ctx.reply(embed=emb,
                                components = [[
                                    Button(style=ButtonStyle.green, label = "Sim", custom_id = "Aceitar", emoji="👌"),
                                    Button(style=ButtonStyle.red, label = "Não", custom_id = "Negar", emoji="👎")
                                ]])
            eqpRole = discord.utils.get(ctx.guild.roles, id=self.cfg.eqp_role)
            res  = await self.client.wait_for("button_click", check = lambda i: eqpRole in i.user.roles)
            if res.component.label == "Sim":
                try:
                    soup = BeautifulSoup(requests.get("http://kiniga.com/").text, 'lxml')
                    table = soup.find_all('div', attrs={'class': 'tab-content-wrap'})[3]
                    novel_recente = table.find_all('div', attrs={'class': 'page-item-detail'})[0]
                    t = novel_recente.find_all('div', attrs={'class': 'item-summary'})[0]
                    title = t.find('div', attrs={'class': 'post-title'})
                    if title:
                        try:
                            for l in title.find_all('a', href=True):
                                try:
                                    creators_channel = 694308861699686420
                                    novel = BeautifulSoup(requests.get(l['href']).text, 'lxml')
                                    link = l['href']  # link
                                    titulo = title.get_text()  # titulo da história
                                    author = novel.find('div', attrs={'class': 'author-content'}).find_all('a', href=True)[0]  # nome do autor
                                    s = novel.find('div', attrs={'class': 'summary__content'})  # sinopse da história
                                    sinopse = s.find('p').get_text()

                                    i = novel.find('div', attrs={'class': 'summary_image'}).find_all('img', {'class': 'img-responsive'})[0]  # img novel
                                    img = i.get('data-src')
                                    channel = discord.utils.get(self.client.get_all_channels(),
                                                                guild__name=self.cfg.guild,
                                                                id=self.cfg.chat_release)
                                    emb = discord.Embed(title="📢 NOVA OBRA PUBLICADA 📢", url=link,
                                                        color=discord.Color.green())
                                    emb = emb.set_author(name=author.get_text(), url=author['href'],
                                                        icon_url="https://kiniga.com/wp-content/uploads/fbrfg/favicon-32x32.png")
                                    emb = emb.set_thumbnail(url="https://kiniga.com/wp-content/uploads/fbrfg/favicon-32x32.png")
                                    emb = emb.add_field(name="Nome:", value=titulo, inline=False)
                                    emb = emb.add_field(name="Sinopse:", value=sinopse, inline=False)
                                    emb = emb.set_footer(text="Kiniga.com - O limite é a sua imaginação")
                                    emb = emb.set_image(url=img)
                                    await channel.send('\@everyone', embed=emb)
                                    channel_cmds = discord.utils.get(self.client.get_all_channels(),
                                                                guild__name=self.cfg.guild,
                                                                id=self.cfg.chat_cmds)
                                    await channel_cmds.send(f"{user.mention}, meus parabéns por se tornar um autor da Kiniga! \n"
                                                    f"Por favor, leia os fixados! E se tiver alguma dúvida relacionada a publicação, pergunte no <#{creators_channel}>")
                                    return await res.send("Feito.")
                                except Exception as e:
                                    await ctx.send(e)
                        except Exception as i:
                            await ctx.send(i)
                        
                except Exception as u:
                    await ctx.send(u)
            if res.component.label == "Não":
                emb = discord.Embed(
                                    description='Certo!',
                                    color=discord.Color.blue())
                await res.respond(embed=emb)
            await user.remove_roles(markAuthorRole, autorRole, creatorRole if not markAuthorRole in user.roles else autorRole, creatorRole)
            await asyncio.sleep(5)
            return await msg.delete()
            # Fim
        except Exception as e:
            return await ctx.reply(f"Ocorreu um erro \n ```{e}``` \n Tente novamente em alguns segundos.")
        
       
def setup(client):
    client.add_cog(Utils(client))
