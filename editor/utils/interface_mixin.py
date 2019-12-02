import configparser
import pyglet
import hashlib


class InterfaceMixin:
    # required in inherited classes attributes
    style_file_path = ""
    SPRITES_NAMES = ()
    TEXTS_NAMES = ()
    SLIDERS_NAMES = ()
    BUTTONS_NAMES = ()

    # required in inherited __init__
    bg_image = None

    # optional or not required
    entities = None
    style_md5 = ""
    scale_y = 0
    x = 0
    y = 0

    def __init__(self):
        self.style = configparser.ConfigParser()
        self.style.read(self.style_file_path)
        self.style_md5 = hashlib.md5(open(self.style_file_path, "rb").read()).hexdigest()
        if pyglet.window.instance.draw:
            pyglet.window.instance.register_method_on_update(self.get_scaled)

    def get_scaled(self, dt, force=False):
        if len(self.entities.keys()) == 0:
            return False

        if pyglet.window.instance.draw:
            new_style_md5 = hashlib.md5(open(self.style_file_path, "rb").read()).hexdigest()
            if new_style_md5 != self.style_md5:
                self.style_md5 = new_style_md5
                style = configparser.ConfigParser()
                style.read(self.style_file_path)
                self.style = style
            else:
                if force is False:
                    return False

        style = self.style
        w, h = pyglet.window.instance.get_size()
        self.scale_y = scale_y = h / self.bg_image.height

        bg = self.entities["bg"]
        try:
            bg.scale = scale_y * float(style["bg"]["from_h_scale"])
        except KeyError:
            pass
        self._post_bg_scale(bg)
        scale_y = self.scale_y  # could be changed in "_post_bg_scale" method
        bg_w = bg.width
        bg_h = bg.height

        for sprite_name in self.SPRITES_NAMES:
            sprite = self.entities.get(sprite_name)
            if not sprite:
                continue
            sprite.scale = scale_y * float(style[sprite_name]["scale"])
            sprite.update(
                x=self.x + int(bg_w * float(style[sprite_name]["x_offset"])),
                y=self.y + int(bg_h * float(style[sprite_name]["y_offset"])))

        for btn_name in self.BUTTONS_NAMES:
            btn = self.entities.get(btn_name)
            if not btn:
                continue
            btn.x = self.x + int(bg_w * float(style[btn_name]["x_offset"]))
            btn.y = self.y + int(bg_h * float(style[btn_name]["y_offset"]))
            btn.scale = scale_y * float(style[btn_name]["scale"])
            btn.update_sprite()

        for text_name in self.TEXTS_NAMES:
            text_ = self.entities.get(text_name)
            if not text_:
                continue
            text_.font_size = scale_y * float(style[text_name]["font_scale"])
            text_.x = self.x + int(bg_w * float(style[text_name]["x_offset"]))
            text_.y = self.y + int(bg_h * float(style[text_name]["y_offset"]))

        for slider_name in self.SLIDERS_NAMES:
            slider_ = self.entities.get(slider_name)
            if not slider_:
                continue
            slider_.x = self.x + int(bg_w * float(style[slider_name]["x_offset"]))
            slider_.y = self.y + int(bg_h * float(style[slider_name]["y_offset"]))
            slider_.width = int(scale_y * float(style[slider_name]["width"]))
            slider_.scale = scale_y * float(style[slider_name]["scale"])
            slider_.get_scaled(0, True)

        return True

    def _post_bg_scale(self, bg):
        pass
