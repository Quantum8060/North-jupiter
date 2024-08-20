import discord
from discord.ext import commands

Debug_guild = [1235247721934360577]


class report(commands.Cog):

    def __init__(self, bot):
        self.bot = bot

    @discord.slash_command(name="report", description="通報を行います。")
    async def report(self, ctx: discord.ApplicationContext, text: discord.Option(str, description="通報内容を入力"), image: discord.Attachment = None):
        if text and image:
            embed = discord.Embed(title="通報サービス", description="以下の通報を受け取りました。")
            embed.add_field(name="通報者", value=ctx.user.display_name, inline=False)
            embed.add_field(name="通報内容", value=f"{text}", inline=False)
            embed.set_image(url=image.url)

            report_c = await self.bot.fetch_channel("1266640534404075570")
            await report_c.send(embed=embed)
            await ctx.respond(f"以下の内容で通報を行いました。\n```{text}```\n※通報に際して管理者から連絡が来る可能性があります。", ephemeral=True)
        elif text:
            embed = discord.Embed(title="通報サービス", description="以下の通報を受け取りました。")
            embed.add_field(name="通報者", value=ctx.user.display_name, inline=False)
            embed.add_field(name="通報内容", value=f"{text}", inline=False)

            report_c = await self.bot.fetch_channel("1266640534404075570")
            await report_c.send(embed=embed)
            await ctx.respond(f"以下の内容で通報を行いました。\n```{text}```\n※通報に際して管理者から連絡が来る可能性があります。", ephemeral=True)





def setup(bot):
    bot.add_cog(report(bot))