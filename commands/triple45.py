from discord.ext import commands
import json
import random
import math
from main import bot
from db_functions import add_coins, add_xp, get_level, get_kriddytoo_shrine_boost, add_kriddytoo_shrine_boost, captcha

triple45file = open("jumps/triple45s.json", "r")
TRIPLE45 = json.loads(triple45file.read())

@commands.command(name = "triple45", aliases = ["tri45"], description = "Attempt a triple 45")
@commands.bot_has_permissions(send_messages=True)
@commands.guild_only()
@commands.cooldown(1, 60, commands.BucketType.user)
async def triple45(ctx, coords="0.0"):
    try:
        coords = float(coords)
    except:
        coords = 0.0

    if await get_level(ctx.author.id) < 15:
        return await ctx.send(f"**{ctx.author}**, triple 45ing requires **level 15**")

    if await get_kriddytoo_shrine_boost(ctx.author.id) > 0:
        kriddytoo_boost = 5
        await add_kriddytoo_shrine_boost(ctx.author.id, -1)
    else:
        kriddytoo_boost = 0


    selected = random.choice(TRIPLE45["triple45s"])

    strength1 = round(random.uniform(-5, 5) * (25 / (25 + kriddytoo_boost + await get_level(ctx.author.id))), 4)
    strength2 = random.randint(0,50) + await get_level(ctx.author.id) + kriddytoo_boost

    strength3 = round(random.uniform(-5, 5) * (25 / (25 + kriddytoo_boost + await get_level(ctx.author.id))), 4)
    strength4 = random.randint(0,50) + await get_level(ctx.author.id) + kriddytoo_boost

    total_speed1 = 0

    #calculate distance
    selected = random.choice(TRIPLE45["triple45s"])

    jump_angle1 = strength1
    facing1 = (45 * (0.9708**strength2))
    landing_speed1 = selected['landing_speed']
    airtime1 = selected['momentum_airtime']

    jump_speed1 = (landing_speed1 * 0.91) + 0.3274 * math.cos(jump_angle1 * (math.pi / 180))

    total_speed1 = landing_speed1 + jump_speed1 + ((jump_speed1 * 0.91 * 0.6) + (0.02 * 1.3 * math.cos(facing1 * (math.pi / 180))))
    current_speed1 = (jump_speed1 * 0.91 * 0.6) + (0.02 * 1.3 * math.cos(facing1 * (math.pi / 180)))

    for i in range(airtime1 - 3):
        current_speed1 = ((current_speed1 * 0.91) + 0.02 * 1.3)
        total_speed1 = total_speed1 + current_speed1

    current_speed1 = ((current_speed1 * 0.91) + 0.02 * 1.3)

    unused_momentum = selected['optimal_distance'] - total_speed1 - coords

    if unused_momentum < 0:
        message = [f"**{ctx.author}**, you overshot the **{selected['name']}** by **{round(-unused_momentum,8)}**"]
        message.append(f"First turn to 0: **{strength1}**, second 45 initial angle: **{round(45 - (45 * (0.9708**strength2)), 6)}**")
        await ctx.send('\n'.join(map(str, message)))
        await add_xp(ctx.author.id, 100, ctx)
    
        
        return


    #actual jump

    jump_angle = strength3
    facing = (45 * (0.9708**strength4))
    landing_speed = current_speed1
    airtime = selected['airtime']

    jump_speed = (landing_speed * 0.91) + 0.3274 * math.cos(jump_angle * (math.pi / 180))

    total_speed = landing_speed + jump_speed + ((jump_speed * 0.91 * 0.6) + (0.02 * 1.3 * math.cos(facing * (math.pi / 180))))
    current_speed = (jump_speed * 0.91 * 0.6) + (0.02 * 1.3 * math.cos(facing * (math.pi / 180)))

    for i in range(airtime - 3):
        current_speed = ((current_speed * 0.91) + 0.02 * 1.3)
        total_speed = total_speed + current_speed


    if (total_speed - unused_momentum) > (selected['distance'] - 0.6 ): #made jump
        message = [f"Congratulations! **{ctx.author}**, you did the **{selected['name']}** and earned **{selected['reward']}** :coin:."]

    elif total_speed > (selected['distance'] - 0.6): #made distance
        message = [f"**{ctx.author}**, you failed but made distance of the **{selected['name']}**"]
    else:
        message = [f"**{ctx.author}**, you failed the **{selected['name']}**"]
        
    message.append(f"Offset: **{round(total_speed - unused_momentum + 0.6 - selected['distance'], 8)}**")
    message.append(f"Offset on distance: **{round(total_speed + 0.6 - selected['distance'], 8)}**")
    message.append(f"First turn to 0: **{strength1}**, second 45 initial angle: **{round(45 - (45 * (0.9708**strength2)), 6)}**")
    message.append(f"Second turn to 0: **{strength3}**, third 45 initial angle: **{round(45 - (45 * (0.9708**strength4)), 6)}**")


    await ctx.send('\n'.join(map(str, message)))

    if (total_speed - unused_momentum) > (selected['distance'] - 0.6):
        await add_coins(ctx.author.id, selected['reward'])
        await add_xp(ctx.author.id, 1500, ctx)
    elif total_speed > (selected['distance'] - 0.6):
        await add_xp(ctx.author.id, 500, ctx)
    else:
        await add_xp(ctx.author.id, 100, ctx)




    if random.randint(1, 250) == 0:
        await captcha(ctx, ctx.author.id, bot)


def setup(bot):
    bot.add_command(triple45)
