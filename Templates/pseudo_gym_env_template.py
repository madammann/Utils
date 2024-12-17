import numpy as np

class PseudoGymTemplate:
    metadata = {"render_modes": ["human", "rgb_array"], "render_fps": 4}
    
    def __init__(self, *args, render_mode=None, **kwargs):
        assert render_mode is None or render_mode in self.metadata["render_modes"]
        self.render_mode = render_mode

    def step(self, *args, **kwargs):
        pass

    def reset(self, *args, **kwargs):
        pass

    @property
    def observation(self, *args, **kwargs):
        pass

    @property
    def terminal(self, *args, **kwargs):
        pass

    @property
    def render_mode(self, *args, **kwargs):
        pass

    @property
    def (self, *args, **kwargs):
        pass