import numpy as np

class EpisodeSampler:
    def __init__(self, env, *args, episode_tracking=False, **kwargs) -> None:
        '''
        ADD
        Args:
            env : Any function or class that can be instantiated by a simple call and returns an environment instance.
            *args: All arguments which are specifically used to instantiate the enviornment.
        Kwargs:
            episode_tracking (bool) : Whether the sampler should store the episode data in a list internally or not.
            **kwargs: All keyword arguments which are specifically used to instantiate the environment.
        Returns:
            None
        '''
        
        self.__env = env(*args, **kwargs)
        self.__store = episode_tracking
        self.__episode = []

    def reset(self, *args, **kwargs) -> tuple:
        '''
        Reset function wrapper for the environment wrapped inside the EpisodeSampler.
        Args:
            *args: All the arguments given to the reset function of the environment.
        Kwargs:
            **kwargs: All the keyword arguments given to the reset function of the environment.
        Returns:
            tuple: The output of the env.reset function as a tuple of what the environment returns.
        '''
        
        del self.__episode
        self.__episode = []
        
        step = self.__env.reset(*args, **kwargs)
        if self.__store:
            self.__episode.append(step)
        
        return *step

    def step(self, *args, **kwargs) -> tuple:
        '''
        ADD
        '''
        
        step = self.__env.step(*args, **kwargs)
        if self.__store:
            self.__episode.append(step)
        
        return *step
        
    @property
    def episode(self) -> list:
        '''
        ADD
        '''
        
        return self.__episode

    def __del__(self):
        '''
        ADD
        '''
        
        del self.__episode

#assumes a reset and a step method for the environment
#ideally make samplers rey.remote-able
#environments are required to take in args adn kwargs without throwing errors

class VectorSampler:
    def __init__(self, env_class, n : int, buffer_size=10000, init_args=tuple(), init_kwargs=dict()):
        '''
        ADD
        
        Args:
            env_class : Any function or class that can be instantiated by a simple call and returns an environment instance.
            n (int) : The number of environments to instantiate and run asynchronously/consecutively.
        Kwargs:
            init_args (tuple) : The arguments to give to the environment instantiation method.
            init_kwargs (dict) : The arguments to give to the environment instantiation method.
        Return:
            None
        '''
        
        self.__buffer = np.empty(shape=(stored_features, buffer_size))
        self.__envs = [for _ in range(n)] #this is where ray parallelization should be done

    # def reset(*args, **kwargs):
        # for env in self.__envs:
            # env.reset()

    def step(*args, **kwargs):
        None
        #if environment has reached a terminal state:
        #reset it

    def __write(self, epsiode):
        pass

    @property
    def raw_trajectories(self):
        '''
        Returns the raw trajectories of the currently running episodes.
        '''
        return None

    @property
    def processed_trajectories(self):
        '''
        ADD
        '''
        return None

    def preprocess(self):
        '''
        ADD
        '''

        pass

    def compute_advantages(self):
        pass

    def compute_logprob(self):
        pass