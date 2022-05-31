import math
from main import bot
import discord, sqlite3, random
from discord.ext import commands
from db_functions import add_coins, add_xp, get_level, get_kriddytoo_shrine_boost, add_kriddytoo_shrine_boost
from datetime import datetime

instructions = "Use `?duel left` or `?duel right` to move positions, and `?duel attack <x_velocity> <y_velocity>` to launch your attack. You may move up to 3x per turn, and your turn ends once you attack."


@commands.command(name = "duel", description = "Duel another player in a catapult battle")
@commands.bot_has_permissions(send_messages=True)
@commands.guild_only()
@commands.cooldown(1, 1, commands.BucketType.user)
async def duel(ctx, subcommand = None):

    if subcommand is None:
        return await ctx.send(f"{ctx.author}, please input a player to duel.")

    player_1 = ctx.author
    player_2 = None
    try:
        player_2 = await bot.fetch_user(subcommand)
    except:
        try:
            subcommand = subcommand[2:-1]
            subcommand = subcommand.replace('!','')
            player_2 = await bot.fetch_user(subcommand)
        except:
            pass


    if player_2 is None:
        return

    if player_2 == player_1:
        return await ctx.send(f"**{player_1}** you can't duel yourself, stoner :moyai:")    

    if player_2.bot:
        return await ctx.send(f"**{player_1}** picked a fight with **{player_2}** and got instantly killed.")

    #player2 must say yes
    em = discord.Embed(title = f"Duel Request for {player_2}", description = f"**{player_2}**, **{player_1}** has sent you a duel request", color = ctx.author.color)
    em.add_field(name = "Duel Invitation", value = "Type `accept` or `reject` to respond. This will timeout in 20 seconds.")

    await ctx.send(embed = em)

    try:
        msg = await bot.wait_for("message", check = lambda m: m.author == player_2 and m.channel == ctx.channel and (m.content == "accept" or m.content == "reject"), timeout = 20)

        if msg.content == "accept":
            pass
        elif msg.content == "reject":
            return await ctx.send(f"**{player_1}**, **{player_2}** rejected your duel request.")

    except:
        return await ctx.send(f"**{player_2}**, the duel request from **{player_1}** has expired.")

    current_turn = 1
    moves_left = 3
    player1_health = 100
    player2_health = 100

    turn = 1


    #canvas frame

    canvas = [[],[],[],[],[],[],[],[],[],[],[],[]]

    for i in range(12):
        for j in range(12):
            canvas[i].append(":black_large_square:")

    #use y = sin0.5(x + rand(0, pi)) + rand(2, 5) to generate ground surface
    def sinfunction(x, x_random, y_random, mult_random):
        return math.sin(mult_random * (x + x_random)) + y_random

    x_rand = random.randrange(0, 3)
    y_rand = random.randrange(2, 4)
    mult_rand = random.uniform(0.25, 1)
    for i in range(12): 
        canvas[11-round(sinfunction(i, x_rand, y_rand, mult_rand))][i] = ":green_square:"

        #mark location of players
        if i == 1:
            canvas[10-round(sinfunction(i, x_rand, y_rand, mult_rand))][i] = ":blue_square:"
            player1_x = i
            player1_y = 10-round(sinfunction(i, x_rand, y_rand, mult_rand))
        if i == 10:
            canvas[10-round(sinfunction(i, x_rand, y_rand, mult_rand))][i] = ":red_square:"
            player2_x = i
            player2_y = 10-round(sinfunction(i, x_rand, y_rand, mult_rand))

    #fill in ground
    for i in range(12):
        for j in range(12):
            if canvas[i-1][j] == ":green_square:":
                canvas[i][j] = ":green_square:"

    #rendering
    content = []

    for i in range(12):
        content.append(''.join(map(str, canvas[i])))

    em = discord.Embed(title = f"Duel: {player_1} vs {player_2}", description = '\n'.join(map(str, content)), color = ctx.author.color)
    em.add_field(name = "Instructions", value = instructions, inline = False)
    em.add_field(name = f"{player_1}'s turn", value = f"Moves left: {moves_left}", inline = False)
    em.add_field(name = f":blue_square: {player_1} Health", value = f"{player1_health} / 100")
    em.add_field(name = f":red_square: {player_2} Health", value = f"{player2_health} / 100")

    original_msg = await ctx.send(embed = em)


    def clear_trajectory():
        for i in range(12):
            for j in range(12):
                if canvas[i][j] == ":black_square_button:":
                    canvas[i][j] = ":black_large_square:"


    #user response
    duel_open = True




    try:
        while duel_open is True:
            #player 1s turn
            if current_turn == 1:
                msg = await bot.wait_for("message", check = lambda m: m.author == player_1 and m.channel == ctx.channel and m.content.startswith('?duel'), timeout = 60)

                            
                args = msg.content.split(" ")
                
                #did not input subcommand
                if len(args) == 1:
                    duel_open = False
                    em = discord.Embed(title = f"Duel: {player_1} vs {player_2}", description = '\n'.join(map(str, content)), color = ctx.author.color)
                    em.add_field(name = "Instructions", value = instructions, inline = False)
                    em.add_field(name = "Last Action", value = f"```{player_1} attempted to start a new duel, this one has been forfeited.```", inline = False)
                    em.add_field(name = f":blue_square: {player_1} Health", value = f"{player1_health} / 100")
                    em.add_field(name = f":red_square: {player_2} Health", value = f"{player2_health} / 100")
                            
                    return await original_msg.edit(embed = em)

                args.pop(0)
                
                #player moved left
                if args[0] == "left":
                    if player1_x == 0:
                        pass
                    
                    elif moves_left == 0:
                        await ctx.send(f"**{player_1}**, you have already moved three times and must attack now.", delete_after = 5)
                        pass

                    #wall
                    elif canvas[player1_y][player1_x-1] == ":green_square:" or canvas[player1_y][player1_x-1] == ":red_square:":
                        if canvas[player1_y-1][player1_x-1] == ":green_square:" or canvas[player1_y][player1_x-1] == ":red_square:":
                            pass
                        else:
                            clear_trajectory()
                            canvas[player1_y][player1_x] = ":black_large_square:"
                            player1_y = player1_y - 1
                            player1_x = player1_x - 1
                            canvas[player1_y][player1_x] = ":blue_square:"

                            moves_left = moves_left - 1

                    #no wall
                    else:
                        clear_trajectory()
                        canvas[player1_y][player1_x] = ":black_large_square:"
                        player1_x = player1_x - 1
                        canvas[player1_y][player1_x] = ":blue_square:"

                        moves_left = moves_left - 1

                        #falling
                        while canvas[player1_y + 1][player1_x] == ":black_large_square:":
                            canvas[player1_y][player1_x] = ":black_large_square:"
                            player1_y = player1_y + 1
                            canvas[player1_y][player1_x] = ":blue_square:"

                    await msg.delete()

                    content = []

                    for i in range(12):
                        content.append(''.join(map(str, canvas[i])))

                    em = discord.Embed(title = f"Duel: {player_1} vs {player_2}", description = '\n'.join(map(str, content)), color = ctx.author.color)
                    em.add_field(name = "Instructions", value = instructions, inline = False)
                    em.add_field(name = "Last Action", value = f"```{player_1} moved left```", inline = False)
                    em.add_field(name = f"{player_1}'s turn", value = f"Moves left: {moves_left}", inline = False)
                    em.add_field(name = f":blue_square: {player_1} Health", value = f"{player1_health} / 100")
                    em.add_field(name = f":red_square: {player_2} Health", value = f"{player2_health} / 100")
                        
                    await original_msg.edit(embed = em)

                #player moved right
                elif args[0] == "right":
                    if player1_x == 11:
                        pass

                    elif moves_left == 0:
                        await ctx.send(f"**{player_1}**, you have already moved three times and must attack now.", delete_after = 5)
                        pass

                    #wall
                    elif canvas[player1_y][player1_x+1] == ":green_square:" or canvas[player1_y][player1_x+1] == ":red_square:":
                        if canvas[player1_y-1][player1_x+1] == ":green_square:" or canvas[player1_y-1][player1_x+1] == ":red_square:":
                            pass
                        else:
                            clear_trajectory()
                            canvas[player1_y][player1_x] = ":black_large_square:"
                            player1_y = player1_y - 1
                            player1_x = player1_x + 1
                            canvas[player1_y][player1_x] = ":blue_square:"

                            moves_left = moves_left - 1

                    #no wall
                    else:
                        clear_trajectory()
                        canvas[player1_y][player1_x] = ":black_large_square:"
                        player1_x = player1_x + 1
                        canvas[player1_y][player1_x] = ":blue_square:"

                        moves_left = moves_left - 1

                        #falling
                        while canvas[player1_y + 1][player1_x] == ":black_large_square:":
                            canvas[player1_y][player1_x] = ":black_large_square:"
                            player1_y = player1_y + 1
                            canvas[player1_y][player1_x] = ":blue_square:"

                    await msg.delete()

                    content = []

                    for i in range(12):
                        content.append(''.join(map(str, canvas[i])))

                    em = discord.Embed(title = f"Duel: {player_1} vs {player_2}", description = '\n'.join(map(str, content)), color = ctx.author.color)
                    em.add_field(name = "Instructions", value = instructions, inline = False)
                    em.add_field(name = "Last Action", value = f"```{player_1} moved right```", inline = False)
                    em.add_field(name = f"{player_1}'s turn", value = f"Moves left: {moves_left}", inline = False)
                    em.add_field(name = f":blue_square: {player_1} Health", value = f"{player1_health} / 100")
                    em.add_field(name = f":red_square: {player_2} Health", value = f"{player2_health} / 100")
                        
                    await original_msg.edit(embed = em)


                #player attacked
                elif args[0] == "attack":
                    if len(args) < 3:
                        await ctx.send(f"{player_1.mention}, please use the syntax `?duel attack <x_velocity> <y_velocity>`. The <> brackets are omitted.", delete_after = 10)
                        await msg.delete()
                    else:
                        try:
                            args[1] = float(args[1])
                            args[2] = float(args[2])
                        except:
                            await ctx.send(f"{player_1.mention}, your x and y velocities must be numbers.", delete_after = 10)
                            await msg.delete()
                            continue

                        if abs(args[1]) > 1 or args[2] > 1 or args[2] < 0:
                            await ctx.send(f"{player_1.mention}, your x velocity must be between `-1` and `1`, and your y velocity must be between `0` and `1`.", delete_after = 10)
                            await msg.delete()
                            continue

                        clear_trajectory()

                        if float(args[1]) < 0.0:
                            facing = 180 * (math.pi / 180)
                        else:
                            facing = 0 * (math.pi / 180)

                        trajectory = []

                        #tick 1
                        jump_speed_x = abs(float(args[1])) * math.cos(facing)
                        jump_speed_y = abs(float(args[2]))

                        total_speed_x = jump_speed_x
                        total_speed_y = jump_speed_y

                        #add to trajectory
                        trajectory.append((player1_y - total_speed_y, player1_x + total_speed_x))

                        jump_speed_x = (jump_speed_x * 0.91 * 0.6) + (0.02 * 1.3 * math.cos(facing))
                        jump_speed_y = (jump_speed_y - 0.08) * 0.98

                        total_speed_x = total_speed_x + jump_speed_x
                        total_speed_y = total_speed_y + jump_speed_y

                        #add to trajectory
                        trajectory.append((player1_y - total_speed_y, player1_x + total_speed_x))

                        #repeat until hit player or wall
                        try:
                            while canvas[round(trajectory[len(trajectory)-1][0])][round(trajectory[len(trajectory)-1][1])] == ":black_large_square:" or trajectory[len(trajectory)-1][0] < 0: 
                                
                                jump_speed_x = (jump_speed_x * 0.91) + (0.02 * 1.3 * math.cos(facing))
                                total_speed_x = total_speed_x + jump_speed_x

                                jump_speed_y = (jump_speed_y - 0.08) * 0.98
                                total_speed_y = total_speed_y + jump_speed_y

                                #add to trajectory
                                if (player1_x + total_speed_x) < 0:
                                    break
                                else:
                                    trajectory.append((player1_y - total_speed_y, player1_x + total_speed_x))

                        except:
                            pass

                        jump_speed_y = (jump_speed_y - 0.08) * 0.98
                        total_speed_y = total_speed_y + jump_speed_y
                        
                        #draw trajectory
                        last_action = f"{player_1} attacked, it is now {player_2}'s turn"
                        for i in range(len(trajectory)):
                            try:
                                if round(trajectory[i][0]) > 0:
                                    if canvas[round(trajectory[i][0])][round(trajectory[i][1])] == ":blue_square:":
                                        continue
                                    elif canvas[round(trajectory[i][0])][round(trajectory[i][1])] == ":red_square:":
                                        if turn != 1:
                                            damage = round(20 * (1 - abs(round(trajectory[i][1])-trajectory[i][1])))
                                            last_action = f"{player_1} hit {player_2} for {damage} damage, it is now {player_2}'s turn"
                                            player2_health = player2_health - damage
                                        pass
                                    elif canvas[round(trajectory[i][0])][round(trajectory[i][1])] == ":green_square:":
                                        last_action = f"{player_1} attacked, it is now {player_2}'s turn"
                                        pass
                                    else:
                                        canvas[round(trajectory[i][0])][round(trajectory[i][1])] = ":black_square_button:"
                            except:
                                pass

                        content = []

                        for i in range(12):
                            content.append(''.join(map(str, canvas[i])))

                        if turn == 1:
                            last_action = f"{player_1} attacked, but damage was nullified as it is the first turn of the game. It is now {player_2}'s turn."
                            turn = 2

                        em = discord.Embed(title = f"Duel: {player_1} vs {player_2}", description = '\n'.join(map(str, content)), color = ctx.author.color)
                        em.add_field(name = "Instructions", value = instructions, inline = False)
                        em.add_field(name = "Last Action", value = f"```{last_action}```", inline = False)
                        em.add_field(name = f":blue_square: {player_1} Health", value = f"{player1_health} / 100")
                        em.add_field(name = f":red_square: {player_2} Health", value = f"{player2_health} / 100")
                            
                        await original_msg.edit(embed = em)
                        await msg.delete()

                        if player1_health < 1:
                            duel_open = False
                            return await ctx.send(f"**{player_2}** won the duel!")

                        if player2_health < 1:
                            duel_open = False
                            return await ctx.send(f"**{player_1}** won the duel!")

                        current_turn = 2
                        moves_left = 3

                #close duel
                else:
                    try:
                        possible_player = await bot.fetch_user(args[0])
                    except:
                        try:
                            args[0] = args[0][2:-1]
                            args[0] = args[0].replace('!','')
                            possible_player = await bot.fetch_user(args[0])
                        except:
                            possible_player = None
                            pass
                    if possible_player is None:
                        await ctx.send(f"{player_1.mention}, that is not a valid action.", delete_after = 10)
                        continue
                    else:
                        duel_open = False
                        em = discord.Embed(title = f"Duel: {player_1} vs {player_2}", description = '\n'.join(map(str, content)), color = ctx.author.color)
                        em.add_field(name = "Instructions", value = instructions, inline = False)
                        em.add_field(name = "Last Action", value = "```Invalid action, this duel was forfeited.```", inline = False)
                        em.add_field(name = f":blue_square: {player_1} Health", value = f"{player1_health} / 100")
                        em.add_field(name = f":red_square: {player_2} Health", value = f"{player2_health} / 100")
                                
                        return await original_msg.edit(embed = em)




            #player 2s turn
            if current_turn == 2:
                msg = await bot.wait_for("message", check = lambda m: m.author == player_2 and m.channel == ctx.channel and m.content.startswith('?duel'), timeout = 60)

                            
                args = msg.content.split(" ")
                
                #did not input subcommand
                if len(args) == 1:
                    duel_open = False
                    em = discord.Embed(title = f"Duel: {player_1} vs {player_2}", description = '\n'.join(map(str, content)), color = ctx.author.color)
                    em.add_field(name = "Instructions", value = instructions, inline = False)
                    em.add_field(name = "Last Action", value = f"```{player_2} attempted to start a new duel, this one has been forfeited.```", inline = False)
                    em.add_field(name = f":blue_square: {player_1} Health", value = f"{player1_health} / 100")
                    em.add_field(name = f":red_square: {player_2} Health", value = f"{player2_health} / 100")
                            
                    return await original_msg.edit(embed = em)

                args.pop(0)
                
                #player moved left
                if args[0] == "left":
                    if player2_x == 0:
                        pass
                    
                    elif moves_left == 0:
                        await ctx.send(f"**{player_2}**, you have already moved three times and must attack now.", delete_after = 5)
                        pass

                    #wall
                    elif canvas[player2_y][player2_x-1] == ":green_square:" or canvas[player2_y][player2_x-1] == ":blue_square:":
                        if canvas[player2_y-1][player2_x-1] == ":green_square:" or canvas[player2_y][player2_x-1] == ":blue_square:":
                            pass
                        else:
                            canvas[player2_y][player2_x] = ":black_large_square:"
                            player2_y = player2_y - 1
                            player2_x = player2_x - 1
                            canvas[player2_y][player2_x] = ":red_square:"

                            moves_left = moves_left - 1

                    #no wall
                    else:
                        canvas[player2_y][player2_x] = ":black_large_square:"
                        player2_x = player2_x - 1
                        canvas[player2_y][player2_x] = ":red_square:"

                        moves_left = moves_left - 1

                        #falling
                        while canvas[player2_y + 1][player2_x] == ":black_large_square:":
                            canvas[player2_y][player2_x] = ":black_large_square:"
                            player2_y = player2_y + 1
                            canvas[player2_y][player2_x] = ":red_square:"

                    await msg.delete()

                    clear_trajectory()

                    content = []

                    for i in range(12):
                        content.append(''.join(map(str, canvas[i])))

                    em = discord.Embed(title = f"Duel: {player_1} vs {player_2}", description = '\n'.join(map(str, content)), color = ctx.author.color)
                    em.add_field(name = "Instructions", value = instructions, inline = False)
                    em.add_field(name = "Last Action", value = f"```{player_2} moved left```", inline = False)
                    em.add_field(name = f"{player_2}'s turn", value = f"Moves left: {moves_left}", inline = False)
                    em.add_field(name = f":blue_square: {player_1} Health", value = f"{player1_health} / 100")
                    em.add_field(name = f":red_square: {player_2} Health", value = f"{player2_health} / 100")
                        
                    await original_msg.edit(embed = em)

                #player moved right
                elif args[0] == "right":
                    if player2_x == 11:
                        pass

                    elif moves_left == 0:
                        await ctx.send(f"**{player_2}**, you have already moved three times and must attack now.", delete_after = 5)
                        pass

                    #wall
                    elif canvas[player2_y][player2_x+1] == ":green_square:" or canvas[player2_y][player2_x+1] == ":blue_square:":
                        if canvas[player2_y-1][player2_x+1] == ":green_square:" or canvas[player2_y-1][player2_x+1] == ":blue_square:":
                            pass
                        else:
                            canvas[player2_y][player2_x] = ":black_large_square:"
                            player2_y = player2_y - 1
                            player2_x = player2_x + 1
                            canvas[player2_y][player2_x] = ":red_square:"

                            moves_left = moves_left - 1

                    #no wall
                    else:
                        canvas[player2_y][player2_x] = ":black_large_square:"
                        player2_x = player2_x + 1
                        canvas[player2_y][player2_x] = ":red_square:"

                        moves_left = moves_left - 1

                        #falling
                        while canvas[player2_y + 1][player2_x] == ":black_large_square:":
                            canvas[player2_y][player2_x] = ":black_large_square:"
                            player2_y = player2_y + 1
                            canvas[player2_y][player2_x] = ":red_square:"

                    await msg.delete()

                    clear_trajectory()

                    content = []

                    for i in range(12):
                        content.append(''.join(map(str, canvas[i])))

                    em = discord.Embed(title = f"Duel: {player_1} vs {player_2}", description = '\n'.join(map(str, content)), color = ctx.author.color)
                    em.add_field(name = "Instructions", value = instructions, inline = False)
                    em.add_field(name = "Last Action", value = f"```{player_2} moved right```", inline = False)
                    em.add_field(name = f"{player_2}'s turn", value = f"Moves left: {moves_left}", inline = False)
                    em.add_field(name = f":blue_square: {player_1} Health", value = f"{player1_health} / 100")
                    em.add_field(name = f":red_square: {player_2} Health", value = f"{player2_health} / 100")
                        
                    await original_msg.edit(embed = em)


                #player attacked
                elif args[0] == "attack":
                    if len(args) < 3:
                        await ctx.send(f"{player_2.mention}, please use the syntax `?duel attack <x_velocity> <y_velocity>`. The <> brackets are omitted.", delete_after = 10)
                        await msg.delete()
                    else:
                        try:
                            args[1] = float(args[1])
                            args[2] = float(args[2])
                        except:
                            await ctx.send(f"{player_2.mention}, your x and y velocities must be numbers.", delete_after = 10)
                            await msg.delete()
                            continue

                        if abs(args[1]) > 1 or args[2] > 1 or args[2] < 0:
                            await ctx.send(f"{player_2.mention}, your x velocity must be between `-1` and `1`, and your y velocity must be between `0` and `1`.", delete_after = 10)
                            await msg.delete()
                            continue

                        clear_trajectory()

                        if float(args[1]) < 0.0:
                            facing = 180 * (math.pi / 180)
                        else:
                            facing = 0 * (math.pi / 180)

                        trajectory = []

                        #tick 1
                        jump_speed_x = abs(float(args[1])) * math.cos(facing)
                        jump_speed_y = abs(float(args[2]))

                        total_speed_x = jump_speed_x
                        total_speed_y = jump_speed_y

                        #add to trajectory
                        trajectory.append((player2_y - total_speed_y, player2_x + total_speed_x))

                        jump_speed_x = (jump_speed_x * 0.91 * 0.6) + (0.02 * 1.3 * math.cos(facing))
                        jump_speed_y = (jump_speed_y - 0.08) * 0.98

                        total_speed_x = total_speed_x + jump_speed_x
                        total_speed_y = total_speed_y + jump_speed_y

                        #add to trajectory
                        trajectory.append((player2_y - total_speed_y, player2_x + total_speed_x))

                        #repeat until hit player or wall
                        try:
                            while canvas[round(trajectory[len(trajectory)-1][0])][round(trajectory[len(trajectory)-1][1])] == ":black_large_square:" or trajectory[len(trajectory)-1][0] < 0: 
                                
                                jump_speed_x = (jump_speed_x * 0.91) + (0.02 * 1.3 * math.cos(facing))
                                total_speed_x = total_speed_x + jump_speed_x

                                jump_speed_y = (jump_speed_y - 0.08) * 0.98
                                total_speed_y = total_speed_y + jump_speed_y

                                #add to trajectory
                                if (player2_x + total_speed_x) < 0:
                                    break
                                else:
                                    trajectory.append((player2_y - total_speed_y, player2_x + total_speed_x))

                        except:
                            pass

                        jump_speed_y = (jump_speed_y - 0.08) * 0.98
                        total_speed_y = total_speed_y + jump_speed_y
                        
                        #draw trajectory
                        last_action = f"{player_2} attacked, it is now {player_1}'s turn"
                        for i in range(len(trajectory)):
                            try:
                                if round(trajectory[i][0]) > 0:
                                    if canvas[round(trajectory[i][0])][round(trajectory[i][1])] == ":red_square:":
                                        continue
                                    elif canvas[round(trajectory[i][0])][round(trajectory[i][1])] == ":blue_square:":
                                        damage = round(20 * (1 - abs(round(trajectory[i][1])-trajectory[i][1])))
                                        last_action = f"{player_2} hit {player_1} for {damage} damage, it is now {player_1}'s turn"
                                        player1_health = player1_health - damage
                                        pass
                                    elif canvas[round(trajectory[i][0])][round(trajectory[i][1])] == ":green_square:":
                                        last_action = f"{player_2} attacked, it is now {player_1}'s turn"
                                        pass
                                    else:
                                        canvas[round(trajectory[i][0])][round(trajectory[i][1])] = ":black_square_button:"
                            except:
                                pass

                        content = []

                        for i in range(12):
                            content.append(''.join(map(str, canvas[i])))

                        em = discord.Embed(title = f"Duel: {player_1} vs {player_2}", description = '\n'.join(map(str, content)), color = ctx.author.color)
                        em.add_field(name = "Instructions", value = instructions, inline = False)
                        em.add_field(name = "Last Action", value = f"```{last_action}```", inline = False)
                        em.add_field(name = f":blue_square: {player_1} Health", value = f"{player1_health} / 100")
                        em.add_field(name = f":red_square: {player_2} Health", value = f"{player2_health} / 100")
                            
                        await original_msg.edit(embed = em)
                        await msg.delete()

                        if player1_health < 1:
                            duel_open = False
                            return await ctx.send(f"**{player_2}** won the duel!")

                        if player2_health < 1:
                            duel_open = False
                            return await ctx.send(f"**{player_1}** won the duel!")

                        current_turn = 1
                        moves_left = 3

                #close duel
                else:
                    try:
                        possible_player = await bot.fetch_user(args[0])
                    except:
                        try:
                            args[0] = args[0][2:-1]
                            args[0] = args[0].replace('!','')
                            possible_player = await bot.fetch_user(args[0])
                        except:
                            possible_player = None
                            pass
                    if possible_player is None:
                        await ctx.send(f"{player_1.mention}, that is not a valid action.", delete_after = 10)
                        continue
                    else:
                        duel_open = False
                        em = discord.Embed(title = f"Duel: {player_1} vs {player_2}", description = '\n'.join(map(str, content)), color = ctx.author.color)
                        em.add_field(name = "Instructions", value = instructions, inline = False)
                        em.add_field(name = "Last Action", value = "```Invalid action, this duel was forfeited.```", inline = False)
                        em.add_field(name = f":blue_square: {player_1} Health", value = f"{player1_health} / 100")
                        em.add_field(name = f":red_square: {player_2} Health", value = f"{player2_health} / 100")
                                
                        return await original_msg.edit(embed = em)




    except:
        duel_open = False
        em = discord.Embed(title = f"Duel: {player_1} vs {player_2}", description = '\n'.join(map(str, content)), color = ctx.author.color)
        em.add_field(name = "Instructions", value = instructions, inline = False)
        em.add_field(name = "Last Action", value = "```Player ran out of time```", inline = False)
        em.add_field(name = f":blue_square: {player_1} Health", value = f"{player1_health} / 100")
        em.add_field(name = f":red_square: {player_2} Health", value = f"{player2_health} / 100")
                
        await original_msg.edit(embed = em)
        await ctx.send("You ran out of time.")
        

def setup(bot):
    bot.add_command(duel)
