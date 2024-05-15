import time


class Timer:
    
    # - Init
    
    def __init__(self):
        self.running = False
        self.paused = False
        self.start_time = 0
        self.bonus_elapsed_time = 0
    
    # - Properties
    
    def is_running(self) -> bool:
        return self.running
    
    def is_paused(self) -> bool:
        return self.paused
    
    def elapsed_time(self) -> float:
        if not self.is_running() or self.is_paused():
            return self.bonus_elapsed_time
        
        return (time.time() - self.start_time) + self.bonus_elapsed_time
    
    # - Actions
    
    def start(self):
        assert not self.is_running()
        self.running = True
        self.start_time = time.time()
        self.paused = False
        self.bonus_elapsed_time = 0
    
    def pause(self):
        assert self.running
        assert not self.paused
        self.bonus_elapsed_time = self.elapsed_time()
        self.paused = True

    def resume(self):
        assert self.running
        assert self.paused
        self.paused = False
        self.start_time = time.time()
    
    def stop(self):
        assert self.running
        self.paused = False
        self.running = False
        self.bonus_elapsed_time = self.elapsed_time()
    
    def reset(self):
        assert not self.running
        self.bonus_elapsed_time = 0
