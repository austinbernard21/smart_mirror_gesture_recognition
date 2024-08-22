from kivy.app import App
from kivy.uix.label import Label
from kivy.uix.widget import Widget
from kivy.clock import Clock
from kivy.uix.behaviors import DragBehavior
from kivy.properties import (
    ObjectProperty, StringProperty
)
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.boxlayout import BoxLayout
from kivy.core.text import LabelBase
from kivy.core.window import Window
import datetime
from threading import Thread
# import detector_threaded




class ClockTime(Widget):
    time_str = StringProperty('00:00')

    def on_touch_down(self, touch):
        if 'pos' in touch.profile:
            # print(touch.pos)
            # print(f"x: {touch.pos[0]}, y: {touch.pos[1]}")
            if self.collide_point(touch.pos[0], touch.pos[1]):
                print('collided')
        # if touch.is_double_tap:
        #     print('double')

    def update_time(self):
        now = datetime.datetime.now()
        time_hour = now.strftime("%H")
        time_minutes = now.strftime("%M")
        self.time_str = f'[b]{time_hour} : [/b]{time_minutes}'

class ClockDate(Widget):
    date_str = StringProperty('date')

    def update_date(self):
        today = datetime.datetime.today()
        date = today.strftime("%B %d, %Y")
        self.date_str = f'{date}'


class ClockLayout(DragBehavior, BoxLayout):
    time = ObjectProperty(None)
    date = ObjectProperty(None)

    def update(self):
        self.time.update_time()
        self.date.update_date()

    
  
class MultipleLayout(FloatLayout):
    clockObject = ObjectProperty(None)

    def call_update(self,dt):
        self.clockObject.update()
    
  
  
class Multiple_LayoutApp(App): 
    def build(self): 
        ml = MultipleLayout()
        Clock.schedule_interval(ml.call_update, 1.0 / 60.0)
        return ml
  
      

if __name__ == '__main__':
    # t = Thread(target=detector_threaded.run_detector)
    # t.daemon = True
    # t.start()
    # Window.fullscreen = True
    LabelBase.register(name='Roboto',
                   fn_regular='fonts/Roboto-Thin.ttf',
                   fn_bold='fonts/Roboto-Medium.ttf')
    MlApp = Multiple_LayoutApp()
    
    MlApp.run()