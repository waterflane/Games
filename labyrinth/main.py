import random
from collections import deque

# helper functions and methods
def field_display(maze):
    for i in maze:
        print(''.join(i))
def check_state(pl_coord, enemy_coord, finish_coord):
    if pl_coord == enemy_coord: return -1
    if pl_coord == finish_coord: return 1

# -------------- Mob ------------------
class Mob():
    def __init__(self, coord: list, maze: list, symbol, effects: list):
        self.coord = coord
        self.maze = maze
        self.symbol = symbol
        self.now_x = coord[0]
        self.now_y = coord[1]
        self.effects = effects
# -------------- Bot ------------------
class Bot(Mob):
    def __init__(self, coord, maze, symbol, effects, range_of_view=3):
        super().__init__(coord, maze, symbol, effects)
        self.range_of_view = range_of_view

    def check_path(self, pl_coord):
        queue = deque([[self.coord, [0,0], self.range_of_view+2]])
        visited = [self.coord]

        while queue:
            now_coord, first_vect, views_left = queue.popleft()
            if now_coord == pl_coord: return True, first_vect
            if not views_left: break

            for dir in [[0,1], [0,-1], [1,0], [-1,0]]:
                new_coord = [now_coord[0]+dir[0], now_coord[1]+dir[1]]
                if first_vect != [0, 0]:
                    if self.maze[new_coord[1]][new_coord[0]] != '#' and new_coord not in visited:
                        queue.append([new_coord, first_vect, views_left-1])
                        visited.append(new_coord)
                else:
                    if self.maze[new_coord[1]][new_coord[0]] != '#' and new_coord not in visited:
                        queue.append([new_coord, dir, views_left-1])
                        visited.append(new_coord)
        return False, [0,0]
    
    def move(self, pl_coord):
        is_moved, vect = self.check_path(pl_coord)
        if is_moved and 'freeze' not in self.effects: 
            self.coord = edit_coord(self.coord, vect, self)
        elif 'freeze' in self.effects: 
            self.effects.remove('freeze')   
# -------------- Player ------------------
class Player(Mob):
    def __init__(self, coord, maze, symbol, effects):
        super().__init__(coord, maze, symbol, effects)
    # move player
    def __pl_input(self):
        actions = {
            'w': [0, -1],
            's': [0, 1],
            'a': [-1, 0],
            'd': [1, 0],
            'ц': [0, -1],
            'ы': [0, 1],
            'ф': [-1, 0],
            'в': [1, 0]
        }
        input_action = input()

        if input_action != '' and input_action in actions.keys():
            return actions[input_action]
        else: return []

    def move(self):
        vect = self.__pl_input()
        if vect and 'freeze' not in self.effects: 
            self.coord = edit_coord(self.coord, vect, self)
        elif 'freeze' in self.effects: 
            self.effects.remove('freeze')   

# -------------- Object ------------------
class Object():
    def __init__(self, maze, symbol: str, coords: list, effects: list):
        self.symbol = symbol
        self.maze = maze
        self.coords = coords
        self.effects = effects

    def check_effect(self, mob: Mob):
        if mob.coord in self.coords:
            self.coords.remove(mob.coord)
            return self.effects
        return []
        
    def accommodation(self, chance: int, ignore_list: list[list[int, int]] = []):
        for y in range(len(self.maze)):
            for x in range(len(self.maze[y])):
                if self.maze[y][x] == ' ' and [x,y] not in ignore_list:
                    if random.randint(1, chance) == 1:
                        self.maze[y][x] = self.symbol 
                        self.coords.append([x,y])

# Coordinate change function
def edit_coord(coord, vect, mob: Mob):
    new_coord = [coord[0]+vect[0], coord[1]+vect[1]] if mob.maze[coord[1]+vect[1]][coord[0]+vect[0]] != '#' else [coord[0], coord[1]]
  
    mob.maze[coord[1]][coord[0]] = ' '
    mob.maze[new_coord[1]][new_coord[0]] = mob.symbol
  
    return new_coord

# -------------- Creating and editing a map ------------------
def create_maze():
    maze = [
        list('#'*11),list('#'*11),list('#'*11),list('#'*11),list('#'*11),list('#'*11),list('#'*11),list('#'*11),list('#'*11),list('#'*11),list('#'*11)
    ]

    queue = deque()
    deque.append(queue, ([1,1], 1))
    deque.append(queue, ([9,9], 2))
    deque.append(queue, ([1,7], 0))
    first_visited = [[1,1]]

    maze[1][1] = ' '
    maze[9][9] = ' '
    maze[7][1] = ' '

    actions = {
        '1': [0, -1],
        '2': [0, 1],
        '3': [-1, 0],
        '4': [1, 0]
    }

    while queue:
        now_coord, priority = deque.popleft(queue)

        while True:
            now_action = random.randint(1,4)
            new_coord = [now_coord[0] + actions[str(now_action)][0], now_coord[1] + actions[str(now_action)][1]]
            if (new_coord[0] > 0 and new_coord[0] < 10) and (new_coord[1] > 0 and new_coord[1] < 10):
                break

        if new_coord in first_visited and priority == 2: 
            maze[new_coord[1]][new_coord[0]] = ' '
            break
        if priority == 1: first_visited.append(new_coord)

        maze[new_coord[1]][new_coord[0]] = ' '
        queue.append((new_coord, priority))

    maze[9][9] = '$'
    maze[7][1] = '%'
    maze[1][1] = '@'
    return maze

def main():
    maze = create_maze()

    player = Player([1, 1], maze, '@', [])
    bot = Bot([1, 7], maze, '%', [])
    finish_coord = [9, 9]

    spike = Object(maze, '0', [], ['freeze'])
    spike.accommodation(5)

    field_display(maze)
    while True:
        player.effects.extend(spike.check_effect(player))
        bot.effects.extend(spike.check_effect(bot))

        player.move()
        bot.move(player.coord)
        
        state = check_state(player.coord, bot.coord, finish_coord)
        field_display(maze)

        if state == -1: 
            print('False')
            break
        if state == 1: 
            print('Win!')
            break

if __name__ == "__main__":
    main()
