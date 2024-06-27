import discord
from discord.ext import commands
import json

Debug_guild = [1235247721934360577]

blacklist_file = 'blacklist.json'

def load_data():
    with open(blacklist_file, 'r') as file:
        return json.load(file)

def save_data(data):
    with open(blacklist_file, 'w') as file:
        json.dump(data, file, indent=4)



class buyView(discord.ui.View):
    @discord.ui.button(label="購入する！", style=discord.ButtonStyle.primary)
    async def buy(self, button: discord.ui.Button, interaction):

        user = interaction.user.id

        await interaction.response.send_message(f"<@{user}>\n \n以下のチャンネルから送金を行ってください。\n<#974605382976696370>", ephemeral=True)

    @discord.ui.button(label="キャンセル", style=discord.ButtonStyle.red)
    async def buy2(self, button: discord.ui.Button, interaction):
        await interaction.response.send_message("購入をキャンセルしました。", ephemeral=True)



class buyland(commands.Cog):

    def __init__(self, bot):
        self.bot = bot

    async def get_state_type(ctx: discord.AutocompleteContext):
        global state_type
        state_type = ctx.options["state_type"]
        if state_type == "ライティングホルム":
            return ["20"]
        elif state_type == "ライティングホルム郊外":
            return ["10"]
        elif state_type == "ラティアファームズ":
            return ["1"]
        elif state_type == "サウススノーランド":
            return ["1"]
        elif state_type == "コンヴィア＝ウェスタリシア":
            return ["2"]
        else:
            return ["10"]

    @discord.slash_command(name="buyland", description="土地を買います。")
    async def buyland(self, ctx: discord.ApplicationContext, state_type: discord.Option(str, choices=["ライティングホルム", "ライティングホルム郊外", "ラティアファームズ", "サウススノーランド", "コンヴィア＝ウェスタリシア", "ヨークタウン"]), price: discord.Option(int, autocomplete=discord.utils.basic_autocomplete(get_state_type)), quantity: discord.Option(int, required=True, description="購入する個数を入力してください。")):

        user_id = str(ctx.author.id)

        data = load_data()

        cost = quantity * price

        if user_id not in data:
            embed = discord.Embed(title="土地購入", description="あなたは以下の内容で土地を購入しようとしています!\n最終確認をお願いします!")
            embed.add_field(name="購入する州", value=f"{state_type}")
            embed.add_field(name="1ブロック辺りの値段", value=f"{price}ノスタル")
            embed.add_field(name="購入数", value=f"{quantity}")
            embed.add_field(name="購入金額", value=f"{cost}")
            await ctx.response.send_message(embed=embed, view=buyView(), ephemeral=True)
        else:
            await ctx.response.send_message("あなたはブラックリストに登録されています。", ephemeral=True)


def setup(bot):
    bot.add_cog(buyland(bot))