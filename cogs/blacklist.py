import discord
from discord.ext import commands
from discord.commands import SlashCommandGroup
from discord.ext.commands import NotOwner
import json

Debug_guild = [1235247721934360577]
main_guild = [962647934695002173, 1235247721934360577, 1256021750756544632]

blacklist_file = 'blacklist.json'

def load_blacklist_data():
    with open(blacklist_file, 'r') as file:
        return json.load(file)

def save_blacklist_data(data):
    with open(blacklist_file, 'w') as file:
        json.dump(data, file, indent=4)


class blacklist(commands.Cog):

    def __init__(self, bot):
        self.bot = bot


    blacklists = SlashCommandGroup("blacklist", "ブラックリストグループ")

    @blacklists.command(name="add", description="ユーザーをブラックリストに追加します。", guild_ids=main_guild)
    @commands.is_owner()
    async def a_blacklist(self, interaction: discord.ApplicationContext, user:discord.Member, reason: discord.Option(str, description="理由を入力します。")):
        b_id = str(interaction.author.id)

        data = load_blacklist_data()

        if b_id not in data:

            user_id = await self.bot.fetch_user(f"{user.id}")

            data = load_blacklist_data()

            if user_id not in data:
                await interaction.respond(f"{user.mention}をブラックリストに追加しました。", ephemeral=True)

                data[str(user.id)] = reason
                save_blacklist_data(data)
            else:
                await interaction.response.send_message("このユーザーはすでにブラックリストに追加されています。", ephemeral=True)
        else:
            await interaction.response.send_message("あなたはブラックリストに登録されています。", ephemeral=True)

    @a_blacklist.error
    async def adderror(ctx, error):
        if isinstance(error, NotOwner):
            await ctx.respond("あなたはこのコマンドを使用する権限を持っていません!", ephemeral=True)
        else:
            await ctx.respond("Something went wrong...", ephemeral=True)
        raise error



    @blacklists.command(name="show", description="ブラックリストを一覧表示します。", guild_ids=main_guild)
    @commands.is_owner()
    async def s_blacklist(self, interaction: discord.ApplicationContext):

        data = load_blacklist_data()

        try:
            with open(blacklist_file, 'r') as file:
                data = json.load(file)
        except FileNotFoundError:
            await interaction.send("データファイルが見つかりませんでした。")
            return

        data = load_blacklist_data()

        embed = discord.Embed(title="ブラックリストユーザー一覧")

        user_info = "\n".join([f"<@!{key}> : {value}" for key, value in data.items()])
        embed.add_field(name="ブラックリストユーザーの一覧です。", value=user_info, inline=False)

        await interaction.response.send_message(embed=embed, ephemeral=True)

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
        b_id = str(interaction.author.id)

        data = load_blacklist_data()

        if b_id not in data:
            user_id = str(user.id)
            if user_id in data:
                del data[user_id]
                save_blacklist_data(data)
                await interaction.response.send_message(f"{user.mention}をブラックリストから削除しました。", ephemeral=True)
            else:
                await interaction.response.send_message("このユーザーはブラックリストに登録されていません。", ephemeral=True)
        else:
            await interaction.response.send_message("あなたはブラックリストに登録されています。", ephemeral=True)

    @r_blacklist.error
    async def removeerror(ctx, error):
        if isinstance(error, NotOwner):
            await ctx.respond("あなたはこのコマンドを使用する権限を持っていません!", ephemeral=True)
        else:
            await ctx.respond("Something went wrong...", ephemeral=True)
        raise error





def setup(bot):
    bot.add_cog(blacklist(bot))