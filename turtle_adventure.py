"""
The turtle_adventure module maintains all classes related to the Turtle's
adventure game.
"""
from turtle import RawTurtle
from gamelib import Game, GameElement
import math
import random


class TurtleGameElement(GameElement):
    """
    An abstract class representing all game elemnets related to the Turtle's
    Adventure game
    """

    def __init__(self, game: "TurtleAdventureGame"):
        super().__init__(game)
        self.__game: "TurtleAdventureGame" = game

    @property
    def game(self) -> "TurtleAdventureGame":
        """
        Get reference to the associated TurtleAnvengerGame instance
        """
        return self.__game


class Waypoint(TurtleGameElement):
    """
    Represent the waypoint to which the player will move.
    """

    def __init__(self, game: "TurtleAdventureGame"):
        super().__init__(game)
        self.__id1: int
        self.__id2: int
        self.__active: bool = False

    def create(self) -> None:
        self.__id1 = self.canvas.create_line(0, 0, 0, 0, width=2, fill="green")
        self.__id2 = self.canvas.create_line(0, 0, 0, 0, width=2, fill="green")

    def delete(self) -> None:
        self.canvas.delete(self.__id1)
        self.canvas.delete(self.__id2)

    def update(self) -> None:
        # there is nothing to update because a waypoint is fixed
        pass

    def render(self) -> None:
        if self.is_active:
            self.canvas.itemconfigure(self.__id1, state="normal")
            self.canvas.itemconfigure(self.__id2, state="normal")
            self.canvas.tag_raise(self.__id1)
            self.canvas.tag_raise(self.__id2)
            self.canvas.coords(self.__id1, self.x-10, self.y-10, self.x+10, self.y+10)
            self.canvas.coords(self.__id2, self.x-10, self.y+10, self.x+10, self.y-10)
        else:
            self.canvas.itemconfigure(self.__id1, state="hidden")
            self.canvas.itemconfigure(self.__id2, state="hidden")

    def activate(self, x: float, y: float) -> None:
        """
        Activate this waypoint with the specified location.
        """
        self.__active = True
        self.x = x
        self.y = y

    def deactivate(self) -> None:
        """
        Mark this waypoint as inactive.
        """
        self.__active = False

    @property
    def is_active(self) -> bool:
        """
        Get the flag indicating whether this waypoint is active.
        """
        return self.__active


class Home(TurtleGameElement):
    """
    Represent the player's home.
    """

    def __init__(self, game: "TurtleAdventureGame", pos: tuple[int, int], size: int):
        super().__init__(game)
        self.__id: int
        self.__size: int = size
        x, y = pos
        self.x = x
        self.y = y

    @property
    def size(self) -> int:
        """
        Get or set the size of Home
        """
        return self.__size

    @size.setter
    def size(self, val: int) -> None:
        self.__size = val

    def create(self) -> None:
        self.__id = self.canvas.create_rectangle(0, 0, 0, 0, outline="brown", width=2)

    def delete(self) -> None:
        self.canvas.delete(self.__id)

    def update(self) -> None:
        # there is nothing to update, unless home is allowed to moved
        pass

    def render(self) -> None:
        self.canvas.coords(self.__id,
                           self.x - self.size/2,
                           self.y - self.size/2,
                           self.x + self.size/2,
                           self.y + self.size/2)

    def contains(self, x: float, y: float):
        """
        Check whether home contains the point (x, y).
        """
        x1, x2 = self.x-self.size/2, self.x+self.size/2
        y1, y2 = self.y-self.size/2, self.y+self.size/2
        return x1 <= x <= x2 and y1 <= y <= y2


class Player(TurtleGameElement):
    """
    Represent the main player, implemented using Python's turtle.
    """

    def __init__(self,
                 game: "TurtleAdventureGame",
                 turtle: RawTurtle,
                 speed: float = 5):
        super().__init__(game)
        self.__speed: float = speed
        self.__turtle: RawTurtle = turtle

    def create(self) -> None:
        turtle = RawTurtle(self.canvas)
        turtle.getscreen().tracer(False) # disable turtle's built-in animation
        turtle.shape("turtle")
        turtle.color("green")
        turtle.penup()

        self.__turtle = turtle

    @property
    def speed(self) -> float:
        """
        Give the player's current speed.
        """
        return self.__speed

    @speed.setter
    def speed(self, val: float) -> None:
        self.__speed = val

    def delete(self) -> None:
        pass

    def update(self) -> None:
        # check if player has arrived home
        if self.game.home.contains(self.x, self.y):
            self.game.game_over_win()
        turtle = self.__turtle
        waypoint = self.game.waypoint
        if self.game.waypoint.is_active:
            turtle.setheading(turtle.towards(waypoint.x, waypoint.y))
            turtle.forward(self.speed)
            if turtle.distance(waypoint.x, waypoint.y) < self.speed:
                waypoint.deactivate()

    def render(self) -> None:
        self.__turtle.goto(self.x, self.y)
        self.__turtle.getscreen().update()

    # override original property x's getter/setter to use turtle's methods
    # instead
    @property
    def x(self) -> float:
        return self.__turtle.xcor()

    @x.setter
    def x(self, val: float) -> None:
        self.__turtle.setx(val)

    # override original property y's getter/setter to use turtle's methods
    # instead
    @property
    def y(self) -> float:
        return self.__turtle.ycor()

    @y.setter
    def y(self, val: float) -> None:
        self.__turtle.sety(val)


class Enemy(TurtleGameElement):
    """
    Define an abstract enemy for the Turtle's adventure game
    """

    def __init__(self,
                 game: "TurtleAdventureGame",
                 size: float,
                 color: str):
        super().__init__(game)
        self.__size = size
        self.__color = color

    @property
    def size(self) -> float:
        """
        Get the size of the enemy
        """
        return self.__size

    @property
    def color(self) -> str:
        """
        Get the color of the enemy
        """
        return self.__color

    def hits_player(self):
        """
        Check whether the enemy is hitting the player
        """
        return (
            (self.x - self.size/2 <= self.game.player.x <= self.x + self.size/2)
            and
            (self.y - self.size/2 <= self.game.player.y <= self.y + self.size/2)
        ) or (
            (self.game.player.x-7 <= self.x <= self.game.player.x+7)
            and
            (self.game.player.y-7 <= self.y <= self.game.player.y+7)
        )


class RandomMovingEnemy(Enemy):
    def __init__(self,
                 game: "TurtleAdventureGame",
                 size: float,
                 color: str = "#7e7e7e"):
        super().__init__(game, size, color)

    def create(self) -> None:
        self.__id = self.canvas.create_oval(0, 0, 0, 0, fill=self.color)

    def update(self) -> None:
        if self.x <= 0:
            self.x += random.randrange(0, 15)
        elif self.x >= self.game.winfo_width():
            self.x += random.randrange(-15, 0)
        else:
            self.x += random.randrange(-15, 15)
        if self.y <= 0:
            self.y += random.randrange(0, 15)
        elif self.y >= self.game.winfo_height():
            self.y += random.randrange(-15, 0)
        else:
            self.y += random.randrange(-15, 15)
        if self.hits_player():
            self.game.game_over_lose()

    def render(self) -> None:
        self.canvas.coords(self.__id,
                           self.x - self.size / 2,
                           self.y - self.size / 2,
                           self.x + self.size / 2,
                           self.y + self.size / 2)

    def delete(self) -> None:
        pass


class BouncingEnemy(Enemy):
    def __init__(self,
                 game: "TurtleAdventureGame",
                 size: float,
                 color: str = "#a72afe",
                 xspeed: float = 5,
                 yspeed: float = 5):
        super().__init__(game, size, color)
        self.__xspeed = xspeed
        self.__yspeed = yspeed
        self.__xstate = self.moving_right
        self.__ystate = self.moving_down

    def moving_down(self):
        self.y += self.__yspeed
        if self.y >= self.canvas.winfo_height():
            self.__ystate = self.moving_up

    def moving_up(self):
        self.y -= self.__yspeed
        if self.y <= 0:
            self.__ystate = self.moving_down

    def moving_right(self):
        self.x += self.__xspeed
        if self.x >= self.canvas.winfo_width():
            self.__xstate = self.moving_left

    def moving_left(self):
        self.x -= self.__xspeed
        if self.x <= 0:
            self.__xstate = self.moving_right

    def create(self) -> None:
        self.__id = self.canvas.create_oval(0, 0, 0, 0, fill=self.color)

    def update(self) -> None:
        self.__xstate()
        self.__ystate()
        if self.hits_player():
            self.game.game_over_lose()

    def render(self) -> None:
        self.canvas.coords(self.__id,
                           self.x - self.size / 2,
                           self.y - self.size / 2,
                           self.x + self.size / 2,
                           self.y + self.size / 2)

    def delete(self) -> None:
        pass


class HomingEnemy(Enemy):
    def __init__(self,
                 game: "TurtleAdventureGame",
                 size: float,
                 color: str = "#42ffbf",
                 speed: float = 3.8):
        super().__init__(game, size, color)
        self.__speed = speed
        if self.game.player.x <= self.x:
            self.__xstate = self.moving_left
        elif self.game.player.x >= self.x:
            self.__xstate = self.moving_right
        if self.game.player.y <= self.y:
            self.__ystate = self.moving_up
        elif self.game.player.y >= self.y:
            self.__ystate = self.moving_down

    def moving_right(self):
        if self.game.player.x - self.x == 0:
            self.x += 0
        else:
            self.x += self.__speed * math.cos(
                math.atan(abs(self.game.player.y - self.y) / abs(self.game.player.x - self.x)))
        if self.game.player.x <= self.x:
            self.__xstate = self.moving_left

    def moving_left(self):
        if self.game.player.x - self.x == 0:
            self.x += 0
        else:
            self.x -= self.__speed * math.cos(
                math.atan(abs(self.game.player.y - self.y) / abs(self.game.player.x - self.x)))
        if self.game.player.x >= self.x:
            self.__xstate = self.moving_right

    def moving_down(self):
        if self.game.player.x - self.x == 0:
            self.y += self.__speed
        else:
            self.y += self.__speed * math.sin(
                math.atan(abs(self.game.player.y - self.y) / abs(self.game.player.x - self.x)))
        if self.game.player.y <= self.y:
            self.__ystate = self.moving_up

    def moving_up(self):
        if self.game.player.x - self.x == 0:
            self.y -= self.__speed
        else:
            self.y -= self.__speed * math.sin(
                math.atan(abs(self.game.player.y - self.y) / abs(self.game.player.x - self.x)))
        if self.game.player.y >= self.y:
            self.__ystate = self.moving_down

    def create(self) -> None:
        self.__id = self.canvas.create_oval(0, 0, 0, 0, fill=self.color)

    def update(self) -> None:
        self.__xstate()
        self.__ystate()
        if self.hits_player():
            self.game.game_over_lose()

    def render(self) -> None:
        self.canvas.coords(self.__id,
                           self.x - self.size / 2,
                           self.y - self.size / 2,
                           self.x + self.size / 2,
                           self.y + self.size / 2)

    def delete(self) -> None:
        pass


class CampingEnemy(Enemy):
    def __init__(self,
                 game: "TurtleAdventureGame",
                 size: float,
                 color: str = "#ff0000",
                 speed: float = random.randrange(3, 5)):
        super().__init__(game, size, color)
        self.__speed = speed
        self.__state = self.moving_right
        self.__multiplier = (self.game.home.size/2)*5

    @property
    def multiplier(self):
        return self.__multiplier

    def moving_right(self):
        self.x += self.__speed
        if self.x >= self.game.home.x + self.__multiplier:
            self.x = self.game.home.x + self.__multiplier
            self.y = self.game.home.y - self.__multiplier
            self.__state = self.moving_down

    def moving_left(self):
        self.x -= self.__speed
        if self.x <= self.game.home.x - self.__multiplier:
            self.x = self.game.home.x - self.__multiplier
            self.y = self.game.home.y + self.__multiplier
            self.__state = self.moving_up

    def moving_down(self):
        self.y += self.__speed
        if self.y >= self.game.home.y + self.__multiplier:
            self.x = self.game.home.x + self.__multiplier
            self.y = self.game.home.y + self.__multiplier
            self.__state = self.moving_left

    def moving_up(self):
        self.y -= self.__speed
        if self.y <= self.game.home.y - self.__multiplier:
            self.x = self.game.home.x - self.__multiplier
            self.y = self.game.home.y - self.__multiplier
            self.__state = self.moving_right

    def create(self) -> None:
        self.__id = self.canvas.create_oval(0, 0, 0, 0, fill=self.color)

    def update(self) -> None:
        self.__state()
        if self.hits_player():
            self.game.game_over_lose()

    def render(self) -> None:
        self.canvas.coords(self.__id,
                           self.x - self.size / 2,
                           self.y - self.size / 2,
                           self.x + self.size / 2,
                           self.y + self.size / 2)

    def delete(self) -> None:
        pass


class Bullet(Enemy):
    def __init__(self,
                 game: "TurtleAdventureGame",
                 size: float,
                 color: str,
                 speed: float,
                 coordinate: tuple):
        super().__init__(game, size, color)
        if self.game.player.x - coordinate[0] == 0:
            self.__yspeed = speed
            self.__xspeed = 0
        else:
            self.__yspeed = speed * math.sin(
                math.atan(abs(self.game.player.y - coordinate[1]) /
                          abs(self.game.player.x - coordinate[0])))
            self.__xspeed = speed * math.cos(
                math.atan(abs(self.game.player.y - coordinate[1]) /
                          abs(self.game.player.x - coordinate[0])))
        if coordinate[0] >= self.game.player.x:
            self.__xspeed = -self.__xspeed
        else:
            self.__xspeed = self.__xspeed
        if coordinate[1] >= self.game.player.y:
            self.__yspeed = -self.__yspeed
        else:
            self.__yspeed = self.__yspeed

    def create(self) -> None:
        self.__id = self.canvas.create_oval(0, 0, 0, 0, fill=self.color)

    def hits_border(self):
        return (self.x <= 0) or (self.x >= self.game.winfo_width()) or \
            (self.y <= 0) or (self.y >= self.game.winfo_height())

    def update(self) -> None:
        for _ in range(10):
            self.x += self.__xspeed / 10
            self.y += self.__yspeed / 10
            if self.hits_player():
                self.game.game_over_lose()
        if self.hits_border():
            self.game.delete_element(self)

    def render(self) -> None:
        self.canvas.coords(self.__id,
                           self.x - self.size / 2,
                           self.y - self.size / 2,
                           self.x + self.size / 2,
                           self.y + self.size / 2)

    def delete(self) -> None:
        self.canvas.delete(self.__id)


class Turret(Enemy):
    def __init__(self,
                 game: "TurtleAdventureGame",
                 size: float,
                 color: str = "#ff8929",
                 bullet_size: float = 5,
                 velocity: float = 18,
                 fire_rate: float = 1.3):
        super().__init__(game, size, color)
        self.__bullet_size = bullet_size
        self.__velocity = velocity
        self.__fire_rate = (1/fire_rate)*1000
        self.__timer = 0

    def shoot(self):
        self.__timer += 33
        if self.__timer >= self.__fire_rate:
            bullet = Bullet(self.game, self.__bullet_size, self.color, self.__velocity, (self.x, self.y))
            bullet.x = self.x
            bullet.y = self.y
            self.game.add_element(bullet)
            self.__timer = 0

    def create(self) -> None:
        self.__id = self.canvas.create_oval(0, 0, 0, 0, fill=self.color)

    def update(self) -> None:
        self.shoot()
        if self.hits_player():
            self.game.game_over_lose()

    def render(self) -> None:
        self.canvas.coords(self.__id,
                           self.x - self.size / 2,
                           self.y - self.size / 2,
                           self.x + self.size / 2,
                           self.y + self.size / 2)

    def delete(self) -> None:
        pass


class EnemyGenerator:
    """
    An EnemyGenerator instance is responsible for creating enemies of various
    kinds and scheduling them to appear at certain points in time.
    """

    def __init__(self, game: "TurtleAdventureGame", level: int):
        self.__game: TurtleAdventureGame = game
        self.__level: int = level

        # example
        self.__enemies = [RandomMovingEnemy,
                          HomingEnemy,
                          CampingEnemy,
                          BouncingEnemy,
                          Turret]
        self.initial_enemies()
        self.__game.after(random.randrange(int(0.5e3), int(1e3)), self.spawn_more)

    @property
    def game(self) -> "TurtleAdventureGame":
        """
        Get reference to the associated TurtleAnvengerGame instance
        """
        return self.__game

    @property
    def level(self) -> int:
        """
        Get the game level
        """
        return self.__level

    def safe_area(self, x, y):
        return (self.game.player.x-100 <= x <= self.game.player.x+100) and \
            (self.game.player.y-100 <= y <= self.game.player.y+100)

    def home_area(self, x, y):
        dist = (self.game.home.size / 2) * 5
        return (self.game.home.x-dist <= x <= self.game.home.x+dist) and \
            (self.game.player.y-dist <= y <= self.game.player.y+dist)

    def create_enemy(self, enemy_type=None) -> None:
        """
        Create a new enemy, possibly based on the game level
        """
        if enemy_type is None:
            enemy_type = random.choice(self.__enemies)
        enemy = enemy_type(self.__game, random.randrange(15, 30))
        if isinstance(enemy, CampingEnemy):
            enemy.x = self.game.home.x - enemy.multiplier
            enemy.y = self.game.home.y - enemy.multiplier
        else:
            while True:
                tempx = random.randrange(0+int(enemy.size/2), self.game.winfo_width()-int(enemy.size/2))
                tempy = random.randrange(0+int(enemy.size/2), self.game.winfo_height()-int(enemy.size/2))
                if not self.safe_area(tempx, tempy) and (not self.home_area(tempx, tempy)):
                    break
            enemy.x = tempx
            enemy.y = tempy
        self.game.add_element(enemy)

    def initial_enemies(self):
        for _ in range(self.level):
            for enemy_type in self.__enemies:
                self.create_enemy(enemy_type)

    def spawn_more(self):
        for _ in range(int(self.level*1.5)+1):
            self.create_enemy()
        self.__game.after(random.randrange(int(1e3), int(1.5e3)), self.spawn_more)


class TurtleAdventureGame(Game): # pylint: disable=too-many-ancestors
    """
    The main class for Turtle's Adventure.
    """

    # pylint: disable=too-many-instance-attributes
    def __init__(self, parent, screen_width: int, screen_height: int, level: int = 1):
        self.level: int = level
        self.screen_width: int = screen_width
        self.screen_height: int = screen_height
        self.waypoint: Waypoint
        self.player: Player
        self.home: Home
        self.enemies: list[Enemy] = []
        self.enemy_generator: EnemyGenerator
        super().__init__(parent)

    def init_game(self):
        self.canvas.config(width=self.screen_width, height=self.screen_height)
        turtle = RawTurtle(self.canvas)
        # set turtle screen's origin to the top-left corner
        turtle.screen.setworldcoordinates(0, self.screen_height-1, self.screen_width-1, 0)

        self.waypoint = Waypoint(self)
        self.add_element(self.waypoint)
        self.home = Home(self, (self.screen_width-100, self.screen_height//2), 20)
        self.add_element(self.home)
        self.player = Player(self, turtle)
        self.add_element(self.player)
        self.canvas.bind("<Button-1>", lambda e: self.waypoint.activate(e.x, e.y))
        self.player.x = 50
        self.player.y = self.screen_height//2
        self.enemy_generator = EnemyGenerator(self, level=self.level)

    def add_enemy(self, enemy: Enemy) -> None:
        """
        Add a new enemy into the current game
        """
        self.enemies.append(enemy)
        self.add_element(enemy)

    def game_over_win(self) -> None:
        """
        Called when the player wins the game and stop the game
        """
        self.stop()
        font = ("Arial", 36, "bold")
        self.canvas.create_text(self.screen_width/2,
                                self.screen_height/2,
                                text="You Win",
                                font=font,
                                fill="green")

    def game_over_lose(self) -> None:
        """
        Called when the player loses the game and stop the game
        """
        self.stop()
        font = ("Arial", 36, "bold")
        self.canvas.create_text(self.screen_width/2,
                                self.screen_height/2,
                                text="You Lose",
                                font=font,
                                fill="red")
