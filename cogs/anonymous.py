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



class anonymous(commands.Cog):

    def __init__(self, bot):
        self.bot = bot

    @discord.slash_command(name='anonymous', description="匿名で送信します。")
    @commands.cooldown(1, 10, commands.BucketType.user)
    async def anonymous(self, interaction: discord.ApplicationContext, text: discord.Option(discord.SlashCommandOptionType.string, description="匿名メッセージを送信します。") =None, picture: discord.Attachment = None):
        user_id = str(interaction.author.id)

        data = load_data()

        if user_id not in data:
            if text and picture:
                embed=discord.Embed()
                embed.add_field(name="", value=f"{text}", inline=True)
                embed.set_image(url=picture.url)

                await interaction.respond("匿名メッセージを送信しました。", ephemeral=True)
                await interaction.channel.send(embed=embed)

                log_c = await self.bot.fetch_channel("1266555623722451027")

                await log_c.send(f"anonymousコマンド使用\nuser:{interaction.user.display_name}", embed=embed)
            elif text:
                embed=discord.Embed()
                embed.add_field(name="", value=f"{text}", inline=True)

                await interaction.respond("匿名メッセージを送信しました。", ephemeral=True)
                await interaction.channel.send(embed=embed)

                log_c = await self.bot.fetch_channel("1266555623722451027")

                await log_c.send(f"anonymousコマンド使用\nuser:{interaction.user.display_name}", embed=embed)
            elif picture:
                embed=discord.Embed()
                embed.set_image(url=picture.url)

                await interaction.respond("匿名メッセージを送信しました。", ephemeral=True)
                await interaction.channel.send(embed=embed)

                log_c = await self.bot.fetch_channel("1266555623722451027")

                await log_c.send(f"anonymousコマンド使用\nuser:{interaction.user.display_name}", embed=embed)
            else:
                await interaction.respond("テキスト or 画像を送信してください。", ephemeral=True)
        else:
            await interaction.response.send_message("あなたはブラックリストに登録されています。", ephemeral=True)



class say(commands.Cog):

    def __init__(self, bot):
        self.bot = bot

    @discord.slash_command(name='say', description="BOTが発言します。")
    @commands.is_owner()
    async def anonymous(self, interaction: discord.ApplicationContext, text: discord.Option(str, description="メッセージを入力してください。")):

        await interaction.response.send_message("送信しました。", ephemeral=True)
        await interaction.send(text)





def setup(bot):
    bot.add_cog(anonymous(bot))
    bot.add_cog(say(bot))