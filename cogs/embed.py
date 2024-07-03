import discord
from discord.ext import commands
import discord.ui
import json

Debug_guild = [1235247721934360577]
main_guild = [962647934695002173, 1235247721934360577]

blacklist_file = 'blacklist.json'

def load_data():
    with open(blacklist_file, 'r') as file:
        return json.load(file)

def save_data(data):
    with open(blacklist_file, 'w') as file:
        json.dump(data, file, indent=4)

class EmbedModal(discord.ui.Modal):
    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)

        self.add_item(discord.ui.InputText(label="埋め込むメッセージを入力してください。", style=discord.InputTextStyle.long))


    async def callback(self, interaction: discord.Interaction):

        embed = discord.Embed(description=self.children[0].value, color=0xf1c40f)
        embed.set_author(name=f"{interaction.user.display_name}", icon_url=interaction.user.avatar.url)
        embed.add_field(name="", value="")

        await interaction.channel.send(embed=embed)
        await interaction.response.send_message("送信しました。", ephemeral=True)


class embed(commands.Cog):

    def __init__(self, bot):
        self.bot = bot

    @discord.slash_command(name="announce", description="メッセージを埋め込みにして送信します。", guild_ids=main_guild)
    @commands.has_permissions(administrator=True)
    async def embed(self, interaction: discord.ApplicationContext):
        user_id = str(interaction.author.id)

        data = load_data()

        if user_id not in data:
            modal = EmbedModal(title="Announceコマンド")
            await interaction.send_modal(modal)
            await interaction.respond("フォームでの入力を待機しています…", ephemeral=True)
        else:
            await interaction.response.send_message("あなたはブラックリストに登録されています。", ephemeral=True)

def setup(bot):
    bot.add_cog(embed(bot))