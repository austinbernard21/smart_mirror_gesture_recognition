from kivy.base import runTouchApp
from kivy.app import App
from kivy.lang import Builder
from kivy.core.window import Window
from kivy.uix.screenmanager import Screen
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.gridlayout import GridLayout
from kivy.uix.floatlayout import FloatLayout
from kivy.clock import Clock

from kivy.graphics import Color, Line
from kivy.uix.button import Button
from kivy.metrics import dp
# from kivymd.uix.behaviors import HoverBehavior
# from kivydnd.dragndropwidget import DragNDropWidget
from kivy.uix.label import Label
from kivy.uix.widget import Widget
from kivy.uix.behaviors import DragBehavior
from kivy.properties import (
    ObjectProperty, StringProperty
)
from kivy.core.text import LabelBase
from kivy.graphics import Rectangle
import datetime
from threading import Thread
import pyautogui

import detector_threaded


Window.clearcolor = (1, 1, 1, 1)
Window.show_cursor = True
# Window.fullscreen = True

class ClockTime(Widget):
    # time_str = StringProperty('00:00')

    def __init__(self, **kwargs):
        # Call the initialization function of the parent class
        super(ClockTime, self).__init__(**kwargs)
        # Set the control to fill horizontally and set the height vertically
        # self.size_hint = (1, None)
        # self.height = 50
        # binding[subscribe]Event handling method of mouse position change
        # Window.bind(mouse_pos=self.on_mouse_pos)
        # self.stable_position = self.center
        # self.drag_rectangle = self.x, self.y, self.width, self.height
        # self.drag_timeout = 10000000
        # self.drag_distance = 0
        with self.canvas:
            # add your instruction for main canvas here
            Color(1, 0, .4, mode='rgb')
            Rectangle(pos=self.pos, size=self.size)
        # print('canvas',self.canvas)

    # time_str = StringProperty('00:00')

    def on_touch_down(self, touch):
        if 'pos' in touch.profile:
            if self.collide_point(touch.pos[0],touch.pos[1]):
                if (touch.is_double_tap):
                    print('double')
                else:
                    print('single')

    # def update_time(self):
    #     now = datetime.datetime.now()
    #     time_hour = now.strftime("%H")
    #     time_minutes = now.strftime("%M")
    #     self.time_str = f'[b]{time_hour} : [/b]{time_minutes}'

class HoverButton(Button):
    def __init__(self, **kwargs):
        # Call the initialization function of the parent class
        super(HoverButton, self).__init__(**kwargs)
        # Set the control to fill horizontally and set the height vertically
        # self.size_hint = (1, None)
        # self.height = 50
        # binding[subscribe]Event handling method of mouse position change
        Window.bind(mouse_pos=self.on_mouse_pos)
        self.stable_position = self.center
        

    # Mouse position processing method
    def on_mouse_pos(self, *args):
        if not self.get_root_window():
            return

        self.drag_rectangle = self.center[0], self.center[1], self.width, self.height
        self.drag_timeout = 10000000
        self.drag_distance = 0
        print(f'{self.text} : {self.center}')
        # Get mouse position data
        pos = args[1]
        t_x = self.center[0]
        t_y = Window.size[1] - self.center[1]
        self.stable_position = (t_x,t_y)
        # print('position ',self.pos)
        # print('drag ',self.drag_rectangle)
        # print('next')
        # print('stable', self.stable_position)

        if self.collide_point(*pos):
            # If on a control, the style method entered by the mouse is called
            Clock.schedule_once(self.mouse_enter_css, 0)
        else:
            # If on a control, the style method of mouse out is called
            Clock.schedule_once(self.mouse_leave_css, 0)

    def mouse_leave_css(self, *args):
        self.background_color = (1,1,1,1)
        # Window.set_system_cursor('arrow')

    def mouse_enter_css(self, *args):  
        self.background_color = (50,50,50,50)
        # Window.set_system_cursor('hand')

    def on_touch_down(self, touch):
        if self.collide_point(*touch.pos):
            # print(self.text)
            # pyautogui.moveTo(self.stable_position)
            pass


class Overlay2Layouts(Screen):

    def __init__(self, **kwargs):
        super(Overlay2Layouts, self).__init__(**kwargs)
        self.size = Window.size

        
        layout = GridLayout(cols=4,rows=4,opacity=0.7)
        rows = 4
        cols = 4
        for row in range(rows):
            for col in range(cols):
                layout.add_widget(HoverButton(text=f'Hello: {row}:{col}'))

        layout1 = FloatLayout()
        clock_widget = ClockTime()
        second_clock = ClockTime()
        layout1.add_widget(clock_widget)
        layout1.add_widget(second_clock)


        # layout1 = BoxLayout(opacity=0.5)
        # with layout1.canvas:
        #     Color(1, 0, 0, 1)   # red colour
        #     Line(points=[self.center_x, self.height / 4, self.center_x, self.height * 3/4])
        #     Line(points=[self.width * 3/ 4, self.center_y, self.width /4, self.center_y])

        # layout2 = BoxLayout()
        # with layout2.canvas:
        #     Color(0, 0, 0, 1)   # black colour
        #     Line(circle=[self.center_x, self.center_y, 190])

        self.add_widget(layout)
        self.add_widget(layout1)
        # self.add_widget(layout2)

# class ClockLayout(DragBehavior,BoxLayout):
#     time = ObjectProperty(None)


# class Main_Layout(FloatLayout):
#     clockObject = ObjectProperty(None)


class Multiple_LayoutApp(App): 
    def build(self): 
        ml = Overlay2Layouts()
        # Clock.schedule_interval(ml.call_update, 1.0 / 60.0)
        return ml


if __name__ == "__main__":
    # Clock.schedule_interval(my_callback,2)
    # runTouchApp(Overlay2Layouts())
    MlApp = Multiple_LayoutApp()
    MlApp.run()
