import os
import pyglet
import random
import io
from utils import interface_mixin
from utils import sprite_patching
from utils import utils
from interface.widgets import slider
import tkinter
from tkinter import filedialog

from wand import image

STYLE_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                          "styles", "main_interface.ini")


class MainInterface(interface_mixin.InterfaceMixin):
    SPRITES_NAMES = ["example_color_border", "example_color"]
    BUTTONS_NAMES = ["save_dds_btn", "save_btn", "load_btn"]
    TEXTS_NAMES = [
        "r_text", "r_value",
        "g_text", "g_value",
        "b_text", "b_value",
        "a_text", "a_value",
        "dds_section", "png_section"
    ]
    SLIDERS_NAMES = ["r", "g", "b", "a"]
    style_file_path = STYLE_FILE

    def __init__(self):
        super().__init__()
        self.base_z_index = 0
        self.batches = pyglet.window.instance.batches

        self.png_batch = self.batches[1]
        self.png_batch.zoom = 1

        self.dds_batch = self.batches[3]
        self.dds_batch.zoom = 1

        self.order_groups = pyglet.window.instance.order_groups
        self.entities = {}
        self.x = 0
        self.x_ = 0
        self.y = 0
        self.y_ = 0

        self.png_data = bytearray()

        # images
        self.bg_image = pyglet.resource.image(os.path.join("static", "main_interface.png"))
        self.draw_framework_back = pyglet.resource.image(os.path.join("static", "draw_framework_back.png"))
        self.draw_framework_transp = pyglet.resource.image(os.path.join("static", "draw_framework_transp.png"))

        self._initiate_interface()
        self.get_scaled(0, force=True)
        self.canvas_width = 1

    def _initiate_interface(self):
        for key, entity in self.entities.items():
            entity.delete()
        self.entities = dict()

        self.entities["bg"] = sprite_patching.SpritePatched(
            self.bg_image, x=0, y=0, batch=self.batches[9],
            group=self.order_groups[self.base_z_index + 10],
            details={"name": "bg"}
        )

        self.entities["example_color_border"] = sprite_patching.SpritePatched(
            self.draw_framework_transp, x=0, y=0, batch=self.batches[9],
            group=self.order_groups[self.base_z_index + 12],
            details={"name": "example_color_border"}
        )

        self.entities["example_color"] = sprite_patching.SpritePatched(
            self.draw_framework_transp, x=0, y=0, batch=self.batches[9],
            group=self.order_groups[self.base_z_index + 11],
            details={"name": "example_color_border"}
        )

        self.entities["r_text"] = pyglet.text.Label(
                "Red:",
                font_name='Arial',
                font_size=18,
                x=0, y=0,
                anchor_x='left', anchor_y='bottom',
                color=(255, 0, 0, 255),
                group=self.order_groups[self.base_z_index + 11],
                batch=self.batches[9]
        )
        self.entities["r_value"] = pyglet.text.Label(
                f"0",
                font_name='Arial',
                font_size=18,
                x=0, y=0,
                anchor_x='left', anchor_y='bottom',
                color=(255, 0, 0, 255),
                group=self.order_groups[self.base_z_index + 11],
                batch=self.batches[9]
        )

        self.entities["r"] = slider.Slider(
            x=0, y=0, min_value=0, max_value=255,
            value=0,
            batch=self.batches[9],
            base_z_index=self.base_z_index + 11,
            text_field=self.entities["r_value"],
            on_change_callback=self.on_slider_change_color
        )

        self.entities["g_text"] = pyglet.text.Label(
                "Green:",
                font_name='Arial',
                font_size=18,
                x=0, y=0,
                anchor_x='left', anchor_y='bottom',
                color=(0, 255, 0, 255),
                group=self.order_groups[self.base_z_index + 11],
                batch=self.batches[9]
        )
        self.entities["g_value"] = pyglet.text.Label(
                f"0",
                font_name='Arial',
                font_size=18,
                x=0, y=0,
                anchor_x='left', anchor_y='bottom',
                color=(0, 255, 0, 255),
                group=self.order_groups[self.base_z_index + 11],
                batch=self.batches[9]
        )

        self.entities["g"] = slider.Slider(
            x=0, y=0, min_value=0, max_value=255,
            value=0,
            batch=self.batches[9],
            base_z_index=self.base_z_index + 11,
            text_field=self.entities["g_value"],
            on_change_callback=self.on_slider_change_color
        )

        self.entities["b_text"] = pyglet.text.Label(
                "Blue:",
                font_name='Arial',
                font_size=18,
                x=0, y=0,
                anchor_x='left', anchor_y='bottom',
                color=(0, 0, 255, 255),
                group=self.order_groups[self.base_z_index + 11],
                batch=self.batches[9]
        )
        self.entities["b_value"] = pyglet.text.Label(
                f"0",
                font_name='Arial',
                font_size=18,
                x=0, y=0,
                anchor_x='left', anchor_y='bottom',
                color=(0, 0, 255, 255),
                group=self.order_groups[self.base_z_index + 11],
                batch=self.batches[9]
        )

        self.entities["b"] = slider.Slider(
            x=0, y=0, min_value=0, max_value=255,
            value=0,
            batch=self.batches[9],
            base_z_index=self.base_z_index + 11,
            text_field=self.entities["b_value"],
            on_change_callback=self.on_slider_change_color
        )

        self.entities["a_text"] = pyglet.text.Label(
                "Alpha:",
                font_name='Arial',
                font_size=18,
                x=0, y=0,
                anchor_x='left', anchor_y='bottom',
                color=(255, 255, 255, 255),
                group=self.order_groups[self.base_z_index + 11],
                batch=self.batches[9]
        )
        self.entities["a_value"] = pyglet.text.Label(
                f"255",
                font_name='Arial',
                font_size=18,
                x=0, y=0,
                anchor_x='left', anchor_y='bottom',
                color=(255, 255, 255, 255),
                group=self.order_groups[self.base_z_index + 11],
                batch=self.batches[9]
        )

        self.entities["a"] = slider.Slider(
            x=0, y=0, min_value=0, max_value=255,
            value=255,
            batch=self.batches[9],
            base_z_index=self.base_z_index + 11,
            text_field=self.entities["a_value"],
            on_change_callback=self.on_slider_change_color
        )

        self.entities["dds_section"] = pyglet.text.Label(
                "DDS section:",
                font_name='Arial',
                font_size=18,
                x=0, y=0,
                anchor_x='left', anchor_y='bottom',
                color=(255, 255, 255, 255),
                group=self.order_groups[self.base_z_index + 11],
                batch=self.batches[9]
        )

        save_btn_image = pyglet.resource.image(os.path.join("static", "save_btn.png"))
        self.entities["save_dds_btn"] = slider.Button(
            x=0,
            y=0,
            image=save_btn_image,
            pressed_image=save_btn_image,
            disabled_image=save_btn_image,
            button_id=None,
            click_callback=self.save_dds_file,
            batch=self.batches[9],
            group=self.order_groups[self.base_z_index + 11]
        )

        self.entities["png_section"] = pyglet.text.Label(
                "PNG section:",
                font_name='Arial',
                font_size=18,
                x=0, y=0,
                anchor_x='left', anchor_y='bottom',
                color=(255, 255, 255, 255),
                group=self.order_groups[self.base_z_index + 11],
                batch=self.batches[9]
        )

        self.entities["save_btn"] = slider.Button(
            x=0,
            y=0,
            image=save_btn_image,
            pressed_image=save_btn_image,
            disabled_image=save_btn_image,
            button_id=None,
            click_callback=self.save_source_image,
            batch=self.batches[9],
            group=self.order_groups[self.base_z_index + 11]
        )

        load_btn_image = pyglet.resource.image(os.path.join("static", "load_btn.png"))
        self.entities["load_btn"] = slider.Button(
            x=0,
            y=0,
            image=load_btn_image,
            pressed_image=load_btn_image,
            disabled_image=load_btn_image,
            button_id=None,
            click_callback=self.load_png_image,
            batch=self.batches[9],
            group=self.order_groups[self.base_z_index + 11]
        )

        self.entities["png_draw_framework_back"] = sprite_patching.SpritePatched(
            self.draw_framework_back, x=0, y=0, batch=self.batches[0],
            group=self.order_groups[self.base_z_index],
            details={"name": "png_draw_framework_back"}
        )

        # CANVAS
        data = []
        width = 32
        height = 32
        for _ in range(width * height):
            if _ < (width * height) / 2:
                data.append(255)
                data.append(0)
                data.append(0)
            else:
                data.append(random.randrange(256))
                data.append(random.randrange(256))
                data.append(random.randrange(256))
            data.append(255)
        self.png_data = bytearray(data)
        image_data = pyglet.image.ImageData(width=width, height=height, format="RGBA", data=bytes(self.png_data))
        self.entities["png_canvas"] = sprite_patching.SpritePatched(
            image_data, x=0, y=0, batch=self.png_batch,
            group=self.order_groups[self.base_z_index],
            details={"name": "png_canvas"}
        )

        image_data = pyglet.image.ImageData(width=1, height=1, format="RGBA", data=bytes([0, 0, 0, 0]))
        self.entities["dds_canvas"] = sprite_patching.SpritePatched(
            image_data, x=0, y=0, batch=self.dds_batch,
            group=self.order_groups[self.base_z_index],
            details={"name": "dds_canvas"}
        )
        self.transform_to_dds()
        # END - CANVAS

        self.entities["png_draw_framework_transp"] = sprite_patching.SpritePatched(
            self.draw_framework_transp, x=0, y=0, batch=self.batches[2],
            group=self.order_groups[self.base_z_index],
            details={"name": "png_draw_framework_transp"}
        )

        self.entities["dds_draw_framework_back"] = sprite_patching.SpritePatched(
            self.draw_framework_back, x=0, y=0, batch=self.batches[2],
            group=self.order_groups[self.base_z_index],
            details={"name": "dds_draw_framework_back"}
        )

        self.entities["dds_draw_framework_transp"] = sprite_patching.SpritePatched(
            self.draw_framework_transp, x=0, y=0, batch=self.batches[4],
            group=self.order_groups[self.base_z_index + 1],
            details={"name": "dds_draw_framework_transp"},
        )

        self.on_slider_change_color()
        self.get_scaled(0, force=True)

    def on_slider_change_color(self, *args, **kwargs):
        color = (
            self.entities["r"].value,
            self.entities["g"].value,
            self.entities["b"].value,
            self.entities["a"].value
        )

        image_data = pyglet.image.ImageData(width=1, height=1, format="RGBA", data=bytes(color))
        self.entities["example_color"].image = image_data
        self.entities["example_color"].set_filter()

    def save_source_image(self, *args, **kwargs):
        self.entities["save_btn"].enable()
        tk = tkinter.Tk()
        tk.withdraw()
        file_path = filedialog.asksaveasfilename(
            initialdir=".", title="Name your PNG file",
            filetypes=(("PNG", "*.png"), )
        )
        if not file_path:
            return
        canvas = self.entities["png_canvas"]
        width = canvas.image.width
        height = canvas.image.height
        image_data = pyglet.image.ImageData(
            width=width, height=height, format="RGBA", data=bytes(self.png_data)
        )
        image_data.save(file_path)
        print(f"file was saved")

    def load_png_image(self, *args, **kwargs):

        self.entities["load_btn"].enable()
        tk = tkinter.Tk()
        tk.withdraw()
        file_path = filedialog.askopenfilename(
            initialdir=".", title="Name your PNG file",
            filetypes=(("PNG", "*.png"), )
        )
        if not file_path:
            return
        image_to_load = pyglet.image.load(file_path)
        canvas = self.entities["png_canvas"]
        canvas.image = image_to_load
        canvas.set_filter()
        self.png_data = bytearray(canvas.image.get_image_data().get_data())
        self.transform_to_dds()

    def save_dds_file(self, *args, **kwargs):
        self.entities["save_dds_btn"].enable()
        tk = tkinter.Tk()
        tk.withdraw()
        file_path = filedialog.asksaveasfilename(
            initialdir=".", title="Name your DDS file (DXT5)",
            filetypes=(("DDS", "*.dds"), )
        )
        if not file_path:
            return
        blob = bytes(self.png_data)
        width = self.entities["png_canvas"].image.width
        height = self.entities["png_canvas"].image.height
        img = image.Image(format="RGBA",
                          blob=blob,
                          depth=8,
                          width=width,
                          height=height)
        # img.flip()
        image.library.MagickSetOption(img.wand, b"dds:mipmaps", b"0")
        image.library.MagickSetOption(img.wand, b"dds:compression", b"dxt5")
        dds_blob = img.make_blob(format="dds")

        with open(file_path, "wb") as f:
            f.write(dds_blob)
        print("dds file was saved")

    def click_on_png_canvas(self, normalized_x, normalized_y, button):
        if button != 1:
            return
        canvas = self.entities["png_canvas"]
        width = canvas.image.width
        height = canvas.image.height
        if normalized_x < 0 or normalized_x > width - 1:
            return
        if normalized_y < 0 or normalized_y > height - 1:
            return
        color = (
            self.entities["r"].value,
            self.entities["g"].value,
            self.entities["b"].value,
            self.entities["a"].value
        )

        y_sprite_offset = width * normalized_y * 4
        position = normalized_x * 4 + y_sprite_offset
        self.png_data[position:position + 4] = color
        image_data = pyglet.image.ImageData(width=width, height=height, format="RGBA", data=bytes(self.png_data))
        canvas.image = image_data
        canvas.set_filter()
        self.transform_to_dds()

    @utils.calculate_func_time
    def transform_to_dds(self):
        # !!!ACHTUNG!!!
        # memory leak here!
        blob = bytes(self.png_data)
        width = self.entities["png_canvas"].image.width
        height = self.entities["png_canvas"].image.height
        img = image.Image(format="RGBA",
                          blob=blob,
                          depth=8,
                          width=width,
                          height=height)
        image.library.MagickSetOption(img.wand, b"dds:mipmaps", b"0")
        image.library.MagickSetOption(img.wand, b"dds:compression", b"dxt5")
        dds_blob = img.make_blob(format="dds")
        with io.BytesIO() as in_memory:
            in_memory.write(dds_blob)
            in_memory.seek(0)

            dds_image = pyglet.image.load(filename="any.dds", file=in_memory)

        self.entities["dds_canvas"].image = dds_image
        self.entities["dds_canvas"].set_filter()

    def _post_bg_scale(self, bg):
        w, h = pyglet.window.instance.get_size()
        bg.scale = self.scale_y
        bg_w = bg.width
        bg.update(x=w - bg_w)
        self.x = bg.x
        self.y = bg.y

    def get_scaled(self, dt, force=False):
        is_required = super().get_scaled(dt, force)
        if is_required is False:
            return
        w, h = pyglet.window.instance.get_size()
        bg = self.entities["bg"]
        free_w = max(w - bg.width, 1)
        png_draw_framework_back = self.entities["png_draw_framework_back"]
        scale_x = png_draw_framework_back.scale_x * (free_w / 2) / max(png_draw_framework_back.width, 1)
        scale_y = png_draw_framework_back.scale_y * (h / max(png_draw_framework_back.height, 1))
        png_draw_framework_back.update(scale_x=scale_x, scale_y=scale_y)
        x_offset = png_draw_framework_back.width
        self.canvas_width = max(1, x_offset)

        self.entities["png_draw_framework_transp"].update(scale_x=scale_x, scale_y=scale_y)
        self.entities["dds_draw_framework_back"].update(scale_x=scale_x, scale_y=scale_y, x=x_offset)
        self.entities["dds_draw_framework_transp"].update(scale_x=scale_x, scale_y=scale_y, x=x_offset)

        self.png_batch.clipping_x = [0]
        self.dds_batch.clipping_x = [x_offset]