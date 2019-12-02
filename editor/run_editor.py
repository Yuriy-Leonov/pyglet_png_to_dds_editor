import asyncio
import multiprocessing
import os
import sys
import platform
import time

import pyglet
from pyglet.window import key

from interface import interface_holder
from utils import utils


class Window(pyglet.window.Window):

    def __init__(self, *args, **kwargs):
        super(Window, self).__init__(*args, **kwargs)
        if platform.system() == "Windows":
            self.set_location(50, 50)
        else:
            self.set_location(0, 0)
        pyglet.window.instance = self
        self.draw = True  # used for interface changing
        # self.draw = False

        self.mouse_x = 0
        self.mouse_y = 0
        self.fps_display = pyglet.window.FPSDisplay(self)
        self.fps_display.label.color = (100, 100, 100, 255)
        self.fps_display.label.font_size = 10

        self.loop = asyncio.get_event_loop()
        self.inputs = []
        self.buttons_map = {}

        self.keys = key.KeyStateHandler()
        self.push_handlers(self.keys)

        self.normalized_x = 0  # means x on canvas
        self.previous_normalized_x = 0
        self.normalized_y = 0  # means y on canvas
        self.previous_normalized_y = 0

        w, h = self.get_size()
        self.previous_h = h
        self.position = [0, 0, 0]

        self.batches = [
            pyglet.graphics.Batch()
            for _ in range(10)
        ]
        self.batch_for_png = pyglet.graphics.Batch()
        self.batch_for_dds = pyglet.graphics.Batch()

        self.call_on_update = {}

        pyglet.clock.schedule_interval(self.update, 1 / 120)
        self.set_vsync(False)
        self.total_scale = 1
        self.order_groups = [
            utils.OrderedGroupMemories(z_ind)
            for z_ind in range(20)
        ]
        self.hover_previous = set()
        self.interface_holder = interface_holder.InterfaceHolder()
        asyncio.ensure_future(self.crunch_place_canvas_to_center())
        self.saved = True

    def make_screenshot(self):
        if not os.path.exists("screenshots"):
            os.makedirs("screenshots")
        name = f"screenshots{os.path.sep}Screenshot_{int(time.time() * 1000)}.png"
        pyglet.image.get_buffer_manager().get_color_buffer().save(name)
        print(f"print screen was made: {name}")

    def on_key_press(self, KEY, MOD):
        if KEY == key.ESCAPE:
            if self.saved:
                self.close()
                sys.exit(0)
            else:
                print("TODO add dialog window")
        if MOD & pyglet.window.key.MOD_CTRL and KEY == key.P:
            self.make_screenshot()
            return

    async def crunch_place_canvas_to_center(self):
        await asyncio.sleep(0)
        self.place_canvas_to_center()

    def place_canvas_to_center(self):
        _, canvas_height = self.get_size()
        canvas_width = self.interface_holder.main_interface.canvas_width
        png_image_width = self.interface_holder.main_interface.entities["png_canvas"].image.width
        png_image_height = self.interface_holder.main_interface.entities["png_canvas"].image.height
        zoom = self.interface_holder.main_interface.png_batch.zoom
        self.position[0] = (canvas_width / 2 - png_image_width / 2) * -1 * zoom
        self.position[1] = (canvas_height / 2 - png_image_height / 2) * -1 * zoom

    async def switch_context(self):
        await asyncio.sleep(0)

    def update(self, delta_time):
        self.loop.run_until_complete(self.switch_context())
        for method in list(self.call_on_update.keys()):
            method(delta_time)

    def register_method_on_update(self, method):
        self.call_on_update[method] = True

    def unregister_method_on_update(self, method):
        self.call_on_update.pop(method, None)

    def on_resize(self, width, height):
        self.interface_holder.get_scaled(0, force=True)

    def set_2d(self, batch):
        width, height = self.get_size()
        pyglet.graphics.glEnable(pyglet.graphics.GL_BLEND)
        if hasattr(batch, "clipping_x"):
            pyglet.graphics.glViewport(batch.clipping_x[0], 0, width, height)
        else:
            pyglet.graphics.glViewport(0, 0, width, height)
        pyglet.graphics.glMatrixMode(pyglet.graphics.GL_PROJECTION)
        pyglet.graphics.glLoadIdentity()
        if hasattr(batch, "zoom"):
            x, y, _ = self.position
            pyglet.graphics.glOrtho(x, (width + x / batch.zoom) * batch.zoom, y, (height + y / batch.zoom) * batch.zoom, -1, 1)
        else:
            pyglet.graphics.glOrtho(0, width, 0, height, -1, 1)
        pyglet.graphics.glMatrixMode(pyglet.graphics.GL_MODELVIEW)
        pyglet.graphics.glLoadIdentity()

    def on_draw(self):
        self.clear()
        for batch in self.batches:
            self.set_2d(batch)
            batch.draw()
        self.fps_display.draw()

    def on_mouse_motion(self, x, y, dx, dy):
        self.normalized_x, self.normalized_y = self.normalize_mouse_coords(x, y)
        self.mouse_x = x
        self.mouse_y = y

    def normalize_mouse_coords(self, x, y):
        if x > self.interface_holder.main_interface.canvas_width * 2:
            return -1, -1
        mouse_x_canvas_offset = x % self.interface_holder.main_interface.canvas_width
        self_x, self_y, _ = self.position
        zoom = self.interface_holder.main_interface.png_batch.zoom
        normalized_x = int(mouse_x_canvas_offset * zoom + self_x)
        normalized_y = int(y * zoom + self_y)
        return normalized_x, normalized_y

    def precise_normalize_mouse_coords(self, x, y):
        if x > self.interface_holder.main_interface.canvas_width * 2:
            return -1, -1
        mouse_x_canvas_offset = x % self.interface_holder.main_interface.canvas_width
        self_x, self_y, _ = self.position
        zoom = self.interface_holder.main_interface.png_batch.zoom
        normalized_x = mouse_x_canvas_offset * zoom + self_x
        normalized_y = y * zoom + self_y
        return normalized_x, normalized_y

    def on_mouse_scroll(self, x, y, scroll_x, scroll_y):
        if x > self.interface_holder.main_interface.canvas_width * 2:
            return
        normalized_x_init, normalized_y_init = self.precise_normalize_mouse_coords(x, y)

        # if scroll_y is positive - means scroll up
        png_batch = self.interface_holder.main_interface.png_batch
        dds_batch = self.interface_holder.main_interface.dds_batch
        scroll_y = scroll_y * -1

        current_zoom = png_batch.zoom
        diff = (scroll_y / 100) * current_zoom * 10
        new_zoom = current_zoom + diff

        png_batch.zoom = new_zoom
        dds_batch.zoom = new_zoom

        normalized_x_end, normalized_y_end = self.precise_normalize_mouse_coords(x, y)
        self.position[0] -= normalized_x_end - normalized_x_init
        self.position[1] -= normalized_y_end - normalized_y_init

    def on_mouse_drag(self, x, y, dx, dy, button, modifiers):
        self.normalized_x, self.normalized_y = self.normalize_mouse_coords(x, y)
        self.mouse_x = x
        self.mouse_y = y
        if button == 2:  # mouse wheel is held
            png_batch = self.interface_holder.main_interface.png_batch
            zoom = 1 * png_batch.zoom
            diff_x = (dx * zoom) * -1
            diff_y = (dy * zoom) * -1
            self.position[0] += diff_x
            self.position[1] += diff_y
        elif button == 1 and x <= self.interface_holder.main_interface.canvas_width:  # left mouse button
            if self.previous_normalized_x != self.normalized_x or self.previous_normalized_y != self.normalized_y:
                self.interface_holder.main_interface.click_on_png_canvas(
                    normalized_x=self.normalized_x,
                    normalized_y=self.normalized_y,
                    button=button
                )
        self.previous_normalized_x = self.normalized_x
        self.previous_normalized_y = self.normalized_y

        for group in reversed(self.order_groups):
            for sprite in group.sprites:
                if utils.is_collide_2d(x, y, sprite):
                    finish_hover = None
                    if button == 1:
                        finish_hover = sprite.on_drag(x, y, dx, dy)
                    if finish_hover == 1:
                        # skip
                        continue
                    return

    def on_mouse_press(self, x, y, button, modifiers):
        self.normalized_x, self.normalized_y = self.normalize_mouse_coords(x, y)
        self.mouse_x = x
        self.mouse_y = y
        if x <= self.interface_holder.main_interface.canvas_width and button == 1:
            # process click as on png canvas
            self.interface_holder.main_interface.click_on_png_canvas(
                normalized_x=self.normalized_x,
                normalized_y=self.normalized_y,
                button=button
            )
            return
        # below code works a little bit weird, because editor use several batches for 2d
        for group in reversed(self.order_groups):
            for btn in group.buttons:
                if utils.is_collide_2d(x, y, btn.sprite):
                    btn.on_mouse_press(x, y, button, modifiers)
                    return
            for sprite in group.sprites:
                if utils.is_collide_2d(x, y, sprite):
                    finish_click = sprite.on_click(x, y, button)
                    if finish_click == 1:
                        continue
                    return


if __name__ == '__main__':
    multiprocessing.freeze_support()
    window = Window(width=1600, height=600, caption='Pyglet', resizable=True)
    pyglet.app.run()
