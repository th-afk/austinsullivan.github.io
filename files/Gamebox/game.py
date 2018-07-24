# Grayson Gatti (gtg8cd) AND Austin Sullivan (acs3ss)
# CS 1110 - Spring 2017
# Monday, May 1st 2017

import pygame
import gamebox
import random
import math


# this code uses stop_loop to exit ticks() function. Then changes level, resets the screen, etc before re-entering ticks
def tick(keys):
    global level, room, char_health, char_speed, frames, half_frames, attack_cooldown, attack_burst, flipped, \
        ability_burst, ability, kill_count, dead_enemies, level_screen, game_over, boss_appear, boss_health, dead_boss

    if game_over:
        end_game()

    half_frames += 1
    if half_frames % 2 == 0:
        frames += 1

    attacking = False
    walking = False
    left = False
    ability = False

    # causes an error, quitting the game when F1 hit
    if pygame.K_F1 in keys:
        level = -3
        gamebox.stop_loop()

    # home screen
    if level == -1:
        if camera.mouseclick:
            if clicking(start):
                gamebox.stop_loop()
    # select char screen
    if level == 0:
        # depending on which character is clicked, sets variables for future use. Then, stops loop to go to next level
        if camera.mouseclick:
            if clicking(knight):
                character = knight
                char_sheet = knight_sheet
                ability_sheet = knight_ability_sheet
                global char_sheet
                global ability_sheet
                gamebox.stop_loop()
            if clicking(ranger):
                character = ranger
                char_sheet = ranger_sheet
                ability_sheet = ranger_ability_sheet
                global char_sheet, ability_sheet
                gamebox.stop_loop()
            global character
    # setup is over, we're ready to play! These are the controls for actual gameplay
    if 0 < level <= 2 and not level_screen:
        # level one setup
        if level == 1:
            camera.draw(background)
            room_setup()
        # level two setup
        if level == 2:
            camera.draw(background)
            room_setup()

        # use the arrows to move
        if pygame.K_w in keys:
            character.y -= char_speed
            walking = True
        if pygame.K_s in keys:
            character.y += char_speed
            walking = True
        if pygame.K_d in keys:
            character.x += char_speed
            walking = True
        if pygame.K_a in keys:
            character.x -= char_speed
            walking = True
            left = True
        # space bar to attack
        if camera.mouseclick:
            if attack_burst <= 20 and attack_cooldown <= 0:  # can't attack continuously. Can attack for 1/3 sec at time
                attacking = True
                attack_burst += 1
            if attack_burst >= 20:
                attack_cooldown = 15  # cooldown before you're allowed to attack again
            if attack_burst == 1 and character == ranger:
                fire_arrow()
        else:
            attack_burst = 0
        attack_cooldown -= 1
        # Q to use abilities
        if pygame.K_q in keys:
            if kill_count >= 3:  # can use ability if ability bar is full enough
                ability = True
                kill_count -= 3
                ability_burst = 0
        ability_burst += 1
        if ability_burst <= 60:   # can't use ability continuously. Can use 2 sec at a time
            ability = True

        # arrow animations and removal
        moving_arrows(arrows)
        moving_arrows(skeleton_arrows)
        moving_arrows(boss_arrows)

        # enemy AI, boss AI
        enemy_movement()
        if boss_appear and not dead_boss:
            boss_movement(frames)

        # running into doors
        room_movement()

        # collecting hearts
        for heart in life:
            if character.touches(heart):
                life.remove(heart)
                # you can't have more than 100% health, silly
                if char_health > 90:
                    char_health = 100
                else:
                    char_health += 20

        # interactions with enemies. If knight is attacking, they die. If not, you take damage and get knocked back
        # arrows kill enemies
        for room_num, where in enumerate(enemies):
            if room_num == room:
                for index, (enemy, alive, species) in enumerate(where):
                    if character.touches(enemy) and alive:
                        if not ability:
                            rebound(character, enemy, attacking)
                            if not attacking or character == ranger:
                                char_health = take_damage(20, char_health)
                            else:
                                enemies[room_num][index][1] = False
                                dead_enemy(enemy)
                        if ability and (attacking or character == knight):
                            enemies[room_num][index][1] = False
                            dead_enemy(enemy)
                    for sharp in arrows:
                        if sharp[0].touches(enemy) and alive:
                            enemies[room_num][index][1] = False
                            dead_enemy(enemy)
                    for sharp in skeleton_arrows:
                        if sharp[0].touches(character):
                            skeleton_arrows.remove(sharp)
                            char_health = take_damage(20, char_health)

        # only draws living enemies. Also, checks to see if all enemies are dead
        num_enemies = 0
        for room_num, where in enumerate(enemies):
            for index, (enemy, alive, species) in enumerate(where):
                if alive:
                    num_enemies += 1
                    if room_num == room:
                        camera.draw(enemy)
        if num_enemies == 0:
            dead_enemies = True

        # handles interactions between character and bosses. Boss must be
        if character.touches(boss) and boss_appear:
            if not attacking and not ability:
                char_health = take_damage(20, char_health)
                rebound(character, boss, attacking)
            if attacking and character == knight:
                boss_health = take_damage(20, boss_health)
                rebound(character, boss, attacking)
        # ranger arrow interactions with bosses
        for arrow in arrows:
            if arrow[0].touches(boss) and boss_appear:
                boss_health = take_damage(10, boss_health)
                arrows.remove(arrow)
        # boss arrow interactions with character
        for sharp in boss_arrows:
            if sharp[0].touches(character):
                boss_arrows.remove(sharp)
                char_health = take_damage(20, char_health)


        # you can't run through walls
        [character.move_to_stop_overlapping(wall) for wall in border]
        [boss.move_to_stop_overlapping(wall) for wall in border]

        # draws walls, hearts after enemy death
        [camera.draw(wall) for wall in border]
        [camera.draw(heart) for heart in life]

        # exits level once you get to the end of the level. Also resets room to 0
        if character.touches(ladder) and dead_enemies and dead_boss:
            level_screen = True
            gamebox.stop_loop()

        # your health. Game pauses when you run out of life
        if char_health <= 0:
            game_over = True
        if character == ranger:
            char_health_bar = gamebox.from_image(75, 550, char_health_sheet[5 - int(char_health/20)])
        if character == knight:
            char_health_bar = gamebox.from_image(75, 550, char_health_sheet[5 - int(char_health/40)])
        camera.draw(char_health_bar)
        if boss_health <= 0:
            dead_boss = True
            boss_appear = False

        char_ability_bar = gamebox.from_image(75, 50, ability_bar_sheet[5 - kill_count])
        char_ability_bar.height = 20
        camera.draw(char_ability_bar)

        who_walking(char_sheet, attacking, walking, left, ability, ability_sheet)

        camera.draw(character)

    if level == 3:
        camera.draw(gamebox.from_text(400, 300, "You Win!", "Arial", 40, "gray"))
        if camera.mouseclick:
            gamebox.stop_loop()

    camera.display()

    # adds a level screen between each level. Click to continue
    if level_screen and level > 0:
        camera.clear('black')
        room = 0
        camera.draw(gamebox.from_image(400, 300, 'Level'+str(level)+'.png'))
        camera.display()
        if camera.mouseclick:
            level_screen = False


# home screen setup. Static page, no need to run ticks() other than to check to see if mouse if clicked
def home_screen():
    camera.clear('black')
    camera.draw(gamebox.from_image(400, 300, 'Title.png'))
    gamebox.timer_loop(ticks_per_second, tick)


# character selection screen setup. Again, static page. ticks() just looks for clicks on characters
def char_select():
    camera.clear('black')
    camera.draw(select_screen)
    gamebox.timer_loop(ticks_per_second, tick)


# returns true if an object is clicked on. Compares boundary coordinates to where mouse clicks
def clicking(box):
    (box_l, box_r), (box_t, box_b) = click_coords(box)
    # camera.mouse returns a tuple (x, y) with coordinates of click. Unpack and compare to boundaries of object
    if box_l < camera.mouse[0] < box_r and box_t < camera.mouse[1] < box_b:
        return True


# finds boundary coordinates of an object. This info is sent to clicking()
def click_coords(box):
    possible_x_max = box.right
    possible_x_min = box.left
    possible_y_max = box.bottom
    possible_y_min = box.top
    return (possible_x_min, possible_x_max), (possible_y_min, possible_y_max)


# changes image based on which char is selected on char selection page.
# changes sprite sheet based on if walking or attacking. flips char if moving left
# changes sprite sheet based on if using ability or not
def who_walking(sheet, attacking, walking, orientation, cloaked, cloak_sheet):
    global flipped, walk_time
    if cloaked:  # if using your ability, you're invisible to enemies!
       sheet = cloak_sheet
    if not attacking:
        if walking:
            character.image = sheet[(frames % 4) + 4]
        else:
            character.image = sheet[0]
        walk_time = 0
    else:
        walk_time += 0.5
        image_index = int(walk_time) % 4
        character.image = sheet[image_index]
    if flipped == orientation:  # flips character when moving left
        character.flip()
        if flipped:
            flipped = False
        else:
            flipped = True


# defines different movements for each kind of enemy. includes firing for skeletons
def enemy_movement():
    for room_num, where in enumerate(enemies):
        if room_num == room:
            for index, (enemy, alive, species) in enumerate(where):
                if not ability:  # as long as the character is cloaked....
                    chance = random.randrange(1000)  # random int to determine movement and attacking
                    # checks what kind of enemy it is
                    if species == 'slime':
                        if chance >= 980:
                            move_towards_char(enemy, 30)
                        else:
                            move_towards_char(enemy, 1)
                    if species == 'skeleton':
                        if chance >= 500:
                            move_towards_char(enemy, 2)
                        if chance >= 970 and alive:
                            enemy_fire(enemy)
                    if species == 'zombie':
                        if chance >= 995:
                            sprinting[index] = 25
                        try:
                            if sprinting[index] > 0:
                                move_towards_char(enemy, 25-sprinting[index])
                                sprinting[index] -= 1
                                if enemy.touches(character):
                                    sprinting[index] = 0
                            else:
                                move_towards_char(enemy, 1)
                        except:
                            pass
                else:
                    if ability_burst == 1:
                        enemy.speedx = random.randrange(-1, 1)
                        enemy.speedy = random.randrange(-1, 1)
                    enemy.move_speed()


# boss AI
def boss_movement(ticks):
    global boss_spree
    if ticks % 60 == 0:  # boss goes on rampage every two seconds
        boss_spree = 60
    if boss == boss_slime:
        if boss_spree == 60 or boss_spree == 30:
            x_diff = character.x - boss.x
            y_diff = character.y - boss.y
            scalar = math.sqrt(x_diff ** 2 + y_diff ** 2) // boss_sprint  # ensures that all arrows travel same speed
            charge = x_diff / scalar, y_diff / scalar
            global charge
        elif 0 < boss_spree < 15 or 30 < boss_spree < 45:
            boss.x += charge[0]
            boss.y += charge[1]
        else:
            move_towards_char(boss, 1)
    if boss == boss_phantom:
        if boss_spree >= 0:
            enemy_fire(boss)
        moving_time = ticks % 200
        if 0 <= moving_time < 50:
            boss.x += 3
        elif 50 <= moving_time < 100:
            boss.y += 3
        elif 100 <= moving_time < 150:
            boss.x -= 3
        else:
            boss.y -= 3
    boss_spree -= 1


# helper function to enemy_movement. Simply moves towards enemy
def move_towards_char(enemy, enemy_speed):
    buffer = 5
    if enemy.x > character.x + buffer:
        enemy.x -= enemy_speed
    if enemy.x < character.x - buffer:
        enemy.x += enemy_speed
    if enemy.y > character.y + buffer:
        enemy.y -= enemy_speed
    if enemy.y < character.y - buffer:
        enemy.y += enemy_speed


# fire arrows where mouse is
def fire_arrow():
    arrow = gamebox.from_image(character.x, character.y, 'Arrow.png')
    arrow_speed = 10
    x_diff = camera.mouse[0] - character.x
    y_diff = camera.mouse[1] - character.y
    scalar = math.sqrt(x_diff ** 2 + y_diff ** 2) // arrow_speed  # ensures that all arrows travel same speed
    direction = x_diff / scalar, y_diff / scalar
    if x_diff < 0:  # flip arrows moving to the left
        arrow.flip()
    arrows.append((arrow, direction))


# skeleton arrow creation
def enemy_fire(enemy):
    if enemy == boss:
        arrow = gamebox.from_image(enemy.x, enemy.y, 'PhantonBlast.png')
    else:
        arrow = gamebox.from_image(enemy.x, enemy.y, 'Arrow.png')
    arrow_speed = 10
    x_diff = character.x - enemy.x
    y_diff = character.y - enemy.y
    scalar = math.sqrt(x_diff**2 + y_diff**2) // arrow_speed  # ensures that all arrows travel same speed
    direction = x_diff/scalar, y_diff/scalar
    if x_diff < 0:  # flip enemies moving to the left
        arrow.flip()
    if enemy == boss:
        boss_arrows.append((arrow, direction))
    else:
        skeleton_arrows.append((arrow, direction))


# arrow animation and deletion. also handles skeleton arrows
def moving_arrows(arrow_list):
    for index, (sharp, (x_coord, y_coord)) in enumerate(arrow_list):
        sharp.speedx = x_coord
        sharp.speedy = y_coord
        sharp.move_speed()
        camera.draw(sharp)
        if sharp.x > camera.right or sharp.x < camera.left or sharp.y > camera.bottom or sharp.y < camera.top:
            del arrow_list[index]


# when you bump into an enemy (and aren't attacking), you each get knocked back equal amounts. Utilizes fact that
# object.x and object.y coordinates are from center of object, meaning that there is always a difference between the
# centers as long as each object has dimensions. Also, bigger objects are knocked back farther. Simple, but works nicely
def rebound(good, bad, attacking):
    good.move_to_stop_overlapping(bad)
    # diff cut in half for more reasonable rebound
    x_diff = (good.x - bad.x)/2
    y_diff = (good.y - bad.y)/2
    # char only bounces back if you're not attacking
    if not attacking:
        good.x += x_diff
        good.y += y_diff
    bad.x -= x_diff
    bad.y -= y_diff
    # makes sure both chars stay in play
    [less_rebound(i) for i in (good, bad)]


# sometimes the rebound is too much... This keeps you in play
def less_rebound(char):
    if char.y > camera.bottom:
        char.y = camera.bottom + 50
    if char.y < camera.top:
        char.y = camera.top - 50
    if char.x < camera.left:
        char.x = camera.left + 50
    if char.x > camera.right:
        char.x = camera.right - 50


# occasionally generates hearts when an enemy dies. Also, updates kill_count
def dead_enemy(bad):
    global kill_count
    if kill_count < 5:  # kill_count bar can only be filled to 5
        kill_count += 1
    maybe = random.randrange(100)
    if maybe > 75:
        new_life = gamebox.from_image(bad.x, bad.y, 'Heart.png')
        life.append(new_life)


# defines what happens when you take damage
def take_damage(damage, health):
    if health >= damage:
        health -= damage
    else:
        health = 0
    return health


# moving between rooms
def room_movement():
    global room
    if character.touches(door_t) and doors[2][1]:
        character.y = 475
        room = (room + 1) % 3  # if there is a top door, this will work to get you into the room you need
    if character.touches(door_b) and doors[3][1]:
        character.y = 125
        if room == 0:  # couldn't find a clever function for this one. Just straight assignment
            room = 2
        if room == 1:
            room = 0
    if character.touches(door_r) and doors[1][1]:
        character.x = 125
        room = 3
    if character.touches(door_l) and doors[0][1]:
        character.x = 700
        room = 0


# setup doors for each level depending on what room you're in
def room_setup():
    global boss_appear
    if room == 0:  # room 0 no left
        boss_appear = False
        room_setup_helper((door_r, door_t, door_b))
    if room == 1:  # room 1 only bottom
        boss_appear = False
        room_setup_helper([door_b])       # 1
    if room == 2:  # room 2 only top      0 3
        boss_appear = False
        room_setup_helper([door_t])       # 2
    if room == 3:  # room 3 left
        room_setup_helper([door_l])
        if not dead_boss:
            boss_appear = True
            camera.draw(boss)
            boss_health_bar = gamebox.from_image(575, 50, boss_health_sheet[5 - int(boss_health / 20)])
            boss_health_bar.height = 20
            camera.draw(boss_health_bar)
        if dead_enemies and dead_boss:
            camera.draw(ladder)


# sets 'there' attribute of doors to False if not supposed to be there. Draws the ones that are
def room_setup_helper(allowed):
    for index, (door, there, sheet_num) in enumerate(doors):
        if door in allowed:
            doors[index][1] = True
            if near_door(door):
                door.image = door_sheet[sheet_num + 1]
            else:
                door.image = door_sheet[sheet_num]
            camera.draw(door)
        else:
            doors[index][1] = False


# return True if character is near a door. This will open the door
def near_door(door):
    x_diff = character.x - door.x
    y_diff = character.y - door.y
    scalar = math.sqrt(x_diff**2 + y_diff**2)  # distance door is from char
    if scalar <= 150:
        return True
    else:
        return False


# sets random x coordinate of an enemy
def random_x_coord():
    return random.randrange(250, 700)


# sets random y coordinate of an enemy
def random_y_coord():
    return random.randrange(250, 400)


# creating enemies. Includes append to respective rooms
def create_enemy(species, room_num):
    if species == 'slime':
        new = gamebox.from_image(random_x_coord(), random_y_coord(), 'Slime_WIP.png')
        sprinting.append(None)
    elif species == 'skeleton':
        new = gamebox.from_image(random_x_coord(), random_y_coord(), 'Skelly WIP.png')
        sprinting.append(None)
    elif species == 'zombie':
        new = gamebox.from_image(random_x_coord(), random_y_coord(), 'Zombie WIP.png')
        sprinting.append(0)
    else:
        print("not a valid enemy type")
    new.height = 60
    if room_num == 0:
        room_0_enemies.append([new, True, species])
    elif room_num == 1:
        room_1_enemies.append([new, True, species])
    elif room_num == 2:
        room_2_enemies.append([new, True, species])
    elif room_num == 3:
        room_3_enemies.append([new, True, species])
    else:
        print("not a valid room number")


# shows game over screen when you die. Then, sets game_over to False
def end_game():
    global level, game_over
    level = -2
    camera.draw(gamebox.from_image(400, 300, 'GameOver.png'))
    game_over = False
    if camera.mouseclick:
        gamebox.stop_loop()


def levels():
    global border, ladder, doors, door_r, door_t, door_l, door_b, background, level
    background = gamebox.from_image(400, 300, 'Rooms.png')
    background.height = 700
    outer_b = gamebox.from_color(400, 600, "black", 800, 25)
    outer_t = gamebox.from_color(400, 0, "black", 800, 25)
    outer_l = gamebox.from_color(0, 300, "black", 25, 600)
    outer_r = gamebox.from_color(800, 300, "black", 25, 600)
    border = [outer_b, outer_t, outer_l, outer_r]
    door_b = gamebox.from_image(400, 560, door_sheet[4])
    door_t = gamebox.from_image(400, 40, door_sheet[0])
    door_l = gamebox.from_image(40, 300, door_sheet[2])
    door_r = gamebox.from_image(760, 300, door_sheet[6])
    doors = [[door_l, True, 2], [door_r, True, 6], [door_t, True, 0], [door_b, True, 4]]
    ladder = gamebox.from_image(775, 300, 'Ladder.png')

    enemies = []  # list of enemies...
    room_0_enemies = []  # and lists of enemies in each room
    room_1_enemies = []
    room_2_enemies = []
    room_3_enemies = []
    global enemies, room_0_enemies, room_1_enemies, room_2_enemies, room_3_enemies
    character.x = 50
    character.y = 300

    # handling of enemies is really convoluted. There is a list of lists of lists
    # outer layer is a master list that contains lists for each level. [room0, room1, room2, room3]
    # each level contains a list with all the enemies on that level. [enemy1, enemy2, enemy3]
    # each enemy has its own list that has attributes of it. [enemy_object, alive?, type]
    if level == 1:
        for i in range(3):  # different species of enemy in rooms 0-2 of level 1
            for room_num, species in enumerate(('slime', 'zombie', 'skeleton')):
                create_enemy(species, room_num)
        for i in ('slime', 'zombie', 'skeleton'):  # one of each species in room 3 of level 1
            create_enemy(i, 3)
    if level == 2:
        for i in range(3):
            create_enemy('slime', 0)
            create_enemy('zombie', 0)
        for i in range(6):
            create_enemy('skeleton', 1)
        for i in range(3):
            create_enemy('skeleton', 2)
            create_enemy('zombie', 2)
            create_enemy('slime', 2)
        for i in range(5):
            create_enemy('slime', 3)
            create_enemy('zombie', 3)
            if i <= 2:
                create_enemy('skeleton', 3)

    # create list with enemies from all rooms
    enemies.append(room_0_enemies)
    enemies.append(room_1_enemies)
    enemies.append(room_2_enemies)
    enemies.append(room_3_enemies)

    boss_health = 100
    if level == 1:
        boss = boss_slime
    if level == 2:
        boss = boss_phantom
    dead_boss = False  # can only go to next level if boss is killed
    global boss, boss_health, dead_boss

    gamebox.timer_loop(ticks_per_second, tick)
    del enemies
    level += 1


'''SEQUENTIAL CODE STARTS HERE'''
camera = gamebox.Camera(800, 600)

# setting the initial variables. Some are declared in while loop -> level == 0 below. These reset every game
ticks_per_second = 30
level = -1  # start at level -1, the home page
frames = 0  # keeps track of number of frames shown. Used for character walking
half_frames = 0  # frames move too fast. This increments frames at half the rate
attack_cooldown = 0  # time period before you can attack again
attack_burst = 20  # can attack for at most 2/3 of a second
sprinting = []  # for zombie sprinting counts
ability_burst = 60  # ability can be used for 2 seconds at a time
knight_image_file = 'Knight.png'  # file the knight sprite sheet is loaded from
ranger_image_file = 'Ranger.png'  # file the ranger sprite sheet is loaded from
ranger_ability_file = 'Stealth.png'  # file for the ranger sprite sheet while abilities activated
knight_ability_file = 'Knight_ability.png'  # file for the knight sprite sheet while abilities activated
door_sheet = gamebox.load_sprite_sheet('Doors.png', 2, 4)
char_health_sheet = gamebox.load_sprite_sheet('Hero_Health.png', 6, 1)
ability_bar_sheet = gamebox.load_sprite_sheet('Skill_Bar.png', 6, 1)
boss_slime = gamebox.from_image(450, 300, 'Boss Slime.png')
boss_phantom = gamebox.from_image(600, 200, 'ThePhantomBoss.png')
boss_health_sheet = gamebox.load_sprite_sheet('Boss_Health.png', 6, 1)
char_speed = 5  # speed of the character, number of pixels moved per frame
level_screen = True
game_over = False
boss_spree = 0
boss_sprint = 15
walk_time = 0

while True:
    # home screen
    if level == -1:
        start = gamebox.from_color(420, 350, "red", 320, 160)
        home_screen()
        level += 1
    # char selection screen
    if level == 0:
        select_screen = gamebox.from_image(400, 300, 'Character_Selection.png')
        select_screen.height = 600
        knight_sheet = gamebox.load_sprite_sheet(knight_image_file, 2, 4)
        knight_ability_sheet = gamebox.load_sprite_sheet(knight_ability_file, 2, 4)
        knight = gamebox.from_image(600, 380, knight_sheet[0])
        knight.height = 220
        ranger_sheet = gamebox.load_sprite_sheet(ranger_image_file, 2, 4)
        ranger_ability_sheet = gamebox.load_sprite_sheet(ranger_ability_file, 2, 4)
        ranger = gamebox.from_image(225, 380, ranger_sheet[0])
        ranger.height = 220
        char_select()
        character.height = 60
        if character == ranger:
            char_health = 100  # you start off healthy. Lucky you
        if character == knight:
            char_health = 200  # it's way harder to play as the knight. You get extra health
        room = 0  # keeps track of which room you're in
        kill_count = 0  # for abilities bar. Maximum of 5. Using ability decreases by 3
        life = []  # list of hearts generated from dead enemies
        arrows = []  # list of all ranger arrows. Are deleted as they move off the screen
        skeleton_arrows = []  # list of all skeleton arrows. Again, deleted as they move off the screen
        boss_arrows = []
        dead_enemies = False  # ladder doesn't appear until all enemies killed (and boss is killed. Handled elsewhere)
        boss_appear = False  # boss only appears in room 3
        flipped = True  # is the char flipped?
        level += 1

    # setup for all levels of actual gameplay
    while 0 < level <= 2:
        levels()

    if level == 3:
        camera.clear("black")
        gamebox.timer_loop(ticks_per_second, tick)
        level = -1
    else:  # throws an error that stops the game. Hit F1 to get here
        pygame.quit()
        gamebox.stop_loop()
