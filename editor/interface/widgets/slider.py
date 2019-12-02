import os
import pyglet
from utils import interface_mixin
from utils import sprite_patching
from utils import utils


arrow_left_btn_png = pyglet.resource.image(os.path.join("static", "arrow_left.png"))
arrow_left_btn_pressed_png = pyglet.resource.image(os.path.join("static", "arrow_left_pressed.png"))


arrow_right_btn_png = pyglet.resource.image(os.path.join("static", "arrow_right.png"))
arrow_right_btn_pressed_png = pyglet.resource.image(os.path.join("static", "arrow_right_pressed.png"))


class Button:

    def __init__(self, x, y, batch, image, pressed_image=None,
                 scale=1, disabled_image=None, click_callback=None,
                 button_id=None, group=None, details=None):
        """
        :param x: int
        :param y: int
        :param batch: pyglet.graphics.Batch()
        :param scale: float
        :param image: resource.image("path/to/file")
        :param pressed_image: resource.image("path/to/file")
        :param disabled_image: resource.image("path/to/file")
        """
        self.image = image
        self.batch = batch
        self.group = group
        self.x = x
        self.y = y
        self.width = 0
        self.height = 0
        self.scale = scale
        self.unpressed_image = image
        if pressed_image is None:
            pressed_image = image
        self.pressed_image = pressed_image
        if disabled_image is None:
            disabled_image = image
        self.disabled_image = disabled_image
        self.is_disabled = False
        self.is_pressed = False
        self.click_callback = click_callback
        self.button_id = button_id
        self.sprite = None
        self.update_sprite()
        self.ordered_group = None
        self.details = details
        if group and hasattr(group, "buttons"):
            self.ordered_group = group
            self.ordered_group.buttons.add(self)

        pyglet.window.instance.push_handlers(
            on_mouse_release=self.on_mouse_release)

    def on_mouse_press(self, x, y, button, modifiers):
        if self.is_disabled:
            return
        if button != 1:
            return
        # if not self._is_my_click(x, y):
        #     return

        is_collide = utils.is_collide_2d(x, y, self.sprite)
        if is_collide:
            self.image = self.pressed_image
            self.update_sprite()
            self.is_pressed = True

    def on_mouse_release(self, x, y, button, modifiers):
        if self.is_disabled or not self.is_pressed:
            return
        if button != 1:
            return
        is_collide = utils.is_collide_2d(x, y, self.sprite)
        self.image = self.unpressed_image
        self.update_sprite()
        if is_collide:
            self.disable()
            if self.click_callback:
                self.click_callback(self)
        self.is_pressed = False

    def disable(self):
        self.is_disabled = True
        self.image = self.disabled_image
        self.update_sprite()

    def enable(self):
        self.is_disabled = False
        self.image = self.unpressed_image
        self.update_sprite()

    def delete(self):
        pyglet.window.instance.remove_handlers(
            on_mouse_release=self.on_mouse_release)

        if self.ordered_group:
            self.ordered_group.buttons.remove(self)

        self.sprite.delete()

    def update_sprite(self):
        if not self.sprite:
            self.sprite = pyglet.sprite.Sprite(
                img=self.image,
                x=self.x,
                y=self.y,
                group=self.group,
                batch=self.batch
            )
            return
        self.sprite.image = self.image
        self.sprite.update(
            x=self.x, y=self.y, scale=self.scale
        )
        self.width = self.sprite.width
        self.height = self.sprite.height


class Slider(interface_mixin.InterfaceMixin):
    style_file_path = os.path.join(
        os.path.dirname(os.path.abspath(__file__)), "slider.ini")
    bg_image = None
    rect_icon = None

    def __new__(cls, *args, **kwargs):
        if cls.bg_image is None:
            cls.bg_image = pyglet.resource.image(os.path.join("static", "black_rect.png"))
            cls.rect_icon = pyglet.resource.image(os.path.join("static", "rect.png"))
        return super(Slider, cls).__new__(cls)

    def __init__(self, x, y, min_value, max_value, value, batch,
                 base_z_index, on_change_callback=None, text_field=None,
                 is_float=False, precision=2):
        super().__init__()
        self.x = x
        self.y = y
        self.min_value = min_value
        self.max_value = max_value
        self.value = value
        self.width = 1
        self.batch = batch
        self.on_change_callback = on_change_callback
        self.base_z_index = base_z_index
        self.text_field = text_field
        self.is_float = is_float
        self.precision = precision

        self.entities = {}
        self.scale = 1
        self.is_slider_active = False

        self._create_sprites()

        pyglet.window.instance.push_handlers(
            on_mouse_release=self.on_mouse_release)

    def on_mouse_release(self, x, y, button_pressed, modifiers):
        self.is_slider_active = False

    def _set_filter(self):
        gl_filter = pyglet.graphics.GL_NEAREST
        pyglet.graphics.glTexParameteri(
            pyglet.graphics.GL_TEXTURE_2D,
            pyglet.graphics.GL_TEXTURE_MAG_FILTER,
            gl_filter
        )
        pyglet.graphics.glTexParameteri(
            pyglet.graphics.GL_TEXTURE_2D,
            pyglet.graphics.GL_TEXTURE_MIN_FILTER,
            gl_filter
        )

    def _create_sprites(self):
        self._set_filter()
        self.entities["left_arrow"] = Button(
            x=0,
            y=0,
            image=arrow_left_btn_png,
            pressed_image=arrow_left_btn_pressed_png,
            disabled_image=arrow_left_btn_png,
            button_id=None,
            click_callback=self._on_left_slider_arrow_click,
            batch=self.batch,
            group=pyglet.window.instance.order_groups[self.base_z_index + 2])
        self.entities["right_arrow"] = Button(
            x=0,
            y=0,
            image=arrow_right_btn_png,
            pressed_image=arrow_right_btn_pressed_png,
            disabled_image=arrow_right_btn_png,
            button_id=None,
            click_callback=self._on_right_slider_arrow_click,
            batch=self.batch,
            group=pyglet.window.instance.order_groups[self.base_z_index + 2])

        self.entities["bg"] = sprite_patching.SpritePatched(
            self.bg_image, x=0, y=0, batch=self.batch,
            group=pyglet.window.instance.order_groups[self.base_z_index + 1],
            on_click_callback=self.activate_rect_icon,
            on_drag_callback=self.drag_rect_icon,
            details={"name": "block rect on slider"})
        self.entities["bg"].scale_x = self.width / 32

        self.entities["rect_icon"] = sprite_patching.SpritePatched(
            self.rect_icon, x=0, y=0, batch=self.batch,
            group=pyglet.window.instance.order_groups[self.base_z_index + 3],
            on_click_callback=self.activate_rect_icon,
            on_drag_callback=self.drag_rect_icon,
            details={"name": "rect icon on slider"})

        self.get_scaled(0, True)

    def set_value(self, value):
        if self.is_float:
            self.value = round(value, self.precision)
        else:
            self.value = round(value)
        self._set_text_value()
        if self.on_change_callback:
            self.on_change_callback(self)
        self.get_scaled(0, True)

    def activate_rect_icon(self, sprite, x, y, button_pressed):
        self.is_slider_active = True
        self._calculate_value_from_x(x)

    def drag_rect_icon(self, sprite, x, y, dx, dy):
        if not self.is_slider_active:
            return
        self._calculate_value_from_x(x)

    def _calculate_value_from_x(self, x):
        min_x_drag = self.x + self.width * 0.02  # 2% from start will be 0
        max_x_drag = self.x + self.width * 0.98  # 2% from end will be 100%
        x_offset = x - min_x_drag
        if x_offset < 0:
            x_offset = 0
        max_delta = max_x_drag - min_x_drag

        coef = min(x_offset / max_delta, 1)

        max_value_delta = self.max_value - self.min_value
        new_value = self.min_value + max_value_delta * coef
        self.set_value(new_value)
        self.get_scaled(0, True)

    def _set_text_value(self):
        if self.text_field:
            if self.is_float:
                self.text_field.text = f"{self.value:.{self.precision}f}"
            else:
                self.text_field.text = str(self.value)

    def _on_left_slider_arrow_click(self, btn):
        btn.enable()
        if self.is_float:
            new_value = self.value - 1 * 10 ** (-1 * self.precision)
        else:
            new_value = self.value - 1
        if new_value < self.min_value:
            return
        self.set_value(new_value)

    def _on_right_slider_arrow_click(self, btn):
        btn.enable()
        if self.is_float:
            new_value = self.value + 1 * 10 ** (-1 * self.precision)
        else:
            new_value = self.value + 1
        if new_value > self.max_value:
            return
        self.set_value(new_value)

    def get_scaled(self, dt, force=False):
        is_required = super().get_scaled(dt, force)
        if is_required is False:
            return
        style = self.style
        bg = self.entities["bg"]

        w, h = pyglet.window.instance.get_size()
        init_scale = h / self.bg_image.height
        bg.scale_y = 1 / init_scale * self.scale

        bg_w = self.width
        bg.scale_x = (bg_w / bg.width) * bg.scale_x
        bg_h = bg.height

        bg.update(x=self.x, y=self.y)

        left_arrow = self.entities["left_arrow"]
        left_arrow.scale = self.scale * float(style["left_arrow"]["scale"])
        left_arrow.update_sprite()
        left_arrow.x = self.x - left_arrow.width
        left_arrow.y = self.y + int(bg_h * float(style["left_arrow"]["y_offset"]))
        left_arrow.update_sprite()  # not mistake, second is required

        right_arrow = self.entities["right_arrow"]
        right_arrow.scale = self.scale * float(style["right_arrow"]["scale"])
        right_arrow.x = self.x + self.width - 1
        right_arrow.y = self.y + int(bg_h * float(style["right_arrow"]["y_offset"]))
        right_arrow.update_sprite()

        # update rect_icon
        rect_icon = self.entities["rect_icon"]
        rect_icon.scale = self.scale * float(style["rect_icon"]["scale"])
        x_max_offset = self.width - rect_icon.width
        coef_x = (self.value - self.min_value) / (self.max_value - self.min_value)
        x_offset_from_min_offset = x_max_offset * coef_x

        rect_icon.update(
            x=self.x + x_offset_from_min_offset,
            y=self.y + int(bg_h * float(style["rect_icon"]["y_offset"])))