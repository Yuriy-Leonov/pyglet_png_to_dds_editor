import time
import pyglet


def calculate_func_time(f):
    def tmp(*args, **kwargs):
        st = int(time.time() * 1000)
        resp = f(*args, **kwargs)
        end = int(time.time() * 1000)
        print(f.__name__ + " running in " + str(end - st) + " ms")
        return resp
    return tmp


def is_collide_2d(x, y, sprite_2d):
    w = sprite_2d.width
    h = sprite_2d.height
    x_ = sprite_2d.x
    y_ = sprite_2d.y
    if x_ <= x <= (x_ + w) and y_ <= y <= (y_ + h):
        return True
    return False


class OrderedGroupMemories(pyglet.graphics.OrderedGroup):

    def __init__(self, order, parent=None):
        super(OrderedGroupMemories, self).__init__(order, parent)
        self.sprites = set()
        self.buttons = set()
