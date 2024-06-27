import discord
from discord.ext import commands
import discord.ui
from discord.ext.commands import NotOwner

Debug_guild = [1235247721934360577]

class dmModal(discord.ui.Modal):
    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)

        self.add_item(discord.ui.InputText(label="タイトルを入力してください。", style=discord.InputTextStyle.short))
        self.add_item(discord.ui.InputText(label="送信内容を入力してください。", style=discord.InputTextStyle.long))
        self.add_item(discord.ui.InputText(label="送信先のユーザーのIDを入力してください。", style=discord.InputTextStyle.short))

    async def callback(self, interaction: discord.Interaction):


        embed = discord.Embed(title=self.children[0].value, description=self.children[1].value, color=0x9b59b6)
        embed.add_field(name="", value="")
        embed.set_footer(icon_url=interaction.user.avatar.url, text=f"{interaction.user.name}")
        user = await self.bot.fetch_user(f"{self.children[2].value}")
        await user.send(embeds=[embed])
        await interaction.response.send_message("送信しました。", ephemeral=True)

class dm(commands.Cog):

    def __init__(self, bot):
        self.bot = bot

    @discord.slash_command(name="dm", description="指定したユーザーにDMを送信します。")
    @commands.is_owner()
    async def dm(self, interaction: discord.ApplicationContext):

        modal = dmModal(title="DM送信用フォーム")
        await interaction.send_modal(modal)
        await interaction.respond("フォームでの入力を待機しています…", ephemeral=True)

    @dm.error
    async def dmerror(self, ctx, error):
        if isinstance(error, NotOwner):
            await ctx.respond("あなたはこのコマンドを使用する権限を持っていません!", ephemeral=True)
        else:
            await ctx.respond("Something went wrong...", ephemeral=True)
            raise error

def setup(bot):
    bot.add_cog(dm(bot))