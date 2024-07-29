import discord
import discord.ui
from discord import option
import os
from discord.ext import commands
from discord.ext.commands import MissingAnyRole
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
from datetime import datetime, date
from datetime import timedelta
import pytz
import aiofiles
import toml






intents = discord.Intents.default()
intents.message_content = (True)

config_ini = configparser.ConfigParser()
config_ini.read("config.ini", encoding="utf-8")
TOKEN = config_ini["MAIN"]["TOKEN"]

bot = discord.Bot(intents=intents)
bot.webhooks = {}
Debug_guild = [1235247721934360577, 1256021750756544632]
main_guild = [962647934695002173, 1235247721934360577, 1256021750756544632]

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

#stop
def stop_py():
    if (bot.is_closed()):
        print("osを切ります。")
        os.system("kill 1")






TOML_FILE = 'company.toml'

async def load_company_data():
    if not os.path.exists(TOML_FILE):
        return {}
    async with aiofiles.open(TOML_FILE, 'r') as file:
        contents = await file.read()
        return toml.loads(contents).get('companies', {})

async def save_company_data(data):
    async with aiofiles.open(TOML_FILE, 'w') as file:
        await file.write(toml.dumps({'companies': data}))






transaction_file = 'transaction.json'

async def load_transaction_data():
    try:
        async with aiofiles.open(transaction_file, 'r') as t_file:
            return json.loads(await t_file.read())
    except FileNotFoundError:
        return {}

async def save_transaction_data(t_data):
    async with aiofiles.open(transaction_file, 'w') as t_file:
        await t_file.write(json.dumps(t_data, indent=4))






conn = sqlite3.connect('users.db')
c = conn.cursor()



c.execute('''CREATE TABLE IF NOT EXISTS users
             (id TEXT PRIMARY KEY, cash INTEGER )''')
c.execute('''CREATE TABLE IF NOT EXISTS company
             (id TEXT PRIMARY KEY, cash INTEGER)''')
conn.commit()



#SQlite3
def save_user(user_id, cash):
    with conn:
        c.execute("INSERT OR IGNORE INTO users (id, cash) VALUES (?, ?)", (user_id, cash))
        c.execute("UPDATE users SET cash = ? WHERE id = ?", (cash, user_id))

def get_user_info(user_id):
    c.execute("SELECT id, cash FROM users WHERE id = ?", (user_id,))
    return c.fetchone()



def save_company(company_id, cash):
    with conn:
        c.execute("INSERT OR IGNORE INTO company (id, cash) VALUES (?, ?)", (company_id, cash))
        c.execute("UPDATE company SET cash = ? WHERE id = ?", (cash, company_id))

def get_company_info(company_id):
    c.execute("SELECT id, cash FROM company WHERE id = ?", (company_id,))
    return c.fetchone()



#TOML
async def save_company_access(company_id, ceo, employees):
    companies = await load_company_data()
    companies[company_id] = {'ceo': ceo, 'employees': employees}
    await save_company_data(companies)

async def get_company_access(company_id):
    companies = await load_company_data()
    return companies.get(company_id)

async def add_employee(company_id, employee_id):
    companies = await load_company_data()
    if company_id in companies:
        if 'employees' not in companies[company_id]:
            companies[company_id]['employees'] = []
        companies[company_id]['employees'].append(employee_id)
        await save_company_data(companies)
        return True
    return False

async def is_authorized_user(user_id, company_id):
    company_access = await get_company_access(company_id)
    if company_access:
        return user_id == company_access['ceo'] or user_id in company_access['employees']
    return False





admin = discord.SlashCommandGroup("admin", "admin related commands")

@admin.command(name="open", description="口座の開設", guild_ids=main_guild)
@commands.has_any_role(962650031658250300, 1237718104918982666, 1262092644994125824)
async def open(ctx: discord.ApplicationContext, user: discord.Member, amount: discord.Option(int, required=True, description="保存する内容を入力。")):


    if int(amount) >= 0:
        user_id = str(user.id)
        cash = int(amount)
        save_user(user_id, cash)

        user_info = get_user_info(user.id)

        embed = discord.Embed(title="口座開設完了", description="ノスタルジカをご利用いただきありがとうございます。\n口座の開設が完了しました。", color=0x38c571)
        embed.add_field(name="開設者", value=f"{user.mention}", inline=False)
        embed.add_field(name="開設担当者", value=f"{ctx.user.mention}", inline=False)
        embed.add_field(name="残高", value=f"{user_info[1]}ノスタル", inline=False)

        await ctx.respond(embed=embed)
        log_c = await bot.fetch_channel("1262092921964986509")
        await log_c.send(f"openコマンド使用\nuser:{ctx.user.name}\ntarget:{user.name}")
    else:
        await ctx.respond("0以下にはできません。", ephemeral=True)



@admin.command(name="bal", description="ユーザーの所持金の表示", guild_ids=main_guild)
@commands.has_any_role(962650031658250300, 1237718104918982666, 1262092644994125824)
async def bal(ctx: discord.ApplicationContext, user: discord.Member):
    user_info = get_user_info(user.id)
    if user_info:
        embed = discord.Embed(title="残高確認", description=f"{user.mention}の残高を表示しています。", color=0x38c571)
        embed.add_field(name="残高", value=f"{user_info[1]}ノスタル")

        await ctx.respond(embed=embed, ephemeral=True)
        log_c = await bot.fetch_channel("1262092999161286656")
        await log_c.send(f"balコマンド使用\nuser:{ctx.user.name}\ntarget:{user.name}")
    else:
        await ctx.respond("口座がありません。", ephemeral=True)



@admin.command(name="c_bal", description="企業の所持金の表示", guild_ids=main_guild)
@commands.has_any_role(962650031658250300, 1237718104918982666, 1262092644994125824)
async def bal(ctx: discord.ApplicationContext, company: discord.Option(str, description="企業名を入力してください。")):
    company_info = get_company_info(company)
    if company_info:
        embed = discord.Embed(title="残高確認", description=f"{company}の残高を表示しています。", color=0x38c571)
        embed.add_field(name="残高", value=f"{company_info[1]}ノスタル")

        await ctx.respond(embed=embed, ephemeral=True)
        log_c = await bot.fetch_channel("1262100440506564608")
        await log_c.send(f"c_balコマンド使用\nuser:{ctx.user.name}\ncompany:{company}")
    else:
        await ctx.respond("口座がありません。", ephemeral=True)



@admin.command(name="give", description="金を付与します。", guild_ids=main_guild)
@commands.has_any_role(962650031658250300, 1237718104918982666, 1262092644994125824)
async def give(ctx: discord.ApplicationContext, user: discord.Member, amount: discord.Option(int, required=True, description="金額を入力。")):

    user_info = get_user_info(user.id)

    if int(user_info[1]) + amount >= 0:
        user_id = str(user.id)
        cash = int(user_info[1]) + amount
        save_user(user_id, cash)

        embed = discord.Embed(title="付与", description=f"以下の金額を{user.mention}に付与しました。", color=0x38c571)
        embed.add_field(name="金額", value=f"{amount}ノスタル", inline=False)

        await ctx.response.send_message(embed=embed)
        log_c = await bot.fetch_channel("1262093090316091543")
        await log_c.send(f"giveコマンド使用\nuser:{ctx.user.name}\ntarget:{user.name}\namount:{amount}")
    else:
        await ctx.respond("所持金を0以下にすることはできません。", ephemeral=True)



class panelView(discord.ui.View):

    def __init__(self):
        super().__init__(timeout=None)

    @discord.ui.button(label="口座開設", custom_id="panel-button", style=discord.ButtonStyle.green)
    async def panel(self, button: discord.ui.Button, interaction: discord.Interaction):
        user_id = str(interaction.user.id)

        user_info = get_user_info(user_id)
        if user_info:
            embed = discord.Embed(title="エラー", description="あなたの口座はすでに存在しています。", color=0x38c571)
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

@admin.command(name="panel", description="口座開設用パネルを設置します。", guild_ids=main_guild)
@commands.has_any_role(962650031658250300, 1237718104918982666, 1262092644994125824)
async def panel(ctx: discord.ApplicationContext):

    embed = discord.Embed(title="口座開設パネル", description="口座開設を行う方は以下のボタンを押してください。\n \n注意！\n現時点では口座開設済みの方が押すと口座情報がリセットされます。")

    await ctx.response.send_message(embed=embed, view=panelView())
    log_c = await bot.fetch_channel("1262093173518499842")
    await log_c.send(f"panelコマンド使用\nuser:{ctx.user.name}")



@admin.command(name="tra", description="取引履歴を表示します。", guild_ids=main_guild)
@commands.has_any_role(962650031658250300, 1237718104918982666, 1262092644994125824)
async def transaction(ctx, user: discord.Member):
    data = await load_transaction_data()
    user_data = data.get(str(user.id), None)
    if user_data:
        embed = discord.Embed(title=f"{user.display_name}の取引履歴を表示しています。", color=0x38c571)
        for entry in user_data:
            embed.add_field(name=entry['timestamp'], value=f"金額: {entry['amount']}", inline=False)
        await ctx.respond(embed=embed, ephemeral=True)
        log_c = await bot.fetch_channel("1262093150638571614")
        await log_c.send(f"traコマンド使用\nuser:{ctx.user.name}\ntarget:{user.name}")
    else:
        embed = discord.Embed(title="データなし", description=f"{ctx.user.mention}の取引履歴は存在しません。", color=0xff0000)
        await ctx.respond(embed=embed, ephemeral=True)



@admin.command(name="delete", description="口座を削除します。")
@commands.is_owner()
async def delete(ctx: discord.ApplicationContext, reason:discord.Option(str, description="理由を入力してください。"), user: discord.Member = None, company: discord.Option(discord.SlashCommandOptionType.string, description="企業名を入力してください。") = None):

    if reason and user:
        user_id = str(user.id)

        user_info = get_user_info(user_id)

        if user_info:
            c.execute(f"""DELETE FROM users WHERE id="{user.id}";""")
            conn.commit()

            await ctx.response.send_message(f"{user.mention}のデータを削除しました。", ephemeral=True)
        else:
            await ctx.response.send_message(f"{user.mention}の口座は存在しません。", ephemeral=True)
    elif reason and company:
        company_id = str(company)

        company_info = get_company_info(company_id)

        if company_info:
            c.execute(f"""DELETE FROM company WHERE id="{company}";""")
            conn.commit()

            await ctx.response.send_message(f"{company}のデータを削除しました。", ephemeral=True)
        else:
            await ctx.response.send_message(f"{company}のデータは存在しません。", ephemeral=True)



@admin.command(name="log", description="nohup.outファイルを送信します。")
@commands.is_owner()
async def log(ctx: discord.ApplicationContext):
    await ctx.response.send_message(file=discord.File("nohup.out"), ephemeral=True)



@admin.command(name="get_db", description="DBを取得します。")
@commands.is_owner()
async def get_db(ctx: discord.ApplicationContext):
    await ctx.response.send_message(file=discord.File("users.db"), ephemeral=True)



bot.add_application_command(admin)






company = discord.SlashCommandGroup("company", "company related commands")



@company.command(name="open", description="企業を追加します。", guild_ids=main_guild)
async def c_open(ctx: discord.ApplicationContext, name: discord.Option(str, description="企業名を入力。")):

    company_info = get_company_info(name)

    if company_info:
        embed = discord.Embed(title="エラー", description=f"{name}の口座はすでに存在しています。", color=0xff0000)
        await ctx.response.send_message(embed=embed, ephemeral=True)
    else:
        company_id = str(name)
        cash = int("0")
        save_company(company_id, cash)

        ceo = str(ctx.user.id)
        await save_company_access(company_id, ceo, [])

        company_info = get_company_info(name)

        embed = discord.Embed(title="企業口座開設完了", description="ノスタルジカをご利用いただきありがとうございます。\n以下の企業口座の開設が完了しました。", color=0x38c571)
        embed.add_field(name="企業名", value=f"{name}", inline=False)
        embed.add_field(name="社長", value=f"{ctx.user.mention}", inline=False)

        await ctx.respond(embed=embed)
        log_c = await bot.fetch_channel("1262101253752881229")
        await log_c.send(f"openコマンド使用\nuser:{ctx.user.name}\nc_name:{name}")



@company.command(name="bal", description="企業の所持金の表示", guild_ids=main_guild)
async def c_bal(ctx: discord.ApplicationContext, company: discord.Option(str, description="企業名を入力してください。")):
    company_info = get_company_info(company)
    user_id = str(ctx.user.id)

    if not await is_authorized_user(user_id, company):
        await ctx.response.send_message("あなたはこの企業の口座にアクセスできません。", ephemeral=True)
        return

    if company_info:
        embed = discord.Embed(title="残高確認", description=f"{company}の残高を表示しています。", color=0x38c571)
        embed.add_field(name="残高", value=f"{company_info[1]}ノスタル")

        await ctx.respond(embed=embed, ephemeral=True)
        log_c = await bot.fetch_channel("1262101272014622790")
        await log_c.send(f"balコマンド使用\nuser:{ctx.user.name}\ncompany:{company}")
    else:
        await ctx.respond("口座がありません。", ephemeral=True)



@company.command(name="pay", description="企業から送金します。", guild_ids=main_guild)
async def c_pay(ctx: discord.ApplicationContext, amount: discord.Option(int, description="金額を入力してください。"), mycompany: discord.Option(str, description="企業名を入力"), user: discord.Member = None, company: discord.Option(str, description="企業名を入力") = None):
    company_info = get_company_info(mycompany)
    user_id = str(ctx.user.id)
    if not await is_authorized_user(user_id, mycompany):
        await ctx.response.send_message("あなたはこの企業の口座にアクセスできません。", ephemeral=True)
        return

    if amount > int(0):
        if amount <= int(company_info[1]):
            if amount and mycompany and user:
                company_info = get_company_info(mycompany)
                Balance = int(company_info[1]) - amount

                remittance = get_user_info(user.id)
                partner = int(remittance[1]) + amount

                company_id = str(mycompany)
                cash = int(Balance)
                save_company(company_id, cash)

                user_id = str(user.id)
                cash = int(partner)
                save_user(user_id, cash)

                embed = discord.Embed(title="送金", description="以下の内容で送金を行いました。", color=0x38c571)
                embed.add_field(name="送金先", value=f"{user.mention}", inline=False)
                embed.add_field(name="送金元", value=f"{mycompany}", inline=False)
                embed.add_field(name="金額", value=f"{amount}ノスタル", inline=False)

                await ctx.response.send_message(embed=embed)
                log_c = await bot.fetch_channel("1262101376591466557")
                await log_c.send(f"payコマンド使用\ncompany:{mycompany}\nsend:{user.name}")
            elif amount and mycompany and company:
                company_info = get_company_info(mycompany)
                Balance = int(company_info[1]) - amount

                remittance = get_company_info(company)
                partner = int(remittance[1]) + amount

                Mycompany_id = str(mycompany)
                cash = int(Balance)
                save_company(Mycompany_id, cash)

                company = str(company)
                cash = int(partner)
                save_company(company, cash)

                embed = discord.Embed(title="送金", description="以下の内容で送金を行いました。", color=0x38c571)
                embed.add_field(name="送金先", value=f"{company}", inline=False)
                embed.add_field(name="送金元", value=f"{mycompany}", inline=False)
                embed.add_field(name="金額", value=f"{amount}", inline=False)

                await ctx.response.send_message(embed=embed)
                log_c = await bot.fetch_channel("1262101376591466557")
                await log_c.send(f"payコマンド使用\ncompany:{mycompany}\nsend:{company}")
        else:
            await ctx.response.send_message("残高が足りません。", ephemeral=True)
    else:
        await ctx.response.send_message("0以下にはできません。", ephemeral=True)



@company.command(name="add", description="企業に社員を追加します。", guild_ids=main_guild)
async def add_employee_command(ctx: discord.ApplicationContext, company: discord.Option(str, description="企業名を入力してください。"), user: discord.Member):
    company_id = str(company)
    employee_id = str(user.id)

    ceo_id = str(ctx.user.id)
    company_access = await get_company_access(company_id)
    if company_access.get('ceo') != ceo_id:
        await ctx.respond("あなたはこの企業のCEOではありません。社員を追加できません。", ephemeral=True)
        return

    if await add_employee(company_id, employee_id):
        await ctx.respond(f"{user.mention} が {company} の社員として追加されました。", ephemeral=True)
        log_c = await bot.fetch_channel("1262101352499384320")
        await log_c.send(f"addコマンド使用\nuser:{ctx.user.name}\nadd:{user.name}")
    else:
        await ctx.respond(f"企業 {company} が見つかりませんでした。", ephemeral=True)



@company.command(name="delete", description="企業を削除します。", guild_ids=main_guild)
async def delete(ctx: discord.ApplicationContext, company: discord.Option(str, description="企業名を入力してください。")):
    company_access = await get_company_access(company)

    ceo_id = str(ctx.user.id)

    if company_access.get('ceo') != ceo_id:
        await ctx.respond("あなたはこの企業のCEOではありません。企業を解体できません。", ephemeral=True)
        return

    company_id = str(company)

    company_info = get_company_info(company_id)

    if int(company_info[1]) > int(0):
        await ctx.response.send_message("削除する口座に残高が残っています。!", ephemeral=True)
    else:
        if company_info:
            c.execute(f"""DELETE FROM company WHERE id="{company}";""")
            conn.commit()

            await ctx.response.send_message(f"{company}の口座を削除しました。", ephemeral=True)
            log_c = await bot.fetch_channel("1262101293376475188")
            await log_c.send(f"deleteコマンド使用\nuser:{ctx.user.name}\ncompany:{company}")
        else:
            await ctx.response.send_message(f"{company}の口座は存在しません。", ephemeral=True)



@company.command(name="search", description="企業の口座が存在するか確認します。", guild_ids=main_guild)
async def search(ctx: discord.ApplicationContext, company: discord.Option(str, description="企業名を入力してください。")):

    company_info = get_company_info(company)
    if company_info:

        embed = discord.Embed(title="口座確認", description=f"{company}の口座は存在します。", color=0x38c571)

        await ctx.response.send_message(embed=embed, ephemeral=True)
    else:
        embed = discord.Embed(title="口座確認", description=f"{company}の口座は存在しません。", color=0xff0000)
        await ctx.response.send_message(embed=embed, ephemeral=True)



bot.add_application_command(company)






@bot.slash_command(name="bal", description="自分の所持金の表示", guild_ids=main_guild)
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



@bot.slash_command(name="pay", description="送金します。", guild_ids=main_guild)
async def pay(ctx: discord.ApplicationContext, amount: discord.Option(int, description="送金する金額を記入"), user: discord.Member = None, company: discord.Option(discord.SlashCommandOptionType.string, description="企業を入力してください") =None , reason: discord.Option(discord.SlashCommandOptionType.string, description="取引内容を入力") =None):

    user_info = get_user_info(ctx.user.id)

    if amount > int(0):
        if amount <= int(user_info[1]):
            if amount and user and reason:
                user_info = get_user_info(ctx.author.id)
                Balance = int(user_info[1]) - amount

                remittance = get_user_info(user.id)
                partner = int(remittance[1]) + amount

                user_id = str(ctx.author.id)
                cash = int(Balance)
                save_user(user_id, cash)

                user_id = str(user.id)
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
                embed.add_field(name="送金先", value=f"{user.mention}", inline=False)
                embed.add_field(name="送金元", value=f"{ctx.user.mention}")
                embed.add_field(name="金額", value=f"{amount}ノスタル", inline=False)
                embed.add_field(name="取引内容", value=f"{reason}", inline=False)

                await ctx.response.send_message(embed=embed)
            elif amount and user:
                user_info = get_user_info(ctx.author.id)
                Balance = int(user_info[1]) - amount

                remittance = get_user_info(user.id)
                partner = int(remittance[1]) + amount

                user_id = str(ctx.author.id)
                cash = int(Balance)
                save_user(user_id, cash)

                user_id = str(user.id)
                cash = int(partner)
                save_user(user_id, cash)

                embed = discord.Embed(title="送金", description="以下の内容で送金を行いました。", color=0x38c571)
                embed.add_field(name="送金先", value=f"{user.mention}", inline=False)
                embed.add_field(name="送金元", value=f"{ctx.user.mention}")
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
            elif amount and company and reason:
                user_info = get_user_info(ctx.author.id)
                Balance = int(user_info[1]) - amount

                remittance = get_company_info(company)
                partner = int(remittance[1]) + amount

                user_id = str(ctx.author.id)
                cash = int(Balance)
                save_user(user_id, cash)

                company_id = str(company)
                cash = int(partner)
                save_company(company_id, cash)

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
                embed.add_field(name="送金先", value=f"{company}", inline=False)
                embed.add_field(name="送金元", value=f"{ctx.user.mention}")
                embed.add_field(name="金額", value=f"{amount}ノスタル", inline=False)
                embed.add_field(name="取引内容", value=f"{reason}", inline=False)

                await ctx.response.send_message(embed=embed)
            elif amount and company:
                user_info = get_user_info(ctx.author.id)
                Balance = int(user_info[1]) - amount

                remittance = get_company_info(company)
                partner = int(remittance[1]) + amount

                user_id = str(ctx.author.id)
                cash = int(Balance)
                save_user(user_id, cash)

                company_id = str(company)
                cash = int(partner)
                save_company(company_id, cash)

                embed = discord.Embed(title="送金", description="以下の内容で送金を行いました。", color=0x38c571)
                embed.add_field(name="送金先", value=f"{company}", inline=False)
                embed.add_field(name="送金元", value=f"{ctx.user.mention}")
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
            elif amount and user and company:
                await ctx.response.send_message("userかcompanyはどちらか一方を入力してください。", ephemeral=True)
            elif amount and user and company and reason:
                await ctx.response.send_message("userかcompanyはどちらか一方を入力してください。", ephemeral=True)
            else:
                await ctx.response.send_message("送金先を入力してください。", ephemeral=True)
        else:
            await ctx.response.send_message("残高が足りません。", ephemeral=True)
    else:
        await ctx.response.send_message("1以上の値を入力してください。", ephemeral=True)



@bot.slash_command(name="search", description="口座が存在するか確認します。", guild_ids=main_guild)
async def search(ctx: discord.ApplicationContext, user: discord.Member):

    user_info = get_user_info(user.id)
    if user_info:

        embed = discord.Embed(title="口座確認", description=f"{user.mention}の口座は存在します。", color=0x38c571)

        await ctx.response.send_message(embed=embed, ephemeral=True)
    else:
        embed = discord.Embed(title="口座確認", description=f"{user.mention}の口座は存在しません。", color=0xff0000)
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



@bot.slash_command(name="info", description="ノスタルへの交換レートを表示します。", guild_ids=main_guild)
async def info(ctx: discord.ApplicationContext):

    embed = discord.Embed(title="交換レート", description="以下のアイテムをノスタルに交換できます。\n交換を希望する方は <@!1009494490526007336> に連絡してください。", color=0x38c571)
    embed.add_field(name="鉄", value="1N", inline=True)
    embed.add_field(name="黒曜石", value="5N", inline=True)
    embed.add_field(name="ネザライト", value="4500N", inline=True)
    embed.add_field(name="1000Ruby", value="1N", inline=True)
    embed.add_field(name="10itum", value="1N", inline=True)
    embed.add_field(name="100ヨーク通貨", value="1N", inline=True)
    embed.add_field(name="100ペンギン帝国通貨", value="1N", inline=True)

    await ctx.response.send_message(embed=embed, ephemeral=True)



@bot.slash_command(name="leave", description="...")
@commands.is_owner()
async def leave(ctx: discord.ApplicationContext):
    await ctx.respond("サーバーから退出します。")
    await ctx.guild.leave()



@bot.slash_command(name="math", description="空色財閥用コマンド", guild_ids=main_guild)
async def math(ctx: discord.ApplicationContext, money: discord.Option(int, description="借りた金額を入力してください。"), year:discord.Option(int, description="借りた年を入力してください。"), month: discord.Option(int, description="借りた月を入力してください。"), day: discord.Option(int, description="借りた日付けを入力してください。")):
    dt1 = datetime.now()
    dt2 = date(year=year, month=month, day=day)

    td = dt1.date() - dt2

    dept = int(money * (1.01 ** td.days))

    await ctx.response.send_message(f"返済必要額は{dept}ノスタルです。", ephemeral=True)



@bot.message_command(name="メッセージを通報", guild_ids=Debug_guild)
async def userinfo_c(ctx, message: discord.Message):
    global message_c, message_u
    message_c = message.content
    message_u = message.author

    modal = reportModal(title="通報内容を入力")
    await ctx.send_modal(modal)
    await ctx.respond("フォームでの入力を待機しています…", ephemeral=True)

class reportModal(discord.ui.Modal):
    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)

        self.add_item(discord.ui.InputText(label="内容を入力してください。", style=discord.InputTextStyle.long))

    async def callback(self, interaction: discord.Interaction):

        embed = discord.Embed(title="通報サービス", description="以下の通報を受け取りました。")
        embed.add_field(name="メッセージ送信者", value=message_u, inline=False)
        embed.add_field(name="通報するメッセージ", value=message_c, inline=False)
        embed.add_field(name="通報者", value=interaction.user.display_name, inline=False)
        embed.add_field(name="理由", value=self.children[0].value, inline=False)

        report_c = await bot.fetch_channel("1266640534404075570")

        await report_c.send(embed=embed)
        await interaction.respond(f"以下のメッセージを通報しました。\n```{message_c}```\n※通報に際して管理者から連絡が来る可能性があります。", ephemeral=True)



#cogs登録
cogs_list = [
    'anonymous',
    'blacklist',
    'clear',
    'dm',
    'embed',
    'invite',
    'mcstatus',
    'ping',
    'random',
    'stop',
    'tasks',
    'report',
]

for cog in cogs_list:
    bot.load_extension(f'cogs.{cog}')






bot.run(TOKEN)