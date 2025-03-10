import curses
from bsp import BSP
from random import randint, choice
from screen_utils import draw_layout

DUNGEON_WIDTH = 280
DUNGEON_HEIGHT = 64
ROOM_DENSITY = 0.75

class NPC:
    def __init__(self, y, x, speed=2, detection_radius=8, symbol="N"):
        self.y = y
        self.x = x
        self.speed = speed
        self.detection_radius = detection_radius
        self.move_counter = 0
        self.symbol = symbol

    def is_near_player(self, player_pos):
        """Check if the player is within the detection radius."""
        player_y, player_x = player_pos
        return abs(self.y - player_y) + abs(self.x - player_x) <= self.detection_radius

    def get_next_move(self, dungeon, player_pos):
        """Determine the next move for the NPC."""
        possible_moves = []
        if self.is_near_player(player_pos):
            player_y, player_x = player_pos
            if self.y > player_y:
                possible_moves.append((self.y - 1, self.x))
            if self.y < player_y:
                possible_moves.append((self.y + 1, self.x))
            if self.x > player_x:
                possible_moves.append((self.y, self.x - 1))
            if self.x < player_x:
                possible_moves.append((self.y, self.x + 1))
        else:
            possible_moves = [(self.y + dy, self.x + dx) for dy, dx in [(-1, 0), (1, 0), (0, -1), (0, 1)]]
        valid_moves = [(y, x) for y, x in possible_moves if 0 <= y < DUNGEON_HEIGHT and 0 <= x < DUNGEON_WIDTH and dungeon[y][x] == "."]
        return choice(valid_moves) if valid_moves else (self.y, self.x)

    def move(self, dungeon, player_pos):
        """Move the NPC if the move counter matches the speed requirement."""
        self.move_counter += 1
        if self.move_counter >= self.speed:
            self.y, self.x = self.get_next_move(dungeon, player_pos)
            self.move_counter = 0


class FastNPC(NPC):
    def __init__(self, y, x):
        super().__init__(y, x, speed=1, detection_radius=12, symbol="F")

class SlowNPC(NPC):
    def __init__(self, y, x):
        super().__init__(y, x, speed=3, detection_radius=8, symbol="S")


class Player:
    def __init__(self, name, health, can_use_ranged_weapon, can_use_shield):
        self.name = name
        self.health = health
        self.can_use_ranged_weapon = can_use_ranged_weapon
        self.can_use_shield = can_use_shield

class Knight(Player):
    def __init__(self, name):
        super().__init__(name, health=100, can_use_ranged_weapon=False, can_use_shield=True)

class Ranger(Player):
    def __init__(self, name):
        super().__init__(name, health=80, can_use_ranged_weapon=True, can_use_shield=False)

def get_random_empty_tile(dungeon):
    empty_tiles = [(row, col) for row in range(DUNGEON_HEIGHT) for col in range(DUNGEON_WIDTH) if dungeon[row][col] == "."]
    return choice(empty_tiles)

def get_random_empty_tile_enemy(dungeon, player_pos):
    player_y, player_x = player_pos
    empty_tiles = [
        (row, col) for row in range(DUNGEON_HEIGHT) for col in range(DUNGEON_WIDTH)
        if dungeon[row][col] == "." and abs(row - player_y) > 10 and abs(col - player_x) > 10
    ]
    return choice(empty_tiles) if empty_tiles else get_random_empty_tile(dungeon)

def get_random_empty_tile_prop(dungeon, player_pos):
    player_y, player_x = player_pos
    empty_tiles = [
        (row, col) for row in range(DUNGEON_HEIGHT) for col in range(DUNGEON_WIDTH)
        if dungeon[row][col] == "." and abs(row - player_y) > 20 and abs(col - player_x) > 20
    ]
    return choice(empty_tiles) if empty_tiles else get_random_empty_tile(dungeon)

def choose_class(stdscr):
    stdscr.clear()
    stdscr.addstr(5, 10, "Choose your class:", curses.A_BOLD)
    stdscr.addstr(7, 12, "1 - Knight (Tanky, uses shields)")
    stdscr.addstr(8, 12, "2 - Ranger (Agile, uses ranged weapons)")
    
    stdscr.refresh()
    
    while True:
        key = stdscr.getch()
        if key == ord('1'):
            return "Knight"
        elif key == ord('2'):
            return "Ranger"

def get_player_name(stdscr):
    stdscr.clear()
    stdscr.addstr(5, 10, "Enter your name: ")
    stdscr.refresh()
    
    curses.echo()
    name = stdscr.getstr(6, 12, 20).decode("utf-8")
    curses.noecho()
    
    return name

def menu_screen(stdscr):
    stdscr.clear()
    height, width = stdscr.getmaxyx()
    
    title = "Into The Temple Of The Python"
    instruction = "S to start the game"
    
    stdscr.addstr(height // 2 - 1, (width - len(title)) // 2, title, curses.A_BOLD)
    stdscr.addstr(height // 2 + 1, (width - len(instruction)) // 2, instruction)
    
    stdscr.refresh()

    while True:
        key = stdscr.getch()
        if key == ord('s') or key == ord('S'):
            return


def game_loop(stdscr):
    menu_screen(stdscr)
    player_class = choose_class(stdscr)
    player_name = get_player_name(stdscr)
    if player_class == "Knight":
        player = Knight(player_name)
    else:
        player = Ranger(player_name)
    dungeon = BSP(DUNGEON_WIDTH, DUNGEON_HEIGHT, ROOM_DENSITY)
    player_y, player_x = get_random_empty_tile(dungeon)

    npcs = [
        NPC(*get_random_empty_tile_enemy(dungeon, (player_y, player_x))),
        FastNPC(*get_random_empty_tile_enemy(dungeon, (player_y, player_x))),
        SlowNPC(*get_random_empty_tile_enemy(dungeon, (player_y, player_x))),
        NPC(*get_random_empty_tile_enemy(dungeon, (player_y, player_x))),
        FastNPC(*get_random_empty_tile_enemy(dungeon, (player_y, player_x))),
        SlowNPC(*get_random_empty_tile_enemy(dungeon, (player_y, player_x))),
        NPC(*get_random_empty_tile_enemy(dungeon, (player_y, player_x))),
        FastNPC(*get_random_empty_tile_enemy(dungeon, (player_y, player_x))),
        SlowNPC(*get_random_empty_tile_enemy(dungeon, (player_y, player_x))),
        NPC(*get_random_empty_tile_enemy(dungeon, (player_y, player_x))),
        FastNPC(*get_random_empty_tile_enemy(dungeon, (player_y, player_x))),
        SlowNPC(*get_random_empty_tile_enemy(dungeon, (player_y, player_x)))
    ]

    curses.curs_set(0)
    stdscr.keypad(True)
    stdscr.nodelay(True)

    content2 = "Section 2: Long text test for footer section aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa"
    content3 = "Section 3: Side panel test text aaaaaaaaaaaaaaaaaaaaaaaaaaaaaa"

    in_combat = False
    enemy_in_combat = None

    while True:
        stdscr.clear()

        for npc in npcs:
            if npc.y == player_y and npc.x == player_x:
                in_combat = True
                enemy_in_combat = npc
                break
            else:
                in_combat = False
                enemy_in_combat = None

        if in_combat:
            dungeon_display = [[" " for _ in range(DUNGEON_WIDTH)] for _ in range(DUNGEON_HEIGHT)]
            dungeon_display[player_y][player_x] = enemy_in_combat.symbol
            content2 = "Press F to run"
        else:
            dungeon_display = [list(row) for row in dungeon]
            for npc in npcs:
                dungeon_display[npc.y][npc.x] = npc.symbol
            dungeon_display[player_y][player_x] = "@"
            content2 = "Section 2: Long text test for footer section aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa"

        dungeon_str = ["".join(row) for row in dungeon_display]
        draw_layout(stdscr, dungeon_str, (player_y, player_x), content2, content3, player)

        key = stdscr.getch()
        if key == ord('q'):
            break

        if in_combat and key == ord('f'):
            enemy_in_combat.y, enemy_in_combat.x = get_random_empty_tile_enemy(dungeon, (player_y, player_x))
            in_combat = False
            continue

        if in_combat:
            continue

        move_y, move_x = 0, 0
        if key == curses.KEY_UP:
            move_y = -1
        elif key == curses.KEY_DOWN:
            move_y = 1
        elif key == curses.KEY_LEFT:
            move_x = -1
        elif key == curses.KEY_RIGHT:
            move_x = 1

        if move_y == 0 and move_x == 0:
            continue

        new_y = player_y + move_y
        new_x = player_x + move_x
        if 0 <= new_y < DUNGEON_HEIGHT and 0 <= new_x < DUNGEON_WIDTH and dungeon[new_y][new_x] == ".":
            player_y, player_x = new_y, new_x

        for npc in npcs:
            npc.move(dungeon, (player_y, player_x))

curses.wrapper(game_loop)