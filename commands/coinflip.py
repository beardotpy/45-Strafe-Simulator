import discord
from discord.ext import commands
import sqlite3
import random
from db_functions import add_coins, get_level, add_xp, get_coins, get_kriddytoo_shrine_boost, add_kriddytoo_shrine_boost, get_shop_item, add_item

@commands.command(name = "coinflip", aliases = ["flip"], description = "Gamble with the man in the black coat, bet money on a coin flip")
@commands.bot_has_permissions(send_messages=True)
@commands.guild_only()
@commands.cooldown(1, 10, commands.BucketType.user)
async def coinflip(ctx, amount="0"):

    try:
        amount = int(amount)
    except:
        amount = 0.0

    db = sqlite3.connect('database.sqlite')
    cursor = db.cursor()

    #check if owns hut
    cursor.execute(f"SELECT name FROM items WHERE id = {ctx.author.id} AND name = 'fakeid'")
    hut = cursor.fetchone()
    if hut is None:
        db.commit()
        cursor.close()
        db.close()
        return await ctx.send(f":man_detective:: **{ctx.author}**, you must own a **fakeid** to gamble with me.")
        
    db.commit()
    cursor.close()
    db.close()

    if await get_coins(ctx.author.id) <  amount:
        return await ctx.send(f":man_detective:: **{ctx.author}**, you don't have enough coins")
    
    if amount < 1:
        return await ctx.send(f":man_detective:: **{ctx.author}**, you need to bet coins to coinflip")

    max_bet = await get_level(ctx.author.id) * 40

    if amount > max_bet:
        return await ctx.send(f":man_detective:: **{ctx.author}**, you cannot bet more than **{max_bet}** :coin:")
        

    if random.randint(0, 1) == 1:
        await ctx.send(f":man_detective:: **{ctx.author}** congratulations, the coin was heads and you won **{amount}** :coin:")
        await add_coins(ctx.author.id, amount)
        await add_xp(ctx.author.id, 10, ctx)
    else:
        await ctx.send(f":man_detective:: **{ctx.author}** better luck next time, the coin was tails and you lost **{amount}** :coin:")
        await add_coins(ctx.author.id, -amount)
        await add_xp(ctx.author.id, 10, ctx)

    


def setup(bot):
    bot.add_command(coinflip)
