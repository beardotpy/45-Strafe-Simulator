import discord
from discord.ext import commands
from db_functions import add_coins, get_level, get_coins, get_kriddytoo_shrine_boost, add_kriddytoo_shrine_boost, get_shop_item, add_item

@commands.command(name = "buy", aliases = ["purchase"], description = "Buy an item from the shop")
@commands.bot_has_permissions(send_messages=True)
@commands.guild_only()
@commands.cooldown(1, 5, commands.BucketType.user)
async def buy(ctx, choice="null", amount="1"):

    if await get_level(ctx.author.id) < 2:
        return await ctx.send(f"**{ctx.author}**, buying items requires **level 2**")

    if choice == "null":
        return await ctx.send(f"**{ctx.author}**, please specify an item to purchase")

    item = await get_shop_item(choice)
    if item is None:
        return await ctx.send(f"**{ctx.author}**, that item is not in the shop!")

    try:
        amount = int(amount)
        if amount < 1:
            return await ctx.send(f"**{ctx.author}**, **\"{amount}\"** is not a valid amount.")
    except:
        return await ctx.send(f"**{ctx.author}**, **\"{amount}\"** is not a valid amount.")

    
    if await get_level(ctx.author.id) < item['level_req']:
        return await ctx.send(f"**{ctx.author}**, you are not high enough level to buy that item! \nLevel: **{await get_level(ctx.author.id)} / {item['level_req']}**")

    if await get_coins(ctx.author.id) < item['price'] * amount:
        return await ctx.send(f"**{ctx.author}**, you cannot afford item(s)! \nCoins missing: **{item['price'] * amount - await get_coins(ctx.author.id)}** :coin:")

    await add_item(ctx.author.id, item['name'], amount, item['emoji'], item['description'], item['price'])
    await add_coins(ctx.author.id, (-1 * item['price'] * amount))

    await ctx.send(f"**{ctx.author}**, you successfully purchased **{item['name']} {item['emoji']}** **x {amount}** for **{item['price'] * amount}** :coin:")


def setup(bot):
    bot.add_command(buy)
