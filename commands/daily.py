import discord
from discord.ext import commands
from db_functions import get_level, add_coins
from datetime import datetime, timedelta
import sqlite3

@commands.command(name = "daily", description = "Claim daily reward")
@commands.bot_has_permissions(send_messages=True)
@commands.guild_only()
@commands.cooldown(1, 5, commands.BucketType.user)
async def daily(ctx):

    if await get_level(ctx.author.id) < 3:
        return await ctx.send(f"**{ctx.author}**, claiming daily rewards requires **level 3**")

    current_time = datetime.now()
    tomorrow = (current_time + timedelta(days = 1)).replace(hour = 0, minute = 0)
    next_daily = f"{tomorrow - current_time}"[:-3]

    db = sqlite3.connect('database.sqlite')
    cursor = db.cursor()
    cursor.execute(f"SELECT has_claimed_daily FROM users WHERE id = {ctx.author.id}")
    has_claimed_daily = cursor.fetchone()[0]

    if has_claimed_daily == 1:
        
        em = discord.Embed(title = "Daily already claimed", description =f"**{ctx.author}**, you have already claimed your daily today.", color = ctx.author.color)

        em.add_field(name = "Next Daily:", value = next_daily)

        db.commit()
        cursor.close()
        db.close()
        return await ctx.send(embed = em)


    else:
        cursor.execute(f"SELECT daily_streak FROM users WHERE id = {ctx.author.id}")
        streak = cursor.fetchone()[0] + 1
        cursor.execute(f"UPDATE users SET daily_streak = {streak} WHERE id = {ctx.author.id}")
        reward = 10 * (await get_level(ctx.author.id) + streak + 10)

        em = discord.Embed(title = "Daily", description =f"**{ctx.author}**, you claimed your daily reward.", color = ctx.author.color)

        em.add_field(name = "Rewards:", value = f"You received **{reward} :coin:**")
        em.add_field(name = "Streak:", value = f"Current Streak: **{streak}**")
        em.add_field(name = "Next Daily:", value = next_daily)

        await ctx.send(embed = em)

        sql = ("UPDATE users SET has_claimed_daily = ? WHERE id = ?")
        val = (1, ctx.author.id)
        cursor.execute(sql, val)

        db.commit()
        cursor.close()
        db.close()

        await add_coins(ctx.author.id, reward)






def setup(bot):
    bot.add_command(daily)
