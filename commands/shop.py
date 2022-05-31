import discord
from discord.ext import commands
from db_functions import add_coins, get_level, add_xp, get_kriddytoo_shrine_boost, add_kriddytoo_shrine_boost, get_shop_item_index

@commands.command(name = "shop", aliases = ["store"], description = "Check out purchasable special items")
@commands.bot_has_permissions(send_messages=True)
@commands.guild_only()
@commands.cooldown(1, 5, commands.BucketType.user)
async def shop(ctx, page='1'):
    try:
        page_number = int(page)
        page_number = page_number - 1
    except:
        page_number = 0
    if page_number < 0:
        page_number = 0

    if await get_level(ctx.author.id) < 2:
        return await ctx.send(f"**{ctx.author}**, visiting the shop requires **level 2**")

    em = discord.Embed(title = "Item Shop", description = f"Page {page_number+1} of the shop, items listed below.", color = ctx.author.color)

    for i in range(5):
        try:
            item = await get_shop_item_index((page_number * 5) + i)
            em.add_field(name = f"{item['name']} {item['emoji']}", value = f"Price: **{item['price']} :coin:**\nLevel Req: **{item['level_req']}**\n```{item['description']}```", inline = False)
        except:
            pass
    

    await ctx.send(embed = em)



def setup(bot):
    bot.add_command(shop)
