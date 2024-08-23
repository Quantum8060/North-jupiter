import discord
from discord.ext import commands
from discord.commands import SlashCommandGroup
from discord.ext.commands import NotOwner
import sqlite3
from discord.ext.pages import Paginator, Page

Debug_guild = [1235247721934360577]
main_guild = [962647934695002173, 1235247721934360577, 1256021750756544632]

conn = sqlite3.connect('users.db')
c = conn.cursor()

c.execute('''CREATE TABLE IF NOT EXISTS users
             (id TEXT PRIMARY KEY, cash INTEGER )''')
c.execute('''CREATE TABLE IF NOT EXISTS blacklist
             (id TEXT PRIMARY KEY, cash INTEGER)''')

conn.commit()


def get_user_info(user_id):
    c.execute("SELECT id, cash FROM users WHERE id = ?", (user_id,))
    return c.fetchone()

def save_blacklist(blacklist_id, cash):
    with conn:
        c.execute("INSERT OR IGNORE INTO blacklist (id, cash) VALUES (?, ?)", (blacklist_id, cash))
        c.execute("UPDATE blacklist SET cash = ? WHERE id = ?", (cash, blacklist_id))

def get_all_blacklist():
    c.execute("SELECT id, cash FROM blacklist")
    return c.fetchall()

def get_blacklist_info(blacklist_id):
    c.execute("SELECT id, cash FROM blacklist WHERE id = ?", (blacklist_id,))
    return c.fetchone()



class blacklist(commands.Cog):

    def __init__(self, bot):
        self.bot = bot


    blacklists = SlashCommandGroup("blacklist", "ブラックリストグループ")

    @blacklists.command(name="add", description="ユーザーをブラックリストに追加します。", guild_ids=main_guild)
    @commands.is_owner()
    async def a_blacklist(self, interaction: discord.ApplicationContext, user:discord.Member):

        user_id = str(user.id)
        user_info = get_blacklist_info(user_id)
        user_bal = get_user_info(user.id)

        user_id = await self.bot.fetch_user(f"{user.id}")

        if user_info:
            await interaction.response.send_message("このユーザーはすでにブラックリストに追加されています。", ephemeral=True)
        else:
            user_id = str(user.id)
            cash = int(user_bal[1])
            save_blacklist(user_id, cash)
            await interaction.respond(f"{user.mention}をブラックリストに追加しました。", ephemeral=True)

    @a_blacklist.error
    async def adderror(ctx, error):
        if isinstance(error, NotOwner):
            await ctx.respond("あなたはこのコマンドを使用する権限を持っていません!", ephemeral=True)
        else:
            await ctx.respond("Something went wrong...", ephemeral=True)
        raise error



    @blacklists.command(name="show", description="ブラックリストを一覧表示します。", guild_ids=main_guild)
    @commands.is_owner()
    async def s_blacklist(self, ctx: discord.ApplicationContext):

        blacklist = get_all_blacklist()

        if not blacklist:
            await ctx.respond("ブラックリストにユーザーが登録されていません。", ephemeral=True)
            return

        embeds = []
        for i in range(0, len(blacklist), 5):
            embed = discord.Embed(title="ブラックリスト", color=0x00ff00)
            for blacklist_id, cash in blacklist[i:i+5]:
                embed.add_field(name=f"ユーザー: {blacklist_id}", value=f"所持金: {cash}", inline=False)
            embeds.append(embed)

        paginator = Paginator(pages=embeds, use_default_buttons=True, timeout=60)
        await paginator.respond(ctx.interaction, ephemeral=True)

    @s_blacklist.error
    async def showerror(ctx, error):
        if isinstance(error, NotOwner):
            await ctx.respond("あなたはこのコマンドを使用する権限を持っていません!", ephemeral=True)
        else:
            await ctx.respond("Something went wrong...", ephemeral=True)
        raise error



    @blacklists.command(name="remove", description="ブラックリストからユーザーを削除します。", guild_ids=main_guild)
    @commands.is_owner()
    async def r_blacklist(self, interaction: discord.ApplicationContext, user: discord.Member):

        user_id = str(user.id)
        user_info = get_blacklist_info(user_id)

        user_id = str(user.id)
        if user_info:
            c.execute(f"""DELETE FROM blacklist WHERE id="{user_id}";""")
            conn.commit()

            await interaction.response.send_message(f"{user.mention}をブラックリストから削除しました。", ephemeral=True)

        else:
            await interaction.response.send_message("このユーザーはブラックリストに登録されていません。", ephemeral=True)

    @r_blacklist.error
    async def removeerror(ctx, error):
        if isinstance(error, NotOwner):
            await ctx.respond("あなたはこのコマンドを使用する権限を持っていません!", ephemeral=True)
        else:
            await ctx.respond("Something went wrong...", ephemeral=True)
        raise error





def setup(bot):
    bot.add_cog(blacklist(bot))