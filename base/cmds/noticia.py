import discord, asyncio, json
from discord.ext import commands
import requests
from bs4 import BeautifulSoup

class NoPrivateMessages(commands.CheckFailure):
    pass

def guild_only():
    async def predicate(ctx):
        if ctx.guild is None:
            return
        return True
    return commands.check(predicate)

class Noticia(commands.Cog):

    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.cfg = self.bot.config["config"]
    
    @guild_only()
    @commands.command(name='aaaa', help='Anuncia o lançamento mais recente ao digitar `.novo` ')
    @commands.has_permissions(manage_webhooks=True)
    async def release(self, ctx, member: str):
        await self.bot.wait_until_ready()
        await ctx.message.delete()
        
        user = await ctx.guild.get_member_named(member)
        
        if not user:
            return await ctx.send(f'Não encontrei ninguém com o nome "{member}".', delete_after=10)
        
        try:
            await user.add_roles((self.cfg["mark_role"], self.cfg["eqp_role"]) if not (self.cfg["mark_role"]) in user.roles else (self.cfg["eqp_role"]))
        except Exception as e:
            await ctx.send(f"Ocorreu um erro \n ```{e}```")
        
        while not self.bot.is_closed():
            soup = BeautifulSoup(requests.get("http://kiniga.com/").text, 'lxml')
            table = soup.find_all('div', attrs={'class': 'tab-content-wrap'})[3]
            novel_recente = table.find_all('div', attrs={'class': 'page-item-detail'})[0]
            t = novel_recente.find_all('div', attrs={'class': 'item-summary'})[0]
            title = t.find('div', attrs={'class': 'post-title'})
            if title:
                try:
                    for l in title.find_all('a', href=True):
                        try:
                            novel = BeautifulSoup(requests.get(l['href']).text, 'lxml')
                            link = l['href']  # link
                            titulo = title.get_text()  # titulo da história
                            author = novel.find('div', attrs={'class': 'author-content'}).find_all('a', href=True)[0]  # nome do autor
                            s = novel.find('div', attrs={'class': 'summary__content'})  # sinopse da história
                            sinopse = s.find('p').get_text()

                            i = novel.find('div', attrs={'class': 'summary_image'}).find_all('img', {'class': 'img-responsive'})[0]  # img novel
                            img = i.get('data-src')
                            channel = discord.utils.get(self.bot.get_all_channels(),
                                                        guild__name=self.cfg["guild"],
                                                        id=self.cfg["chat_release"])
                            emb = discord.Embed(title="📢 NOVA OBRA PUBLICADA 📢", url=link,
                                                color=discord.Color.green())
                            emb = emb.set_author(name=author.get_text(), url=author['href'],
                                                 icon_url="https://kiniga.com/wp-content/uploads/fbrfg/favicon-32x32.png")
                            emb = emb.set_thumbnail(url="https://kiniga.com/wp-content/uploads/fbrfg/favicon-32x32.png")
                            emb = emb.add_field(name="Nome:", value=titulo, inline=False)
                            emb = emb.add_field(name="Sinopse:", value=sinopse, inline=False)
                            emb = emb.set_footer(text="Kiniga.com - O limite é a sua imaginação")
                            emb = emb.set_image(url=img)
                            return await channel.send('\@everyone', embed=emb)
                        except Exception as e:
                            raise e
                except Exception as i:
                    raise i

async def setup(bot: commands.Bot) -> None:
    # , guilds=[ discord.Object(id=943170102759686174), discord.Object(id=1010183521907789977)]
    await bot.add_cog(Noticia(bot))