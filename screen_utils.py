import curses
import textwrap
import math

def draw_layout(stdscr, dungeon, player_pos, content2, content3, player):
    if not hasattr(draw_layout, 'colors_initialized'):
        curses.start_color()
        curses.init_pair(1, curses.COLOR_CYAN, curses.COLOR_BLACK)
        draw_layout.colors_initialized = True

    player_info = f"Name: {player.name}\nClass: {player.__class__.__name__}\nHealth: {player.health}\n"
    player_info += "Weapon: Bow" if player.can_use_ranged_weapon else "Weapon: Sword & Shield"
    content3 = player_info

    player_y, player_x = player_pos

    if not hasattr(draw_layout, 'visibility_map'):
        draw_layout.visibility_map = [[False for _ in range(len(dungeon[0]))] for _ in range(len(dungeon))]
    if not hasattr(draw_layout, 'last_seen_map'):
        draw_layout.last_seen_map = [[None for _ in range(len(dungeon[0]))] for _ in range(len(dungeon))]

    stdscr.clear()

    view_width = 70
    view_height = 16

    top = max(0, min(player_y - view_height // 2, len(dungeon) - view_height))
    left = max(0, min(player_x - view_width // 2, len(dungeon[0]) - view_width))

    height, width = stdscr.getmaxyx()
    vertical_divider = (width // 2) + 25
    horizontal_divider = (height // 2) + 6

    def display_wrapped_text(y_start, x_start, max_width, max_height, text):
        """Display wrapped text within the bounds of a section."""
        wrapped_lines = textwrap.wrap(text, max_width)
        for i, line in enumerate(wrapped_lines[:max_height]):
            stdscr.addstr(y_start + i, x_start, line)

    def is_visible(y, x):
        """Check if a tile is visible to the player."""
        distance = math.sqrt((y - player_y) ** 2 + (x - player_x) ** 2)
        if distance > 12:
            return False
        line = bresenham_line(player_y, player_x, y, x)
        for (ly, lx) in line:
            if dungeon[ly][lx] == '#':
                return (ly == y and lx == x)
        return True

    def bresenham_line(y0, x0, y1, x1):
        """Generate a line from (y0, x0) to (y1, x1) using Bresenham's algorithm."""
        line = []
        dx = abs(x1 - x0)
        dy = -abs(y1 - y0)
        sx = 1 if x0 < x1 else -1
        sy = 1 if y0 < y1 else -1
        err = dx + dy
        while True:
            line.append((y0, x0))
            if x0 == x1 and y0 == y1:
                break
            e2 = 2 * err
            if e2 >= dy:
                err += dy
                x0 += sx
            if e2 <= dx:
                err += dx
                y0 += sy
        return line

    for y in range(len(dungeon)):
        for x in range(len(dungeon[0])):
            if is_visible(y, x):
                draw_layout.visibility_map[y][x] = True
                draw_layout.last_seen_map[y][x] = dungeon[y][x]

    for y in range(view_height):
        for x in range(view_width):
            tile_y = top + y
            tile_x = left + x
            if 0 <= tile_y < len(dungeon) and 0 <= tile_x < len(dungeon[0]):
                if draw_layout.visibility_map[tile_y][tile_x]:
                    if is_visible(tile_y, tile_x):
                        tile = dungeon[tile_y][tile_x]
                        if tile in ["N", "F", "S"]:
                            stdscr.addch(y + 1, x + 1, tile)
                        elif tile_y == player_y and tile_x == player_x:
                            stdscr.addch(y + 1, x + 1, "@")
                        else:
                            stdscr.addch(y + 1, x + 1, tile)
                    else:
                        tile = draw_layout.last_seen_map[tile_y][tile_x]
                        if tile == '#':
                            for dy, dx in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
                                ny, nx = tile_y + dy, tile_x + dx
                                if 0 <= ny < len(dungeon) and 0 <= nx < len(dungeon[0]):
                                    if dungeon[ny][nx] in ['.', '@', 'N', 'F', 'S'] and draw_layout.visibility_map[ny][nx]:
                                        stdscr.addch(y + 1, x + 1, '#', curses.color_pair(1))
                                        break
                        else:
                            stdscr.addch(y + 1, x + 1, tile, curses.color_pair(1))
                else:
                    stdscr.addch(y + 1, x + 1, ' ')

    display_wrapped_text(horizontal_divider + 1, 1, vertical_divider - 2, height - horizontal_divider - 2, content2)

    display_wrapped_text(1, vertical_divider + 2, width - vertical_divider - 4, height - 2, content3)

    for y in range(height):
        stdscr.addch(y, vertical_divider, '|')
    for x in range(vertical_divider):
        stdscr.addch(horizontal_divider, x, '-')

    stdscr.refresh()