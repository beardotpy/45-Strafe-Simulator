from discord.ext import commands
import json
import random
import math
import discord
from main import bot
from db_functions import add_coins, add_xp, get_level, captcha

single45file = open("jumps/single45s.json", "r")
SINGLE45 = json.loads(single45file.read())

@commands.command(name = "single45", aliases = ["45"], description = "Attempt a single 45")
@commands.bot_has_permissions(send_messages=True)
@commands.guild_only()
@commands.cooldown(1, 10, commands.BucketType.user)
async def single45(ctx):
    strength = random.randint(0,50) + await get_level(ctx.author.id)

    total_speed = 0
    selected = random.choice(SINGLE45["single45s"])


    #repeat until you roll a 45 you can do
    while total_speed < (selected['distance'] - 0.6):
        selected = random.choice(SINGLE45["single45s"])

        jump_angle = 0
        facing = (45 * (0.9708**strength))
        landing_speed = selected['landing_speed']
        airtime = selected['airtime']

        jump_speed = (landing_speed * 0.91) + 0.3274 * math.cos(jump_angle * (math.pi / 180))

        total_speed = landing_speed + jump_speed + ((jump_speed * 0.91 * 0.6) + (0.02 * 1.3 * math.cos(facing * (math.pi / 180))))
        current_speed = (jump_speed * 0.91 * 0.6) + (0.02 * 1.3 * math.cos(facing * (math.pi / 180)))


        for i in range(airtime - 3):
            current_speed = ((current_speed * 0.91) + 0.02 * 1.3)
            total_speed = total_speed + current_speed

        if 'neo' in selected:
            total_speed = total_speed * random.randint(0,1)

    await ctx.send(f"**{ctx.author}**, you did the **{selected['name']}** and earned **{selected['reward']}** :coin:. Your last 45 was **{round(45 - facing, 6)}**, and you made the jump by **{round((total_speed - (selected['distance'] - 0.6)), 6)}**")

    await add_coins(ctx.author.id, selected['reward'])

    await add_xp(ctx.author.id, 100, ctx)

    if random.randint(1, 250) == 0:
        await captcha(ctx, ctx.author.id, bot)


def setup(bot):
    bot.add_command(single45)

