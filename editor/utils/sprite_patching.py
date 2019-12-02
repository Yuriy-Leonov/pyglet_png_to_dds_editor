import pyglet


class SpritePatched(pyglet.sprite.Sprite):

    def __init__(self, *args, **kwargs):
        self.gl_filter = pyglet.graphics.GL_NEAREST
        self.ordered_group = None
        group = kwargs.get("group")
        self.on_click_callback = kwargs.pop("on_click_callback", None)
        self.on_drag_callback = kwargs.pop("on_drag_callback", None)
        self.on_release_callback = kwargs.pop("on_release_callback", None)
        self.on_hover_callback = kwargs.pop("on_hover_callback", None)
        self.on_mouse_leave_callback = kwargs.pop("on_mouse_leave_callback", None)
        self.details = kwargs.pop("details", {})
        if group and hasattr(group, "sprites"):
            self.ordered_group = group
            self.ordered_group.sprites.add(self)

        super(SpritePatched, self).__init__(*args, **kwargs)
        self.set_filter()

    def set_filter(self):
        gl_filter = self.gl_filter
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

    def delete(self):
        if self.ordered_group:
            self.ordered_group.sprites.remove(self)
        try:
            pyglet.main_window.hover_previous.remove(self)
        except Exception:
            pass
        super(SpritePatched, self).delete()

    def on_click(self, x, y, button):
        if self.on_click_callback:
            return self.on_click_callback(self, x, y, button)

    def on_drag(self, x, y, dx, dy):
        if self.on_drag_callback:
            return self.on_drag_callback(self, x, y, dx, dy)

    def on_release(self):
        if self.on_release_callback:
            return self.on_release_callback(self)

    def on_hover(self, x, y, dx, dy):
        if self.on_hover_callback:
            return self.on_hover_callback(self, x, y, dx, dy)

    def on_mouse_leave(self, x, y, dx, dy):
        if self.on_mouse_leave_callback:
            return self.on_mouse_leave_callback(self, x, y, dx, dy)
