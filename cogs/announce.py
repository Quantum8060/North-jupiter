import discord
from discord.ext import commands
import discord.ui
import json
from discord.ext.commands import MissingAnyRole

Debug_guild = [1235247721934360577]
main_guild = [962647934695002173, 1235247721934360577]



announce_file = 'announce.json'

def load_data():
    with open(announce_file, 'r') as file:
        return json.load(file)

def save_data(data):
    with open(announce_file, 'w') as file:
        json.dump(data, file, indent=4)



class announce(commands.Cog):

    def __init__(self, bot):
        self.bot = bot

    @discord.slash_command(name="announce_t", description="メッセージを埋め込みにして送信します。", guild_ids=main_guild)
    @commands.has_permissions(administrator=True)
    async def announce_t(self, interaction: discord.ApplicationContext):
        user_id = str(interaction.author.id)

        data = load_data()
        if user_id not in data:
            await interaction.respond("アナウンスモードになりました。", ephemeral=True)

            data[str(interaction.author.id)] = user_id
            save_data(data)
        elif user_id in data:
            del data[user_id]
            save_data(data)
            await interaction.response.send_message("アナウンスモードを終了しました。", ephemeral=True)

    @announce_t.error
    async def embederror(ctx, error):
        if isinstance(error, MissingAnyRole):
            await ctx.respond("あなたはこのコマンドを使用する権限を持っていません!", ephemeral=True)
        else:
            await ctx.respond("Something went wrong...", ephemeral=True)
            raise error

def setup(bot):
    bot.add_cog(announce(bot))