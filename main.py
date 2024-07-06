import discord
import discord.ui
from discord import option
import os
from discord.ext import commands
from discord.ext.commands import MissingPermissions
from time import sleep
import aiohttp
import json
import configparser
from discord.ext import tasks
import asyncio
import random
import string
from dotenv import load_dotenv
import sqlite3
from datetime import datetime
import pytz
import aiofiles


intents = discord.Intents.default()
intents.message_content = (True)

config_ini = configparser.ConfigParser()
config_ini.read("config.ini", encoding="utf-8")
TOKEN = config_ini["MAIN"]["TOKEN"]

bot = discord.Bot(intents=intents)
bot.webhooks = {}
Debug_guild = [1235247721934360577]
main_guild = [962647934695002173, 1235247721934360577]

global result
result = ''.join(random.choices(string.ascii_letters + string.digits, k=16))

#起動通知
@bot.event
async def on_ready():
    os.environ['PASS'] = result
    print(f"Bot名:{bot.user} On ready!!")
    print(os.environ['PASS'])
    print("------")
    channel = await bot.fetch_channel("1235247794114134037")
    pass_channel = await bot.fetch_channel("1251824100515512432")
    await channel.send(f"{bot.user}BOT起動完了")
    await pass_channel.send(f"{result}")
    bot.add_view(panelView())



transaction_file = 'transaction.json'

async def load_transaction_data():
    try:
        async with aiofiles.open(transaction_file, 'r') as t_file:
            return json.loads(await t_file.read())
    except FileNotFoundError:
        return {}

async def save_transaction_data(data):
    async with aiofiles.open(transaction_file, 'w') as t_file:
        await t_file.write(json.dumps(data, indent=4))



#stop
def stop_py():
    if (bot.is_closed()):
        print("osを切ります。")
        os.system("kill 1")



conn = sqlite3.connect('users.db')
c = conn.cursor()

# テーブルが存在しない場合は作成
c.execute('''CREATE TABLE IF NOT EXISTS users
             (id TEXT PRIMARY KEY, cash TEXT)''')
conn.commit()

def save_user(user_id, cash):
    with conn:
        c.execute("INSERT OR IGNORE INTO users (id, cash) VALUES (?, ?)", (user_id, cash))
        c.execute("UPDATE users SET cash = ? WHERE id = ?", (cash, user_id))

# ユーザー情報を取得する関数
def get_user_info(user_id):
    c.execute("SELECT id, cash FROM users WHERE id = ?", (user_id,))
    return c.fetchone()



admin = discord.SlashCommandGroup("admin", "Math related commands")

@admin.command(name="open", description="口座の開設")
@commands.has_permissions(administrator=True)
async def open(ctx: discord.ApplicationContext, user: discord.Member, amount: discord.Option(int, required=True, description="保存する内容を入力。")):

    user_id = str(user.id)
    cash = int(amount)
    save_user(user_id, cash)

    user_info = get_user_info(user.id)

    embed = discord.Embed(title="口座開設完了", description="ノスタルジカをご利用いただきありがとうございます。\n口座の開設が完了しました。", color=0x38c571)
    embed.add_field(name="開設者", value=f"{user.mention}", inline=False)
    embed.add_field(name="開設担当者", value=f"{ctx.user.mention}", inline=False)
    embed.add_field(name="残高", value=f"{user_info[1]}ノスタル", inline=False)

    await ctx.respond(embed=embed)



@admin.command(name="bal", description="ユーザーの所持金の表示")
@commands.has_permissions(administrator=True)
async def bal(ctx: discord.ApplicationContext, user: discord.Member):
    user_info = get_user_info(user.id)
    if user_info:
        embed = discord.Embed(title="残高確認", description=f"{user.mention}の残高を表示しています。", color=0x38c571)
        embed.add_field(name="残高", value=f"{user_info[1]}ノスタル")

        await ctx.respond(embed=embed, ephemeral=True)
    else:
        await ctx.respond("口座がありません。", ephemeral=True)



@admin.command(name="give", description="金を付与します。")
@commands.has_permissions(administrator=True)
async def give(ctx: discord.ApplicationContext, user: discord.Member, amount: discord.Option(int, required=True, description="金額を入力。")):

    user_info = get_user_info(user.id)

    user_id = str(user.id)
    cash = int(user_info[1]) + amount
    save_user(user_id, cash)

    embed = discord.Embed(title="付与", description=f"以下の金額を{user.mention}に付与しました。", color=0x38c571)
    embed.add_field(name="金額", value=f"{amount}ノスタル", inline=False)

    await ctx.response.send_message(embed=embed)



@admin.command(name="help", description="管理者用helpを表示します。")
@commands.has_permissions(administrator=True)
async def help(ctx: discord.ApplicationContext):
    embed = discord.Embed(title="help", description="管理者用のコマンドを一覧表示しています。\n管理者用コマンドはコマンドに「admin」とついています。")
    embed.add_field(name="bal", value="```指定したユーザーの所持金を確認します。```", inline=False)
    embed.add_field(name="give", value="```指定したユーザーに振り込みます。```", inline=False)
    embed.add_field(name="help", value="```このhelpを表示します。```", inline=False)
    embed.add_field(name="open", value="```指定したユーザーの口座を開設します。```", inline=False)
    embed.add_field(name="panel", value="```口座開設用パネルを設置します。```", inline=False)

    await ctx.response.send_message(embed=embed, ephemeral=True)



class panelView(discord.ui.View):

    def __init__(self):
        super().__init__(timeout=None)

    @discord.ui.button(label="口座開設", custom_id="panel-button", style=discord.ButtonStyle.green)
    async def panel(self, button: discord.ui.Button, interaction: discord.Interaction):
        user_id = str(interaction.user.id)

        user_info = get_user_info(user_id)
        if user_info:
            embed = discord.Embed(title="口座確認", description="あなたの口座は存在します。", color=0x38c571)
            await interaction.response.send_message(embed=embed, ephemeral=True)
        else:
            user_id = str(interaction.user.id)
            cash = int(10000)
            save_user(user_id, cash)

            user_info = get_user_info(interaction.user.id)

            embed = discord.Embed(title="口座開設完了", description="ノスタルジカをご利用いただきありがとうございます。\n口座の開設が完了しました。", color=0x38c571)
            embed.add_field(name="開設者", value=f"{interaction.user.mention}ノスタル", inline=False)
            embed.add_field(name="残高", value=f"{user_info[1]}", inline=False)

            await interaction.response.send_message(embed=embed)

@admin.command(name="panel", description="口座開設用パネルを設置します。")
@commands.has_permissions(administrator=True)
async def panel(ctx: discord.ApplicationContext):

    embed = discord.Embed(title="口座開設パネル", description="口座開設を行う方は以下のボタンを押してください。\n \n注意！\n現時点では口座開設済みの方が押すと口座情報がリセットされます。")

    await ctx.response.send_message(embed=embed, view=panelView())



@admin.command(name="tra", description="取引履歴を表示します。", guild_ids=main_guild)
@commands.has_permissions(administrator=True)
async def transaction(ctx, user: discord.Member):
    data = await load_transaction_data()
    user_data = data.get(str(user.id), None)
    if user_data:
        embed = discord.Embed(title=f"{user.display_name}の取引履歴を表示しています。", color=0x38c571)
        for entry in user_data:
            embed.add_field(name=entry['timestamp'], value=f"金額: {entry['amount']}", inline=False)
        await ctx.respond(embed=embed, ephemeral=True)
    else:
        embed = discord.Embed(title="データなし", description=f"{ctx.user.mention}の取引履歴は存在しません。", color=0xff0000)
        await ctx.respond(embed=embed, ephemeral=True)

bot.add_application_command(admin)



@bot.slash_command(name="bal", description="自分の所持金の表示")
async def bal(ctx: discord.ApplicationContext):
    user_info = get_user_info(ctx.user.id)

    b_id = str(ctx.user.id)

    if user_info:
        embed = discord.Embed(title="残高確認", description=f"{ctx.user.mention}の残高を表示しています。", color=0x4169e1)
        embed.add_field(name="残高", value=f"{user_info[1]}ノスタル")

        await ctx.respond(embed=embed, ephemeral=True)
    else:
        embed = discord.Embed(title="データなし", description="口座がありません。", color=0xff0000)
        await ctx.respond(embed=embed, ephemeral=True)



@bot.user_command(name="balance")
async def u_bal(ctx, user: discord.Member):
    user_info = get_user_info(ctx.author.id)


    if user_info:
        embed = discord.Embed(title="残高確認", description=f"{ctx.author.mention}の残高を表示しています。", color=0x4169e1)
        embed.add_field(name="残高", value=f"{user_info[1]}ノスタル")

        await ctx.respond(embed=embed, ephemeral=True)
    else:
        embed = discord.Embed(title="口座確認", description="口座がありません。", color=0xff0000)
        await ctx.respond(embed=embed, ephemeral=True)



@bot.slash_command(name="pay", description="送金します。")
async def pay(ctx: discord.ApplicationContext, amount: discord.Option(int, description="送金する金額を記入"), send: discord.Member, reason: discord.Option(discord.SlashCommandOptionType.string, description="取引内容を入力") =None):

    user_info = get_user_info(ctx.user.id)

    if amount <= int(user_info[1]):
        if amount and send and reason:
            user_info = get_user_info(ctx.author.id)
            Balance = int(user_info[1]) - amount

            remittance = get_user_info(send.id)
            partner = int(remittance[1]) + amount

            user_id = str(ctx.author.id)
            cash = int(Balance)
            save_user(user_id, cash)

            user_id = str(send.id)
            cash = int(partner)
            save_user(user_id, cash)

            user_data = {
                'id': ctx.user.id,
                'amount': amount,
                'reason': reason,
                'timestamp': datetime.now(pytz.timezone('Asia/Tokyo')).strftime("%Y-%m-%d %H:%M:%S")
            }

            data = await load_transaction_data()
            if str(ctx.user.id) not in data:
                data[str(ctx.user.id)] = []
            data[str(ctx.user.id)].append(user_data)
            await save_transaction_data(data)

            embed = discord.Embed(title="送金", description="以下の内容で送金を行いました。", color=0x38c571)
            embed.add_field(name="送金先", value=f"{send.mention}", inline=False)
            embed.add_field(name="金額", value=f"{amount}ノスタル", inline=False)
            embed.add_field(name="取引内容", value=f"{reason}", inline=False)

            await ctx.response.send_message(embed=embed)
        elif amount and send:
            user_info = get_user_info(ctx.author.id)
            Balance = int(user_info[1]) - amount

            remittance = get_user_info(send.id)
            partner = int(remittance[1]) + amount

            user_id = str(ctx.author.id)
            cash = int(Balance)
            save_user(user_id, cash)

            user_id = str(send.id)
            cash = int(partner)
            save_user(user_id, cash)

            embed = discord.Embed(title="送金", description="以下の内容で送金を行いました。", color=0x38c571)
            embed.add_field(name="送金先", value=f"{send.mention}", inline=False)
            embed.add_field(name="金額", value=f"{amount}", inline=False)

            user_data = {
                'id': ctx.user.id,
                'amount': amount,
                'timestamp': datetime.now(pytz.timezone('Asia/Tokyo')).strftime("%Y-%m-%d %H:%M:%S")
            }

            data = await load_transaction_data()
            if str(ctx.user.id) not in data:
                data[str(ctx.user.id)] = []
            data[str(ctx.user.id)].append(user_data)
            await save_transaction_data(data)

            await ctx.response.send_message(embed=embed)
    else:
        await ctx.response.send_message("残高が足りません。", ephemeral=True)



@bot.slash_command(name="search", description="口座が存在するか確認します。")
async def search(ctx: discord.ApplicationContext, user: discord.Member):

    user_info = get_user_info(user.id)
    if user_info:

        embed = discord.Embed(title="口座確認", description=f"{user.mention}の口座は存在します。", color=0x38c571)

        await ctx.response.send_message(embed=embed, ephemeral=True)
    else:
        embed = discord.Embed(title="口座確認", description=f"{user.mention}の口座は存在しません。", color=0xff0000)
        await ctx.response.send_message(embed=embed, ephemeral=True)



@bot.slash_command(name="help", description="helpを表示します。")
async def help(ctx: discord.ApplicationContext):
    embed = discord.Embed(title="help", description="一般のユーザー用のコマンドを一覧表示しています。\nすべてのコマンドはスラッシュコマンドです。/を入力して出てくるコマンドを実行してください。")
    embed.add_field(name="bal", value="```所持金を確認します。```", inline=False)
    embed.add_field(name="help", value="```helpを表示します。```", inline=False)
    embed.add_field(name="pay", value="```この指定したユーザーに支払いを行います。```", inline=False)
    embed.add_field(name="search", value="```指定したユーザーの口座が存在するか確認します。```", inline=False)
    embed.add_field(name="tra", value="```送金履歴を確認します。\n※今後のアップデートで入金履歴も確認できるようになります！```", inline=False)

    await ctx.response.send_message(embed=embed, ephemeral=True)



@bot.slash_command(name="tra", description="取引履歴を表示します。", guild_ids=main_guild)
async def transaction(ctx: discord.ApplicationContext):
    data = await load_transaction_data()
    user_data = data.get(str(ctx.user.id), None)
    if user_data:
        embed = discord.Embed(title=f"{ctx.user.display_name}の取引履歴を表示しています。", color=0x38c571)
        for entry in user_data:
            embed.add_field(name=entry['timestamp'], value=f"金額: {entry['amount']}", inline=False)
        await ctx.respond(embed=embed, ephemeral=True)
    else:
        embed = discord.Embed(title="データなし", description=f"{ctx.user.mention}の取引履歴は存在しません。", color=0xff0000)
        await ctx.respond(embed=embed, ephemeral=True)



@bot.slash_command(name="info", description="ノスタルへの交換レートを表示します。", guild_ids=Debug_guild)
async def info(ctx: discord.ApplicationContext):

    embed = discord.Embed(title="交換レート", description="以下のアイテムをノスタルに交換できます。\n交換を希望する方は <@!1009494490526007336> に連絡してください。", color=0x38c571)
    embed.add_field(name="鉄", value="1N", inline=True)
    embed.add_field(name="黒曜石", value="5N", inline=True)
    embed.add_field(name="ネザライト", value="4500N", inline=True)
    embed.add_field(name="100ヨーク通貨", value="1N", inline=True)
    embed.add_field(name="100ペンギン帝国通貨", value="1N", inline=True)

    await ctx.response.send_message(embed=embed, ephemeral=True)


#cogs登録
cogs_list = [
    'clear',
    'ping',
    'invite',
    'mcstatus',
    'dm',
    'tasks',
    'random',
    'blacklist',
    'stop',
    'embed'
]

for cog in cogs_list:
    bot.load_extension(f'cogs.{cog}')


bot.run(TOKEN)