import discord
from discord.ext import commands
from discord.ext.commands import MissingPermissions
import json

Debug_guild = [1235247721934360577]

blacklist_file = 'blacklist.json'

def load_data():
    with open(blacklist_file, 'r') as file:
        return json.load(file)

def save_data(data):
    with open(blacklist_file, 'w') as file:
        json.dump(data, file, indent=4)



class clear(commands.Cog):

    def __init__(self, bot):
        self.bot = bot

    @discord.slash_command(name="clear", description="指定された数のメッセージを削除します。")
    @commands.has_permissions(administrator = True)
    async def clear(self, interaction: discord.ApplicationContext, num: discord.Option(str, required=True, description="削除するメッセージ数を入力")):
        user_id = str(interaction.author.id)

        data = load_data()

        if user_id not in data:
            async for message in interaction.channel.history(limit=int(num)):
                await message.delete(delay=1.2)

            embed=discord.Embed(title="メッセージ削除", description=f"{num}メッセージを削除しました。", color=0x4169e1)
            embed.add_field(name="", value="")
            await interaction.respond(embeds=[embed], ephemeral=True)
        else:
            await interaction.response.send_message("あなたはブラックリストに登録されています。", ephemeral=True)

    @clear.error
    async def clearerror(ctx, error):
        if isinstance(error, MissingPermissions):
            await ctx.respond("あなたはこのコマンドを使用する権限を持っていません!", ephemeral=True)
        else:
            await ctx.respond("Something went wrong...", ephemeral=True)
        raise error



def setup(bot):
    bot.add_cog(clear(bot))
