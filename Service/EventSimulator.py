# Python 3
from pynput.mouse import Controller as MController
from pynput.keyboard import Controller as KController

from Model.InputEvent import InputEvent, KeystrokeEvent, MouseMoveEvent, MouseClickEvent, MouseScrollEvent


class MouseEventSimulator:
    mouse = MController()
    
    print_callback = None
    
    def simulate(self, event: InputEvent):
        if isinstance(event, MouseMoveEvent):
            self.move(event.point)
        elif isinstance(event, MouseClickEvent):
            if event.is_pressed:
                self.press(event.key)
            else:
                self.release(event.key) 
        elif isinstance(event, MouseScrollEvent):
            self.scroll(event.point, event.scroll_dt)
        else:
            assert False
    
    def move(self, point):
        self.print(f"MouseEventSimulator: move to ({point.x},{point.y})")
        self.mouse.position = (point.x, point.y)
    
    def offset(self, offset):
        self.print(f"MouseEventSimulator: offset by ({offset.x},{offset.y})")
        self.mouse.move(offset[0], offset[1])
    
    def click(self, key):
        self.print(f"MouseEventSimulator: click {key}")
        self.mouse.click(key)
        
    def press(self, key):
        self.print(f"MouseEventSimulator: click {key}")
        self.mouse.press(key)
    
    def release(self, key):
        self.print(f"MouseEventSimulator: click {key}")
        self.mouse.release(key)
    
    def scroll(self, position, offset):
        self.print(f"MouseEventSimulator: scroll by ({offset[0]},{offset[1]}) @ ({position[0]},{position[1]})")
        self.mouse.move(position[0], position[1])
        self.mouse.scroll(offset[0], offset[1]) # TODO: not working ATM
    
    def print(self, string):
        if self.print_callback is not None:
            self.print_callback(string)

class KeyboardEventSimulator:
    keyboard = KController()

    print_callback = None
    
    def simulate(self, event: InputEvent):
        if isinstance(event, KeystrokeEvent):
            if event.is_pressed:
                self.press(event.key)
            else:
                self.release(event.key)
        else:
            assert False
    
    def click(self, key):
        self.print(f"KeyboardEventSimulator: click {key}")
        self.keyboard.tap(key)

    def press(self, key):
        self.print(f"KeyboardEventSimulator: press {key}")
        self.keyboard.press(key)
    
    def release(self, key):
        self.print(f"KeyboardEventSimulator: release {key}")
        self.keyboard.release(key)
    
    def type_character(self, key):
        self.print(f"KeyboardEventSimulator: type {key}")
        self.keyboard.press(key)
        self.keyboard.release(key)
    
    def print(self, string):
        if self.print_callback is not None:
            self.print_callback(string)
