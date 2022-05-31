import discord
from discord.ext import commands
from db_functions import get_coins, get_level, get_xp, get_kriddytoo_shrine_boost, add_coins, add_xp
from main import bot
import sqlite3
import random

@commands.command(name = "trivia", description = "Play trivia and earn some rewards")
@commands.bot_has_permissions(send_messages=True)
@commands.guild_only()
@commands.cooldown(1, 20, commands.BucketType.user)
async def trivia(ctx):
    
    db = sqlite3.connect('database.sqlite')
    cursor = db.cursor()
    cursor.execute(f"SELECT name FROM items WHERE id = {ctx.author.id} AND name = 'textbook'")
    textbook = cursor.fetchone()
    if textbook is None:
        return await ctx.send(f"**{ctx.author}**, you must own a **textbook** to play trivia.")
    
    cursor.execute("SELECT question FROM trivia")
    index = random.randint(1, len(cursor.fetchall()))

    cursor.execute("SELECT * FROM trivia")
    trivia_question = cursor.fetchall()[index-1]
    question = trivia_question[0]
    correct = trivia_question[1]
    incorrect = (trivia_question[2], trivia_question[3], trivia_question[4])
    incorrect = tuple(random.sample(incorrect, len(incorrect)))
    difficulty = trivia_question[5]

    correct_index = random.randint(1, 4)

    db.commit()
    cursor.close()
    db.close()


    em = discord.Embed(title = f"**{ctx.author}**'s Trivia Game", description = f"{question} (Difficulty: **{difficulty}/10**)\n(Answer with 1, 2, 3, or 4, you have 20 seconds.)", color = ctx.author.color)

    for i in range(correct_index - 1):
        em.add_field(name = f"#{i + 1}", value = incorrect[i])
    em.add_field(name = f"#{correct_index}", value = correct)
    for i in range(4 - correct_index):
        em.add_field(name = f"#{correct_index + i + 1}", value = incorrect[correct_index + i - 1])
    
    await ctx.send(embed = em)

    try:
        msg = await bot.wait_for("message", check = lambda m: m.author == ctx.author and m.channel == ctx.channel and (m.content == "1" or m.content == "2" or m.content == "3" or m.content == "4"), timeout = 20)
        if(msg.content.isnumeric()):
            if(int(msg.content) > 0 and int(msg.content) < 5):
                if(int(msg.content) == correct_index):
                    reward = random.randint(10, 20) * difficulty

                    await ctx.send(f"**{ctx.author}** congratulations you answered correctly, you earned **{reward}** :coin:")
                    await add_coins(ctx.author.id, reward)
                    await add_xp(ctx.author.id, (150 + (difficulty * 10)), ctx)

                    return
                else:
                    await ctx.send(f"**{ctx.author}** nice try you answered incorrectly, the correct answer was **{correct}**")
                    await add_xp(ctx.author.id, (100), ctx)

                    return
    except:
        await ctx.send(f"**{ctx.author}**, you ran out of time")


def setup(bot):
    bot.add_command(trivia)
