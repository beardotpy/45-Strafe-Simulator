import discord
from discord.ext import commands
import sqlite3
import random
from db_functions import add_coins, get_level, add_xp, get_coins, get_kriddytoo_shrine_boost, add_kriddytoo_shrine_boost, get_shop_item, add_item

@commands.command(name = "slots", aliases = ["slotmachine"], description = "Use the man in the black coat's slot machine")
@commands.bot_has_permissions(send_messages=True)
@commands.guild_only()
@commands.cooldown(1, 10, commands.BucketType.user)
async def slots(ctx):

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

    if await get_coins(ctx.author.id) <  40:
        return await ctx.send(f":man_detective:: **{ctx.author}**, you need at least **40** :coin: to use the slot machine.")
    
    rewards = ["eggplant", "tomato", "lemon", "gem", "moneybag"]

    await add_coins(ctx.author.id, -40)

    slot1 = random.choice(rewards)
    slot2 = random.choice(rewards)
    slot3 = random.choice(rewards)

    em = discord.Embed(title = f"{ctx.author}'s Slot Game", description = f"You spent **40** :coin: on slots. \nYour roll:\n**\>>>** :{slot1}: :{slot2}: :{slot3}: **<<<**", color = ctx.author.color)    


    if slot1 == slot2 and slot2 == slot3:
        if slot1 == "gem":
            await add_item(ctx.author.id, "gem", 3, ":gem:", "Rare collectable item, has no use.", 500)
            text = f"You got three of a kind and won **3x {slot1}**"
        elif slot1 == "moneybag":
            await add_coins(ctx.author.id, 300)
            text = f"You got three of a kind and won **300** :coin:"
        else:
            await add_item(ctx.author.id, slot1, 3, f":{slot1}:", "Collectable item, has no use.", 20)
            text = f"You got three of a kind and won **3x {slot1}**"

    elif slot1 == slot2 or slot2 == slot3:
        if slot2 == "gem":
            await add_item(ctx.author.id, "gem", 1, ":gem:", "Rare collectable item, has no use.", 500)
            text = f"You got one of a kind and won **1x {slot2}**"
        elif slot2 == "moneybag":
            await add_coins(ctx.author.id, 100)
            text = f"You got one of a kind and won **100** :coin:"
        else:
            await add_item(ctx.author.id, slot2, 1, f":{slot2}:", "Collectable item, has no use.", 20)
            text = f"You got one of a kind and won **1x {slot2}**"

    elif slot1 == slot3:
        if slot3 == "gem":
            await add_item(ctx.author.id, "gem", 1, ":gem:", "Rare collectable item, has no use.", 500)
            text = f"You got one of a kind and won **1x {slot3}**"
        elif slot3 == "moneybag":
            await add_coins(ctx.author.id, 100)
            text = f"You got one of a kind and won **100** :coin:"
        else:
            await add_item(ctx.author.id, slot3, 1, f":{slot3}:", "Collectable item, has no use.", 20)
            text = f"You got one of a kind and won **1x {slot3}**"

    else:
        text = "Nothing was matching. Better luck next time!"
        
    em.add_field(name = "Rewards", value = f":detective:: {text}")
    await ctx.send(embed = em)
    await add_xp(ctx.author.id, 75, ctx)

def setup(bot):
    bot.add_command(slots)
