import time
import threading
import keyboard
import os
import random

from rich.console import Console
from rich.text import Text
from rich.live import Live

class Maze():
    def __init__(self, weight, height, start_speed, ground_color="#006400"):
        self.weight = weight
        self.height = height
        self.speed = start_speed
        self.ground_color = ground_color
        self.create_maze()

    def create_maze(self):
        self.maze = []
        for i in range(self.height - 1):
            self.maze.append([(' ', None)] * self.weight)
        self.maze.append([('‾', self.ground_color)] * self.weight)

    def edit_maze(self, x, y, last_x=None, last_y=None, icon=' ', color=None):
        if last_x is not None and last_y is not None:
            if last_y == self.height - 1:
                self.maze[last_y][last_x] = ('‾', self.ground_color)
            else:
                self.maze[last_y][last_x] = (' ', None)
        
        if 0 <= y < self.height and 0 <= x < self.weight:
            self.maze[y][x] = (icon, color)

    def get_block_data(self, x, y):
        if 0 <= x < self.weight and 0 <= y < self.height:
            return self.maze[y][x][0]
        return None

    def get_renderable(self):
        text = Text()
        for row in self.maze:
            for char, style in row:
                if style:
                    text.append(char, style=style)
                else:
                    text.append(char)
            text.append('\n')
        return text

class Player():
    def __init__(self, x, size, maze: Maze, icon='@', color="bold #FFD700"):
        self.x = x
        self.y = maze.height - 2
        self.size = size
        self.icon = icon
        self.color = color
        self.coord_list = []
        self.jump_height = 4

        self._move_direction = 0
        self._is_moving = False
        self._is_jumping = False
        self._jump_phase = 0
        self._jump_save = 0

        self.maze = maze
        self._create_player()

    def _create_player(self):
        for i in range(-self.size, self.size+1): 
            self.maze.edit_maze(self.x+i, y=self.y, icon=self.icon, color=self.color)
            self.coord_list.append(self.x+i)

    def start_mr(self):
        self._is_moving = True
        self._move_direction = 1
    def stop_mr(self):
        if self._move_direction == 1:
            self._is_moving = False
            self._move_direction = 0
    def start_ml(self):
        self._is_moving = True
        self._move_direction = -1
    def stop_ml(self):
        if self._move_direction == -1:
            self._is_moving = False
            self._move_direction = 0

    def start_jump(self):
        self._is_jumping = True
        self._jump_save = 2
    def stop_jump(self):
        self._is_jumping = False

    def move(self):
        if self._is_moving == True and self.x+self._move_direction != -1 and self.x+self._move_direction != self.maze.weight:
            self.maze.edit_maze(x=self.x+self._move_direction, last_x=self.x, y=self.y, last_y=self.y, icon=self.icon, color=self.color)
            self.x += self._move_direction

            self.coord_list = [self.x]
        self.jump()

    def jump(self):
        is_ground = (self.maze.get_block_data(self.x, self.y + 1) == '‾')

        if (self._is_jumping and is_ground) or self._jump_phase > 0:
            if self._jump_phase < self.jump_height and self.maze.get_block_data(self.x, self.y - 1) == ' ':
                self.maze.edit_maze(x=self.x, last_x=self.x, y=self.y - 1, last_y=self.y, icon=self.icon, color=self.color)
                self.y -= 1
                self._jump_phase += 1
            else:
                self._jump_phase = 0
                self._is_jumping = False
        elif not is_ground:
            self.maze.edit_maze(x=self.x, last_x=self.x, y=self.y + 1, last_y=self.y, icon=self.icon, color=self.color)
            self.y += 1
            self._jump_phase = 0
        
        if self._jump_save > 0:
            self._jump_save -= 1
        else:
            self._is_jumping = False


# class Gizmo():
#     def __init__(self, num, default_speed, maze: Maze):
#         self.num = num
#         self.speed = default_speed
#         self.maze = maze
#         self.meteors = []

#     def _spawn_gizmo(self):
#         for now in range(self.num):
#             ...

def game_loop(player: Player, maze: Maze):
    with Live(maze.get_renderable(), screen=True, transient=True, refresh_per_second=60) as live:
        while True:
            player.move()
            
            live.update(maze.get_renderable())

            time.sleep(maze.speed)

def main():
    height = 41
    weight = 80 
    os.system(f"mode con: cols={weight} lines={height}")


    maze = Maze(weight, height-1, 0.06, ground_color="#228B22")
    player = Player(weight//2, 0, maze, color="bold yellow")
    # gizmo = Gizmo(num=10, default_speed=0.8, maze=maze)

    keyboard.on_press_key('d', lambda e: player.start_mr())
    keyboard.on_release_key('d', lambda e: player.stop_mr())

    keyboard.on_press_key('a', lambda e: player.start_ml())
    keyboard.on_release_key('a', lambda e: player.stop_ml())

    keyboard.on_press_key('w', lambda e: player.start_jump())
    keyboard.on_release_key('w', lambda e: player.stop_jump())
    keyboard.on_press_key('space', lambda e: player.start_jump())
    keyboard.on_release_key('space', lambda e: player.stop_jump())

    thread = threading.Thread(target=game_loop, args=(player, maze), daemon=True)
    thread.start()

    while True:
        time.sleep(maze.speed)

if __name__ == '__main__':
    main()
