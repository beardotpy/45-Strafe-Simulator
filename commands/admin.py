import discord, sqlite3, random
import math
from main import bot
from discord.ext import commands
from db_functions import add_coins, add_xp, get_level, get_kriddytoo_shrine_boost, add_kriddytoo_shrine_boost
from datetime import datetime

@commands.command(name = "admin", description = "testing")
@commands.bot_has_permissions(send_messages=True)
@commands.guild_only()
@commands.is_owner()
@commands.cooldown(1, 1, commands.BucketType.user)
async def admin(ctx, subcommand=None, args1=None, args2=None, args3=None):

    if subcommand is None:
        return await ctx.send("```Please input arguments.```")

    if subcommand == "test":
        print()



    if subcommand == "dailyreset":
        db = sqlite3.connect('database.sqlite')
        cursor = db.cursor()
        cursor.execute(f"SELECT * FROM users")
        result = cursor.fetchall()
        for row in result:
            print(f"{row[0]} {row[6]}")
            if row[6] == 0:
                cursor.execute(f"UPDATE users SET daily_streak = 0 WHERE id = {row[0]}")
            cursor.execute(f"UPDATE users SET has_claimed_daily = 0 WHERE id = {row[0]}")
        print("Dailies have been reset!")
        await ctx.send("```Dailies have been reset!```")
        db.commit()
        cursor.close()
        db.close()

    if subcommand == "reloadcommand":
        try:
            bot.reload_extension(f'commands.{args1}')
            await ctx.send(f"```Reloaded extension {args1}```")
            print(f"Extension command.{args1} was reloaded")
        except:
            await ctx.send("```That command does not exist```")

    if subcommand == "addcoins":
        try:
            await add_coins(int(args1), int(args2))
            await ctx.send(f"```Given {args2} coins to id {args1}```")
        except:
            await ctx.send(f"```Something went wrong trying to do this.```")

    if subcommand == "shutdown":
        await ctx.send("```Shutting down```")
        await bot.close()
            


def setup(bot):
    bot.add_command(admin)
