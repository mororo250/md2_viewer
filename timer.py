import time

class timer:
    __instance = None
    @staticmethod 
    def get_instance():
        # Static access method.
        if timer.__instance == None:
            timer()
        return timer.__instance
    def __init__(self):
        # Virtually private constructor.
        if timer.__instance != None:
            raise Exception("This class is a singleton!")
        else:
            timer.__instance = self

    def start(self):
        self.curr_time = time.time()
        self.last_time = 0

    # Need to be called in the beggining of a frame
    def update(self):
        self.last_time = self.curr_time
        self.curr_time = time.time()

    def get_fps(self):
        return 1.0 / (self.curr_time - self.last_time)