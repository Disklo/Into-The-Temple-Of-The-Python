import random

def BSP(DUNGEON_WIDTH, DUNGEON_HEIGHT, ROOM_DENSITY):
    class Room:
        def __init__(self, x, y, width, height):
            self.x = x
            self.y = y
            self.width = width
            self.height = height

        def center(self):
            """Return the center point of the room."""
            return (self.x + self.width // 2, self.y + self.height // 2)

        def intersects(self, other):
            """Check if this room intersects with another room."""
            return not (
                self.x + self.width < other.x or
                self.x > other.x + other.width or
                self.y + self.height < other.y or
                self.y > other.y + other.height
            )

    class Leaf:
        MIN_SIZE = 6

        def __init__(self, x, y, width, height):
            self.x = x
            self.y = y
            self.width = width
            self.height = height
            self.left_child = None
            self.right_child = None
            self.room = None

        def split(self):
            """Split the leaf into two children."""
            if self.left_child or self.right_child:
                return False

            split_horizontally = random.choice([True, False])

            if self.width > self.height and self.width / self.height >= 1.25:
                split_horizontally = False
            elif self.height > self.width and self.height / self.width >= 1.25:
                split_horizontally = True

            max_split = (self.height if split_horizontally else self.width) - Leaf.MIN_SIZE
            if max_split <= Leaf.MIN_SIZE:
                return False

            split_point = random.randint(Leaf.MIN_SIZE, max_split)

            if split_horizontally:
                self.left_child = Leaf(self.x, self.y, self.width, split_point)
                self.right_child = Leaf(self.x, self.y + split_point, self.width, self.height - split_point)
            else:
                self.left_child = Leaf(self.x, self.y, split_point, self.height)
                self.right_child = Leaf(self.x + split_point, self.y, self.width - split_point, self.height)

            return True

        def create_rooms(self):
            """Create rooms recursively in each leaf."""
            if self.left_child or self.right_child:
                if self.left_child:
                    self.left_child.create_rooms()
                if self.right_child:
                    self.right_child.create_rooms()
                room1 = self.left_child.get_closest_room() if self.left_child else None
                room2 = self.right_child.get_closest_room() if self.right_child else None
                self.create_hallway(room1, room2)
            else:
                if random.random() < ROOM_DENSITY:
                    room_width = random.randint(3, self.width - 2)
                    room_height = random.randint(3, self.height - 2)
                    room_x = random.randint(self.x + 1, self.x + self.width - room_width - 1)
                    room_y = random.randint(self.y + 1, self.y + self.height - room_height - 1)
                    self.room = Room(room_x, room_y, room_width, room_height)

        def create_hallway(self, room1, room2):
            """Create a hallway connecting two rooms if both exist."""
            if not room1 or not room2:
                return

            x1, y1 = room1.center()
            x2, y2 = room2.center()

            if random.choice([True, False]):
                self.create_h_corridor(x1, x2, y1)
                self.create_v_corridor(y1, y2, x2)
            else:
                self.create_v_corridor(y1, y2, x1)
                self.create_h_corridor(x1, x2, y2)

        def get_closest_room(self):
            """Find the closest room recursively in this subtree."""
            if self.room:
                return self.room
            rooms = []
            if self.left_child:
                left_room = self.left_child.get_closest_room()
                if left_room:
                    rooms.append(left_room)
            if self.right_child:
                right_room = self.right_child.get_closest_room()
                if right_room:
                    rooms.append(right_room)
            return min(rooms, key=lambda r: (r.x + r.y)) if rooms else None

        def create_h_corridor(self, x1, x2, y):
            for x in range(min(x1, x2), max(x1, x2) + 1):
                dungeon[y][x] = '.'

        def create_v_corridor(self, y1, y2, x):
            for y in range(min(y1, y2), max(y1, y2) + 1):
                dungeon[y][x] = '.'

        def get_room(self):
            """Get a room from this leaf or its children."""
            if self.room:
                return self.room
            elif self.left_child:
                return self.left_child.get_room()
            elif self.right_child:
                return self.right_child.get_room()
            return None

    dungeon = [['#' for _ in range(DUNGEON_WIDTH)] for _ in range(DUNGEON_HEIGHT)]

    root_leaf = Leaf(0, 0, DUNGEON_WIDTH, DUNGEON_HEIGHT)
    leaves = [root_leaf]

    split_successful = True
    while split_successful:
        split_successful = False
        for leaf in leaves[:]:
            if not leaf.left_child and not leaf.right_child:
                if leaf.split():
                    leaves.append(leaf.left_child)
                    leaves.append(leaf.right_child)
                    split_successful = True

    root_leaf.create_rooms()

    for leaf in leaves:
        if leaf.room:
            for y in range(leaf.room.y, leaf.room.y + leaf.room.height):
                for x in range(leaf.room.x, leaf.room.x + leaf.room.width):
                    dungeon[y][x] = '.'

    return dungeon