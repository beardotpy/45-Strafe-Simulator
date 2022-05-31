import discord
from discord.ext import commands
from db_functions import add_coins, get_level, add_xp, get_kriddytoo_shrine_boost, add_kriddytoo_shrine_boost, get_shop_item_index
import sqlite3

@commands.command(name = "inventory", aliases = ["inv", "items"], description = "View your item inventory")
@commands.bot_has_permissions(send_messages=True)
@commands.guild_only()
@commands.cooldown(1, 5, commands.BucketType.user)
async def inventory(ctx, page='1'):
    try:
        page_number = int(page)
        page_number = page_number - 1
    except:
        page_number = 0
    if page_number < 0:
        page_number = 0

    db = sqlite3.connect('database.sqlite')
    cursor = db.cursor()
    cursor.execute(f"SELECT name FROM items WHERE id = {ctx.author.id}")
    result = cursor.fetchone()
    if result is None:
        return await ctx.send(f"**{ctx.author}**, your inventory is empty.")

    cursor.execute("DELETE FROM items WHERE amount = 0")
    
    cursor.execute(f"SELECT name FROM items WHERE id = {ctx.author.id}")
    result = cursor.fetchall()

    em = discord.Embed(title = f"{ctx.author}'s Inventory", description = f"Page {page_number+1} of your inventory, items listed below.", color = ctx.author.color)


    for i in range(5):
        try:
            index = i + (page_number * 5)

            name = result[(index)]
            cursor.execute(f"SELECT amount FROM items WHERE id = {ctx.author.id}")
            amount = cursor.fetchall()[index]
            cursor.execute(f"SELECT emoji FROM items WHERE id = {ctx.author.id}")
            emoji = cursor.fetchall()[index]
            cursor.execute(f"SELECT description FROM items WHERE id = {ctx.author.id}")
            description = cursor.fetchall()[index]
            cursor.execute(f"SELECT price FROM items WHERE id = {ctx.author.id}")
            price = cursor.fetchall()[index]

            
            item = {}
            item['name'] = name[0]
            item['amount'] = amount[0]
            item['emoji'] = emoji[0]
            item['description'] = description[0]
            item['price'] = price[0]


            em.add_field(name = f"{item['name']} {item['emoji']} x {item['amount']}\n(Worth: **{item['price']} :coin:**)", value = f"```{item['description']}```", inline = False)
        
        except:
            pass
    

    await ctx.send(embed = em)

    db.commit()
    cursor.close()
    db.close()


def setup(bot):
    bot.add_command(inventory)
