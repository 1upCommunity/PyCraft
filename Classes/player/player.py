# imports
from logging import root
from pyglet.window import key
from pyglet.gl import *
import math

# player class
class Player:
    """
    Player

    * the first person controller
    """
    def __init__(self, parent=None):
        """
        Player.__init__

        :pos: the position of the player
        :rot: the rotation of the player
        :parent: the parent of the player
        """
        self.pos = [0, 80, 0]
        self.rot = [0, 0, 0]
        self.vel = [0, 0]
        self.x = 0
        self.y = 0
        self.z = 0
        self.rotY = 0
        self.rotX = 0
        self.parent = parent
        self.speed = 0.3
        self.pointing_at = [[0,0,0], [0,0,0]]

        self.block_exists = {"left": False, "right": False,
                             "forward": False, "backward": False, "up": False, "down": False}
        self.suffocating = False
        self.falling = False
        self.velocity_y = 0
        self.gravity = 0.01
        self.hit_range = 8
        self.friction = 0.25

        self.terminal_velocity = 5

        self.mouse_click = False
        self.right_click = False

        self.block_type_names = []
        self.current_block_type = "Stone"
        for block in self.parent.model.block_types:
            self.block_type_names.append(block)
        self.current_block_label = pyglet.text.Label("Block: Stone",
            font_name='Arial',
            font_size=12,
            x=100, y=10,
            anchor_x='right', anchor_y='bottom')

    def mouse_motion(self, dx, dy):
        """
        mouse_motion

        * handles mouse movement

        :dx: the change in x
        :dy: the change in y
        """
        self.rot[0] += dy/8
        self.rot[1] -= dx/8
        if self.rot[0] > 90:
            self.rot[0] = 90
        elif self.rot[0] < -90:
            self.rot[0] = -90
        self.rot[0] = self.rot[0]
        self.rot[1] = self.rot[1]

    def collide(self):
        """
        collide

        * handles collision with the world
        """
        x_int = int(self.pos[0])
        y_int = int(self.pos[1])
        z_int = int(self.pos[2])

        if not self.parent.model.block_exists((x_int-1, y_int, z_int)) or self.parent.model.block_exists((x_int-1, y_int-1, z_int)):
            self.block_exists["left"] = False
        else:
            self.block_exists["left"] = True

        if self.parent.model.block_exists((x_int+1, y_int, z_int)) or self.parent.model.block_exists((x_int+1, y_int-1, z_int)):
            self.block_exists["right"] = False
        else:
            self.block_exists["right"] = True

        if not self.parent.model.block_exists((x_int, y_int, z_int-1)) or self.parent.model.block_exists((x_int, y_int-1, z_int+1)):
            self.block_exists["backward"] = False
        else:
            self.block_exists["backward"] = True

        if not self.parent.model.block_exists((x_int, y_int, z_int+1)) or self.parent.model.block_exists((x_int, y_int-1, z_int-1)):
            self.block_exists["forward"] = False
        else:
            self.block_exists["forward"] = True

        if self.parent.model.block_exists((x_int, y_int-2, z_int)):
            self.falling = False
            if self.velocity_y < 0:
                self.velocity_y = 0
        else:
            self.falling = True
            self.velocity_y -= self.gravity

        self._collide(self.pos)

    def _draw_label(self):
        self.current_block_label.text = "Block: " + self.current_block_type
        self.current_block_label.draw()

    def hit_test(self, position, vector, max_distance=8):
        """
        hit_test

        * checks if the player is pointing at a block

        :position: the position of the player
        :vector: the vector of the player
        :max_distance: the maximum distance to check

        :return: a list of positions
        """
        x, y, z = position
        dx, dy, dz = vector
        previous = None
        for _ in range(0, max_distance):
            key = (round(x), round(y), round(z))
            if key != previous and self.parent.model.block_exists(key):
                self.pointing_at[0] = key
                self.pointing_at[1] = previous
                return None
            previous = key
            x, y, z = x + dx, y + dy, z + dz
        self.pointing_at[0] = None
        self.pointing_at[1] = None
        return None

    def get_surrounding_blocks(self):
        """
        get_surrounding_blocks

        * gets the surrounding blocks of the player

        :return: a list of blocks
        """
        value = []
        if self.block_exists["forward"]:
            value.append((0, 0, -1))
        if self.block_exists["backward"]:
            value.append((0, 0, 1))
        if self.block_exists["right"]:
            value.append((1, 0, 0))
        if self.block_exists["left"]:
            value.append((-1, 0, 0))
        if self.block_exists["up"]:
            value.append((0, 1, 0))
        if self.block_exists["down"]:
            value.append((0, -1, 0))
        return value

    @staticmethod
    def _collision_algorithm(b1,b1_rad, b2, b2_side):
        """
        _collision_algorithm

        * handles collision

        :b1: the first entity
        :b1_rad: the radius of the first entity
        :b2: the second entity
        :b2_side: the side of the second entity

        :return: bool if collision
        """
        try:
            x1, y1, z1 = b1
            x2, y2, z2 = b2
            r1 = b1_rad
            r2 = b2_side

            if abs(x1 - x2) < r1 + r2 or abs(y1-y2) < r1 + r2 or abs(z1-z2) < r1 + r2:
                return True
            return False
        except:
            return False

    def _collide(self, position):
        """
        collide

        * handles collision with the world

        :position: the position of the player
        """
        x, y, z = position
        x = x-int(x)
        y = y-int(y)
        z = z-int(z)

        if self._collision_algorithm((x,y,z),0.45,(0,0,1),0.5) and self.vel[0] < 0 and self.block_exists["forward"]:
            self.vel[0] = 0
        elif self._collision_algorithm((x,y,z),0.45,(0,0,-1),0.5) and self.vel[0] > 0 and self.block_exists["backward"]:
            self.vel[0] = 0
        elif self._collision_algorithm((x,y,z),0.45,(-1,0,0),0.5) and self.vel[1] < 0 and self.block_exists["left"]:
            self.vel[1] = 0
        elif self._collision_algorithm((x,y,z),0.45,(1,0,0),0.5) and self.vel[1] > 0 and self.block_exists["right"]:
            self.vel[1] = 0

    def change_block(self, scroll):
        """
        change_block

        * changes a block

        :position: the position of the block
        :block: the block to change
        """
        index = self.block_type_names.index(self.current_block_type)
        index += round(scroll)
        if index > len(self.block_type_names)-1:
            index = 0
        elif index < 0:
            index = len(self.block_type_names)-1
        self.current_block_type = self.block_type_names[index]

        self.current_block_label.setText(self.current_block_type)

    def update(self, keys):
        """
        update

        * updates the player

        :dt: the delta time
        :keys: the keys pressed
        """
        sens = self.speed
        rotY = math.radians(-self.rot[1])
        rotX = math.radians(-self.rot[0])
        dx, dz = math.sin(rotY), math.cos(rotY)
        dy = math.sin(rotX)
        self.hit_test(position=self.pos, vector=(dx, -dy, -dz), max_distance=self.hit_range)
        
        if self.velocity_y > self.terminal_velocity:
            self.velocity_y = self.terminal_velocity
        if self.velocity_y < -self.terminal_velocity:
            self.velocity_y = -self.terminal_velocity

        if keys[key.W]:
            self.vel[0] += dx*sens
            self.vel[1] -= dz*sens
        if keys[key.S]:
            self.vel[0] -= dx*sens
            self.vel[1] += dz*sens
        if keys[key.A]:
            self.vel[0] -= dz*sens
            self.vel[1] -= dx*sens
        if keys[key.D]:
            self.vel[0] += dz*sens
            self.vel[1] += dx*sens
        if keys[key.SPACE] and not self.falling:
            self.velocity_y += 0.05
        if keys[key.LCTRL]:
            self.speed = 0.5
        else:
            self.speed = 0.3
        
        self.collide()

        if self.mouse_click and not self.pointing_at[0] is None and not self.pointing_at[1] is None:
            self.parent.model.remove_block([self.pointing_at[0][0], self.pointing_at[0][1], self.pointing_at[0][2]], self.parent.model.all_chunks[(round(self.pointing_at[0][0] / self.parent.model.chunk_size), round(self.pointing_at[0][2] / self.parent.model.chunk_size))])
        if self.right_click and not self.pointing_at[1] is None:
            self.parent.model.add_block(position = (self.pointing_at[1][0], self.pointing_at[1][1], self.pointing_at[1][2]), block = self.current_block_type, chunk = self.parent.model.all_chunks[(round(self.pos[1] / self.parent.model.chunk_size), round(self.pos[2] / self.parent.model.chunk_size))])

        self.pos[1] += self.velocity_y
        self.pos[0] += self.vel[0]
        self.pos[2] += self.vel[1]

        self.vel[0] *= self.friction
        self.vel[1] *= self.friction

    def _translate(self):
        glRotatef(-self.rot[0], 1, 0, 0)
        glRotatef(-self.rot[1], 0, 1, 0)
        glTranslatef(-self.pos[0], -self.pos[1], -self.pos[2])
