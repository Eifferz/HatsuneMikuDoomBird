from kivy.app import App
from kivy.uix.widget import Widget
from kivy.properties import ObjectProperty
from kivy.uix.image import Image
from kivy.core.window import Window
from kivy.clock import Clock
from random import randint
from kivy.properties import NumericProperty
from pipe import Pipe
from kivy.core.audio import SoundLoader

class Background(Widget):
    cloud_texture = ObjectProperty(None)
    floor_texture = ObjectProperty(None)

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        self.cloud_texture = Image(source="doommonstr.png").texture
        self.cloud_texture.wrap = 'repeat'
        self.cloud_texture.uvsize = (Window.width / self.cloud_texture.width, -1)

        self.floor_texture = Image(source="floor.png").texture
        self.floor_texture.wrap = 'repeat'
        self.floor_texture.uvsize = (Window.width / self.floor_texture.width, -1)

    def on_size(self, *args):
        self.cloud_texture.uvsize = (self.width / self.cloud_texture.width, -1)
        self.floor_texture.uvsize = (self.width / self.floor_texture.width, -1)

    def scroll_textures(self, time_passed):
        self.cloud_texture.uvpos = ((self.cloud_texture.uvpos[0] + time_passed/2.0) % Window.width, self.cloud_texture.uvpos[1])
        self.floor_texture.uvpos = ((self.floor_texture.uvpos[0] + time_passed) % Window.width, self.floor_texture.uvpos[1])
        texture = self.property('cloud_texture')
        texture.dispatch(self)

        texture = self.property('floor_texture')
        texture.dispatch(self)


class HM(Image):
    velocity = NumericProperty(0)
    sound = SoundLoader.load('DoomComplite.mp3')

    def on_touch_down(self, touch):
        self.source = "HM.png"
        self.velocity = 150
        super().on_touch_down(touch)

    def on_touch_up(self, touch):
        self.source = "HM.png"
        super().on_touch_up(touch)

    def __init__(self, **kwargs):
        super(HM, self).__init__(**kwargs)
        self.sound.loop = False
        self.sound.play()


class MainApp(App):
    pipes = []
    GRAVITY = 300
    was_colliding = False

    def move_hm(self, time_passed):
        hm = self.root.ids.hm
        hm.y = hm.y + hm.velocity * time_passed
        hm.velocity = hm.velocity - self.GRAVITY * time_passed
        self.check_collision()

    def check_collision(self):
        hm = self.root.ids.hm
        is_colliding = False
        for pipe in self.pipes:
            if pipe.collide_widget(hm):
                is_colliding = True
                if hm.y < (pipe.pipe_center - pipe.GAP_SIZE/2.0):
                    self.game_over()
                if hm.top > (pipe.pipe_center + pipe.GAP_SIZE/2.0):
                    self.game_over()
        if hm.y < 96:
            self.game_over()
        if hm.top > Window.height:
            self.game_over()

        if self.was_colliding and not is_colliding:
            self.root.ids.score.text = str(int(self.root.ids.score.text)+1)
        self.was_colliding = is_colliding

    def game_over(self):
        self.root.ids.hm.pos = (20, (self.root.height - 96) / 2.0)
        for pipe in self.pipes:
            self.root.remove_widget(pipe)
        self.frames.cancel()
        self.root.ids.start_button.disabled = False
        self.root.ids.start_button.opacity = 1

    def next_frame(self, time_passed):
        self.move_hm(time_passed)
        self.move_pipes(time_passed)
        self.root.ids.background.scroll_textures(time_passed)

    def start_game(self):
        self.root.ids.score.text = "0"
        self.was_colliding = False
        self.pipes = []
        self.frames = Clock.schedule_interval(self.next_frame, 1/60.)
        num_pipes = 5
        distance_between_pipes = Window.width / (num_pipes - 1)
        for i in range(num_pipes):
            pipe = Pipe()
            pipe.pipe_center = randint(96 + 100, self.root.height - 100)
            pipe.size_hint = (None, None)
            pipe.pos = (Window.width + i*distance_between_pipes, 96)
            pipe.size = (64, self.root.height - 96)

            self.pipes.append(pipe)
            self.root.add_widget(pipe)

    def move_pipes(self, time_passed):
        for pipe in self.pipes:
            pipe.x -= time_passed * 100

        num_pipes = 5
        distance_between_pipes = Window.width / (num_pipes - 1)
        pipe_xs = list(map(lambda pipe: pipe.x, self.pipes))
        right_most_x = max(pipe_xs)
        if right_most_x <= Window.width - distance_between_pipes:
            most_left_pipe = self.pipes[pipe_xs.index(min(pipe_xs))]
            most_left_pipe.x = Window.width


MainApp().run()
