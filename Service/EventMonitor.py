from PyQt5.QtCore import pyqtSignal, QObject
from kink import di, inject
from pynput.keyboard import Listener as KeyboardListener
from pynput import mouse
from Model.KeyPressType import KeyPressType
from Model.KeyboardInputEvent import KeystrokeEvent
from Model.MouseInputEvent import MouseMoveEvent, MouseClickEvent, MouseScrollEvent
from Model.Point import Point
from Utilities.Logger import LoggerProtocol


# Docs:
# https://pynput.readthedocs.io/en/latest/keyboard.html
# https://pynput.readthedocs.io/en/latest/mouse.html
# Records keyboard strokes
@inject(use_factory=True)
class KeyboardEventMonitor(QObject):
    
    # Signal automatically binds to every unique instance
    signal_main = pyqtSignal(KeystrokeEvent, name='KeyboardEventMonitor.emit_event_on_main')
    
    # - Init
    
    def __init__(self):
        super(KeyboardEventMonitor, self).__init__()
        self.listener = None
        self.running = False
        self.signal_main.connect(self.emit_event_on_main)
        self.on_press_callback = None
        self.on_release_callback = None
        self.logger = di[LoggerProtocol]
    
    # - Properties
    
    def get_listener(self) -> KeyboardListener: return self.listener
    def set_listener(self, listener): self.listener = listener
    def get_on_press_callback(self): return self.on_press_callback
    def set_on_press_callback(self, callback): self.on_press_callback = callback
    def get_on_release_callback(self): return self.on_release_callback
    def set_on_release_callback(self, callback): self.on_release_callback = callback
    
    def is_running(self) -> bool:
        return self.running
    
    # - Setup
    
    def setup(self, on_press_callback, on_release_callback):
        self.reset()
        self.on_press_callback = on_press_callback
        self.on_release_callback = on_release_callback
    
    # - Actions
    
    def start(self):
        assert self.listener is not None
        assert not self.running
        
        self.logger.info("EventMonitor start")
        
        self.running = True
        
        self.listener.start()
    
    def stop(self):
        assert self.running
        
        self.logger.info("stop")
        
        self.running = False
        self.listener.stop()
        self.listener = None
    
    def reset(self):
        assert not self.running
        
        self.logger.info("reset monitor")
        self.running = False
        
        if self.listener is not None:
            self.listener.stop()
        
        self.listener = KeyboardListener(on_press=self.on_press, on_release=self.on_release)
    
    def join(self):
        assert self.running

        self.logger.info("join")
        
        self.listener.wait()
        self.listener.join()
    
    def on_press(self, key):
        if not self.running: return False
        self.logger.verbose_info(f"{key} pressed")
        
        self.signal_main.emit(KeystrokeEvent(KeyPressType.PRESS, key))
        
        return self.running
    
    def on_release(self, key):
        if not self.running: return False
        self.logger.verbose_info(f"{key} released")
        
        self.signal_main.emit(KeystrokeEvent(KeyPressType.RELEASE, key))
        
        return self.running
    
    def emit_event_on_main(self, value):
        if value.press == KeyPressType.PRESS:
            self.on_press_callback(value)
        else:
            self.on_release_callback(value)


# Record mouse movement
@inject(use_factory=True)
class MouseEventMonitor(QObject):
    
    # Signal automatically binds to every unique instance
    signal_main_move = pyqtSignal(MouseMoveEvent, name='MouseEventMonitor.emit_event_on_main_move')
    signal_main_click = pyqtSignal(MouseClickEvent, name='MouseEventMonitor.emit_event_on_main_click')
    signal_main_scroll = pyqtSignal(MouseScrollEvent, name='MouseEventMonitor.emit_event_on_main_scroll')
    
    # - Init
    
    def __init__(self):
        super(MouseEventMonitor, self).__init__()
        self.listener = None
        self.running = False
        
        self.on_move_callback = None
        self.on_press_callback = None
        self.on_release_callback = None
        self.on_scroll_callback = None
        
        self.signal_main_move.connect(self.emit_event_on_main_move)
        self.signal_main_click.connect(self.emit_event_on_main_click)
        self.signal_main_scroll.connect(self.emit_event_on_main_scroll)
        
        self.logger = di[LoggerProtocol]
    
    # - Properties
    
    def get_listener(self) -> mouse.Listener: return self.listener
    def set_listener(self, listener): self.listener = listener
    def get_on_move_callback(self): return self.on_move_callback
    def set_on_move_callback(self, callback): self.on_move_callback = callback
    def get_on_press_callback(self): return self.on_press_callback
    def set_on_press_callback(self, callback): self.on_press_callback = callback
    def get_on_release_callback(self): return self.on_release_callback
    def set_on_release_callback(self, callback): self.on_release_callback = callback
    def get_on_scroll_callback(self): return self.on_scroll_callback
    def set_on_scroll_callback(self, callback): self.on_scroll_callback = callback
    
    def is_running(self) -> bool:
        return self.running
    
    # - Setup
    
    def setup(self, on_move_callback, on_press_callback, on_release_callback, on_scroll_callback):
        self.reset()
        self.on_move_callback = on_move_callback
        self.on_press_callback = on_press_callback
        self.on_release_callback = on_release_callback
        self.on_scroll_callback = on_scroll_callback
    
    # - Actions
    
    def start(self):
        assert self.listener is not None
        assert not self.running

        self.logger.info("start")

        self.running = True

        self.listener.start()
    
    def stop(self):
        assert self.running
        
        self.logger.info("stop")
        
        self.running = False
        self.listener.stop()
        self.listener = None

    def join(self):
        assert self.running
        
        self.logger.info("join")
        
        self.listener.wait()
        self.listener.join()
    
    def on_move(self, x, y) -> bool:
        if not self.running: return False
        self.logger.verbose_info(f"({x}, {y}) moved")
        
        self.signal_main_move.emit(MouseMoveEvent(Point(x, y)))
        
        return self.running
    
    def on_click(self, x, y, key, is_pressed) -> bool:
        if not self.running: return False
        
        press = KeyPressType.PRESS if is_pressed else KeyPressType.RELEASE
        
        self.logger.verbose_info(f"{key} {press.name}")
        
        self.signal_main_click.emit(MouseClickEvent(press, key, Point(x, y)))
        
        return self.running
    
    def on_scroll(self, x, y, dx, dy) -> bool:
        if not self.running: return False
        
        self.logger.verbose_info(f"scrolled by ({x}, {y}) by ({dx}, {dy})")
        
        self.signal_main_scroll.emit(MouseScrollEvent(Point(x, y), Point(dx, dy)))
        
        return self.running
    
    def reset(self):
        assert not self.running
        
        self.logger.info("reset monitor")
        
        self.listener = mouse.Listener(on_move=self.on_move, on_click=self.on_click, on_scroll=self.on_scroll)
    
    def emit_event_on_main_move(self, event):
        self.on_move_callback(event)
    
    def emit_event_on_main_click(self, event):
        if event.press == KeyPressType.PRESS:
            self.on_press_callback(event)
        else:
            self.on_release_callback(event)
    
    def emit_event_on_main_scroll(self, event):
        self.on_scroll_callback(event)

