import discord
from discord.ext import commands
import sqlite3
from db_functions import add_coins, get_level, get_coins, get_kriddytoo_shrine_boost, add_kriddytoo_shrine_boost, get_shop_item, add_item

@commands.command(name = "sell", description = "Sell an item for coins")
@commands.bot_has_permissions(send_messages=True)
@commands.guild_only()
@commands.cooldown(1, 5, commands.BucketType.user)
async def sell(ctx, choice="null", amount="1"):

    db = sqlite3.connect('database.sqlite')
    cursor = db.cursor()

    #check if owns hut
    cursor.execute(f"SELECT name FROM items WHERE id = {ctx.author.id} AND name = 'hut'")
    hut = cursor.fetchone()
    if hut is None:
        db.commit()
        cursor.close()
        db.close()
        return await ctx.send(f"**{ctx.author}**, you must own a **hut** to sell items.")
        

    #did not specify sell item
    if choice == "null":
        db.commit()
        cursor.close()
        db.close()
        return await ctx.send(f"**{ctx.author}**, please specify an item to sell")

    #check if item exists
    cursor.execute(f"SELECT name FROM items WHERE id = {ctx.author.id} AND name = '{choice}'")
    result = cursor.fetchone()
    if result is None:
        db.commit()
        cursor.close()
        db.close()
        return await ctx.send(f"**{ctx.author}**, you do not own any of that item.")

    try:
        amount = int(amount)
        if amount < 1:
            db.commit()
            cursor.close()
            db.close()
            return await ctx.send(f"**{ctx.author}**, **\"{amount}\"** is not a valid amount.")
    except:
        db.commit()
        cursor.close()
        db.close()
        return await ctx.send(f"**{ctx.author}**, **\"{amount}\"** is not a valid amount.")

    #check if you have enough of that item
    cursor.execute(f"SELECT amount FROM items WHERE id = {ctx.author.id} AND name = '{choice}'")
    result = cursor.fetchone()
    if result[0] < amount:
        db.commit()
        cursor.close()
        db.close()
        return await ctx.send(f"**{ctx.author}**, you do not own enough of that item.")




    cursor.execute(f"SELECT * FROM items WHERE id = {ctx.author.id} AND name = '{choice}'")
    result = cursor.fetchone()

    item = {}
    item['name'] = result[1]
    item['amount'] = result[2]
    item['emoji'] = result[3]
    item['description'] = result[4]
    item['price'] = 0.5 * result[5]


    await add_item(ctx.author.id, item['name'], (-1 * amount), item['emoji'], item['description'], item['price'])
    await add_coins(ctx.author.id, (amount * item['price']))
    await ctx.send(f"**{ctx.author}**, you successfully sold **{item['name']} {item['emoji']}** **x {amount}** for **{int(item['price']) * amount}** :coin:")

    db.commit()
    cursor.close()
    db.close()

def setup(bot):
    bot.add_command(sell)
