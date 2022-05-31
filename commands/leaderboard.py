import discord
from discord.ext import commands
from db_functions import add_coins, get_level, add_xp, get_kriddytoo_shrine_boost, add_kriddytoo_shrine_boost, get_shop_item_index
import sqlite3
from main import bot

@commands.command(name = "leaderboard", aliases = ["lb", "lead", "top"], description = "View coin leaderboards")
@commands.bot_has_permissions(send_messages=True)
@commands.guild_only()
@commands.cooldown(1, 15, commands.BucketType.user)
async def leaderboard(ctx):
    
    db = sqlite3.connect('database.sqlite')
    cursor = db.cursor()
    cursor.execute(f"SELECT * FROM users")
    result = cursor.fetchall()
    
    #sort top to bottom
    for i in range(0, len(result)):    
        for j in range(i+1, len(result)):    
            if(result[i][1] < result[j][1]):    
                temp = result[i];    
                result[i] = result[j];    
                result[j] = temp;  

    leaderboard = []

    for i in range(10):
        leaderboard.append(f"{bot.get_user(result[i][0])}: {result[i][1]} coins")

    text = '\n'.join(map(str, leaderboard))

    await ctx.send(f"**Coin Leaderboard:** ```{text}```")

    db.commit()
    cursor.close()
    db.close()


def setup(bot):
    bot.add_command(leaderboard)
