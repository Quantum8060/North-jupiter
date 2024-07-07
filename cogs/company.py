import discord
from discord.ext import commands
from discord.commands import SlashCommandGroup
import json

Debug_guild = [1235247721934360577]

company_file = 'company.json'

def load_company_data():
    with open(company_file, 'r') as file:
        return json.load(file)

def save_company_data(data):
    with open(company_file, 'w') as file:
        json.dump(data, file, indent=4)


class company(commands.Cog):

    def __init__(self, bot):
        self.bot = bot


    company = SlashCommandGroup("company", "ブラックリストグループ")

    @company.command(name="add", description="ユーザーをブラックリストに追加します。", guild_ids=Debug_guild)
    @commands.is_owner()
    async def a_blacklist(self, interaction: discord.ApplicationContext, user:discord.Member, reason: discord.Option(str, description="理由を入力します。")):
        b_id = str(interaction.author.id)

        data = load_company_data()

        if b_id not in data:

            user_id = await self.bot.fetch_user(f"{user.id}")

            data = load_company_data()

            if user_id not in data:
                await interaction.respond(f"{user.mention}をブラックリストに追加しました。", ephemeral=True)

                data[str(user.id)] = reason
                save_company_data(data)
            else:
                await interaction.response.send_message("このユーザーはすでにブラックリストに追加されています。", ephemeral=True)
        else:
            await interaction.response.send_message("あなたはブラックリストに登録されています。", ephemeral=True)

    @company.command(name="show", description="ブラックリストを一覧表示します。")
    @commands.is_owner()
    async def s_blacklist(self, interaction: discord.ApplicationContext):
        b_id = str(interaction.author.id)

        data = load_company_data()

        try:
            with open(company_file, 'r') as file:
                data = json.load(file)
        except FileNotFoundError:
            await interaction.send("データファイルが見つかりませんでした。")
            return

        user_id = str(interaction.author.id)

        data = load_company_data()

        embed = discord.Embed(title="ブラックリストユーザー一覧")

        user_info = "\n".join([f"<@!{key}> : {value}" for key, value in data.items()])
        embed.add_field(name="ブラックリストユーザーの一覧です。", value=user_info, inline=False)

        await interaction.response.send_message(embed=embed, ephemeral=True)



def setup(bot):
    bot.add_cog(company(bot))