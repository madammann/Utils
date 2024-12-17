import numpy as np

class TestEnvEBIMAS:
    def __init__(self, *args, **kwargs):
        pass

    def step(self, *args, **kwargs):
        reward = np.random.random(size=(1,))
        obs = np.random.randint(0,10,size=(16,4,80),dtype=np.float64)
        tar = np.random.randint(0,10,size(9,), dtype=np.float64)
        terminal = False if np.random.random() <= 0.99 else True

        return (obs, tar), args[0], reward, terminal, False, None

    def reset(self, *args, **kwargs):
        obs = np.random.randint(0,10,size=(16,4,80),dtype=np.float64)
        tar = np.random.randint(0,10,size(9,), dtype=np.float64)

        return (obs, tar), None