import discord
from discord.ext import commands
import os
from time import sleep
from discord.ext import tasks
import asyncio
import subprocess
import sys
from discord.ext.commands import NotOwner

Debug_guild = [1235247721934360577]

class restart(commands.Cog):

    def __init__(self, bot):
        self.bot = bot

    @discord.slash_command(name="restart", description="BOTを再起動します。")
    @commands.is_owner()
    async def restart(self, ctx):
        await ctx.respond("BOTを停止します。", ephemeral=True)
        print("BOTを停止しました。\n------")
        await asyncio.sleep(20)
        command = ["python3","restart.py"]
        proc = subprocess.Popen(command)
        proc.communicate()
        await self.bot.close()
        loop = asyncio.get_event_loop()
        loop.stop
        kill_pid = os.getpid()
        kill = ["kill","-KILL", f"{kill_pid}"]
        subprocess.Popen(kill).communicate()

    @restart.error
    async def restarterror(ctx, error):
        if isinstance(error, NotOwner):
            await ctx.respond("あなたはこのコマンドを使用する権限を持っていません!", ephemeral=True)
        else:
            await ctx.respond("Something went wrong...", ephemeral=True)
            raise error

class stop(commands.Cog):

    def __init__(self, bot):
        self.bot = bot

    @discord.slash_command(name="stop", description="BOTを停止します。")
    @commands.is_owner()
    async def stop(self, ctx):
        await ctx.respond("BOTを停止します。", ephemeral=True)
        print("BOTを停止しました。\n------")
        await self.bot.close()
        await asyncio.sleep(1)
        loop = asyncio.get_event_loop()
        loop.stop

    @stop.error
    async def stoperror(ctx, error):
        if isinstance(error, NotOwner):
            await ctx.respond("あなたはこのコマンドを使用する権限を持っていません!", ephemeral=True)
        else:
            await ctx.respond("Something went wrong...", ephemeral=True)
            raise error


def setup(bot):
    bot.add_cog(restart(bot))
    bot.add_cog(stop(bot))