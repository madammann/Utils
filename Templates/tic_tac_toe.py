import numpy as np

class TicTacToeGame:
    def __init__(self):
        self.__state = np.zeros((9,))
        self.__terminal = False
        
    def reset(self):
        self.__state = np.zeros((3,3))
        self.__terminal = False
        return self.__state, None

    def step(self, action):
        if self.__state[action] != 0:
            return self.__state, action, -10, False, False, None
        self.__state[action] = 1

        #the opponent makes a random move
        ran_idx = np.random.choice(np.arange(9))
        while self.__state[ran_idx] != 0:
            ran_idx += 1
            if ran_idx > 8:
                ran_idx = 0
                
        if self.__state[ran_idx] == 0:
            self.__state[ran_idx] = -1
        else:
            ran_idx += 1
        
        return self.__state, action, self.__terminal, None, None