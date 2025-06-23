# scene_base.py

class SceneBase:
    def __init__(self):
        self.next_scene = self

    def process_input(self, events, keys):
        pass

    def update(self):
        pass

    def render(self, screen):
        pass

    def switch_to_scene(self, next_scene):
        self.next_scene = next_scene
