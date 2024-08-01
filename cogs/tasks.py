import discord
from discord.ext import commands
import psutil
import datetime
from discord.ext.commands import NotOwner

Debug_guild = [1235247721934360577]

class tasks(commands.Cog):

    def __init__(self, bot):
        self.bot = bot

    @discord.slash_command(name='tasks', description="サーバーの使用状況を確認します。")
    @commands.is_owner()
    async def tasks(self, interaction: discord.ApplicationContext):

        time = datetime.datetime.fromtimestamp(psutil.boot_time()).strftime("%Y-%m-%d %H:%M:%S")

        embed = discord.Embed(title="サーバー状況", description="サーバーの状態を表示しています。", color=0x4169e1)
        embed.add_field(name="CPU使用率", value=f"{psutil.cpu_percent(interval=1)}％", inline=False)
        embed.add_field(name="メモリ使用率", value=f"{psutil.virtual_memory().percent}％", inline=False)
        embed.add_field(name="ストレージ使用率", value=f"{psutil.disk_usage('/').percent}％", inline=False)
        embed.add_field(name="サーバー起動時刻", value=f"{time}", inline=False)

        await interaction.response.send_message(embed=embed, ephemeral=True)

    @tasks.error
    async def taskserror(ctx, error):
        if isinstance(error, NotOwner):
            await ctx.respond("あなたはこのコマンドを使用する権限を持っていません!", ephemeral=True)
        else:
            await ctx.respond("Something went wrong...", ephemeral=True)
            raise error


def setup(bot):
    bot.add_cog(tasks(bot))