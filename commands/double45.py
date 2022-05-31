from discord.ext import commands
import json
import math
import random
from main import bot
from db_functions import add_coins, add_xp, get_level, get_kriddytoo_shrine_boost, add_kriddytoo_shrine_boost, captcha

double45file = open("jumps/double45s.json", "r")
DOUBLE45 = json.loads(double45file.read())

@commands.command(name = "double45", aliases = ["dub45"], description = "Attempt a double 45") 
@commands.bot_has_permissions(send_messages=True)
@commands.guild_only()
@commands.cooldown(1, 20, commands.BucketType.user)
async def double45(ctx):

    if await get_kriddytoo_shrine_boost(ctx.author.id) > 0:
        kriddytoo_boost = 5
        await add_kriddytoo_shrine_boost(ctx.author.id, -1)
    else:
        kriddytoo_boost = 0

    if await get_level(ctx.author.id) < 5:
        return await ctx.send(f"**{ctx.author}**, double 45ing requires **level 5**")

    selected = random.choice(DOUBLE45["double45s"])
    strength1 = round(random.uniform(-5, 5) * (25 / (25 + kriddytoo_boost + await get_level(ctx.author.id))), 4)
    strength2 = random.randint(0,50) + await get_level(ctx.author.id) + kriddytoo_boost
    jumps_rolled = 0
    total_speed = 0

    #math

    while total_speed < (selected['distance'] - 0.6) and jumps_rolled < 3:
        selected = random.choice(DOUBLE45["double45s"])
        jump_angle = strength1
        facing = (45 * (0.9708**strength2))
        landing_speed = selected['landing_speed']
        airtime = selected['airtime']

        jump_speed = (landing_speed * 0.91) + 0.3274 * math.cos(jump_angle * (math.pi / 180))

        total_speed = landing_speed + jump_speed + ((jump_speed * 0.91 * 0.6) + (0.02 * 1.3 * math.cos(facing * (math.pi / 180))))
        current_speed = (jump_speed * 0.91 * 0.6) + (0.02 * 1.3 * math.cos(facing * (math.pi / 180)))


        for i in range(airtime - 3):
            current_speed = ((current_speed * 0.91) + 0.02 * 1.3)
            total_speed = total_speed + current_speed

        if total_speed > (selected['distance'] - 0.6):
            await ctx.send(f"**{ctx.author}**, you did the **{selected['name']}** and earned **{selected['reward']}** :coin:. Your jump angle was **{round(jump_angle, 6)}** and your second 45 initial angle was **{round(45 - facing, 6)}**, and you made the jump by **{round((total_speed - (selected['distance'] - 0.6)), 6)}**")
            
            await add_coins(ctx.author.id, selected['reward'])
            await add_xp(ctx.author.id, 300, ctx)
            return

        jumps_rolled = jumps_rolled + 1

    await ctx.send(f"**{ctx.author}**, you failed the **{selected['name']}**. Your jump angle was **{round(jump_angle, 6)}** and your second 45 initial angle was **{round(45 - facing, 6)}**, and you missed the jump by **{round((total_speed - (selected['distance'] - 0.6)), 6)}**")
    await add_xp(ctx.author.id, 100, ctx)

    if random.randint(1, 250) == 0:
        await captcha(ctx, ctx.author.id, bot)

def setup(bot):
    bot.add_command(double45)
