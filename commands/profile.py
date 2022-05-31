import discord
from discord.ext import commands
from db_functions import get_coins, get_level, get_xp, get_kriddytoo_shrine_boost
from main import bot
import sqlite3


@commands.command(name = "profile", aliases = ["user", "coins", "balance", "bal", "money"], description = "Show your profile and coins")
@commands.bot_has_permissions(send_messages=True)
@commands.guild_only()
@commands.cooldown(1, 5, commands.BucketType.user)


async def profile(ctx, target_id=None):

    try:
        target = await bot.fetch_user(target_id)
        if target is None:
            target = ctx.author
    except:
        try:
            target_id = target_id[2:-1]
            target_id = target_id.replace('!','')
            target = await bot.fetch_user(target_id)
            if target is None:
                target = ctx.author
        except:
            target = ctx.author

    

    db = sqlite3.connect('database.sqlite')
    cursor = db.cursor()
    cursor.execute(f"SELECT xp FROM users WHERE id = {target.id}")
    result = cursor.fetchone()
    if result is None:
        return await ctx.send(f"**{target}** has not used 45 Strafe Simulator before.")
    db.commit()
    cursor.close()
    db.close()

    current_level = await get_level(target.id)

    level_up_req = (10 * (current_level ** 2)) + (1000 * current_level) + 100

    em = discord.Embed(title = f"Profile of **{target}**", description = f"{target}'s 45 strafe profile", color = target.color)

    em.add_field(name = "Coins", value = f"{await get_coins(target.id)} :coin:")

    em.add_field(name = "Level", value = f"{current_level}\n(XP: {await get_xp(target.id)}/{level_up_req})")

    if await get_kriddytoo_shrine_boost(target.id) > 0:
        em.add_field(name = "KRiddytoo Shrine Boost", value = f"**{await get_kriddytoo_shrine_boost(target.id)}** uses remaining")

    await ctx.send(embed = em)


def setup(bot):
    bot.add_command(profile)
