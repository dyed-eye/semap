from kivy.app import App
from kivy.properties import ObjectProperty
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.gridlayout import GridLayout
from kivy.uix.checkbox import CheckBox
from kivy.uix.popup import Popup
from kivy.uix.textinput import TextInput
from kivy.uix.image import Image as KivyImage

import cv2 as cv
import os
import time
import xml.etree.ElementTree as ET

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

SCOPES = ['https://www.googleapis.com/auth/drive.readonly']
img_path = ''
grain_size = 0

# path example: "D:\emae\python\apfsem_examples\JACS_01.jpg"
# path has to be copied with right mouse button -> copy as path
# also we assume that metadata has path %path%_metadata.xml


class AlignLabel(Label):
    def on_size(self, *args):
        self.text_size = self.size


class LoadDialog(GridLayout):
    load = ObjectProperty(None)
    cancel = ObjectProperty(None)


# Container class for the app's widgets
class Main(Screen):

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        def image_recognising(img):
            cv.imwrite('res/cached_image.png', img)
            self.ids.image_preview.source = 'res/cached_image.png'
            self.ids.image_preview.reload()
            self.ids.image_preview.size = (img.shape[1] / img.shape[0] * 160, 160)
            self.ids.image_preview_label.text = 'Image preview:'
            self.messages.text = '[color=22ff22]Success![/color]'
            APfSEMApp.img_prev_source = 'res/cached_image.png'

        def ask_google(link):
            '''try:
                response = requests.get(link)
                with Image.open(BytesIO(response.content)) as img:
                    image_recognising(img)
            except:
                self.messages.text = '[color=ff1111]Error: no file specified[/color]'
                print('Error: no image specified')'''
            ...
            # TODO: requests to google api (it would be cool)

        def source_choose(checkbox, value):
            if value:
                self.text_input.text = os.path.dirname(os.path.abspath(__file__))
                self.browse_button.disabled = False
                self.browse_button.opacity = 1
                self.messages.text = ''

        def gd_choose(checkbox, value):
            if value:
                self.text_input.text = 'https://drive.google.com/'
                self.browse_button.disabled = True
                self.browse_button.opacity = 0
                self.messages.text = ''

        def confirm_path(instance):
            if self.ids.source_radio.active:
                if os.path.isfile(self.text_input.text):
                    img = cv.imread(cv.samples.findFile(self.text_input.text))
                    if img is None:
                        self.messages.text = '[color=ff1111]Error: no file specified[/color]'
                        print('Error: no image specified')
                    else:
                        image_recognising(img)
                else:
                    self.messages.text = '[color=ff1111]Error: no file specified[/color]'
                    print('Error: no file specified')
            elif self.ids.gd_radio.active:
                ask_google(self.text_input.text)

        def load(path, filename):
            if len(filename) == 1:
                self.text_input.text = filename[0]
                self.messages.text = ''
                confirm_path(None)
            else:
                self.messages.text = '[color=ff1111]Error: no file specified[/color]'
            # TODO: specify extensions (?)
            dismiss_popup()

        def dismiss_popup():
            self.pop_up.dismiss()

        def pick_path(instance):
            content = LoadDialog(load=load, cancel=dismiss_popup)
            self.pop_up = Popup(title="Select image", content=content,
                                size_hint=(0.9, 0.9))
            self.pop_up.open()

        def big_purple_button_action():
            # TODO: think about other circumstances (!)
            gr_s = 0
            try:
                gr_s = float(self.ids.grain_size_input.text)
            except:
                self.messages.text = '[color=ff1111]Error: incorrect number[/color]'
            if APfSEMApp.img_prev_source != 'res/blank.png':
                if gr_s > 0:
                    global img_path
                    img_path = APfSEMApp.img_prev_source
                    global grain_size
                    grain_size = float(self.ids.grain_size_input.text)
                    APfSEMApp.sm.current = 'process'
                    Evaluate.evaluate(self)
                else:
                    self.messages.text = '[color=ff1111]Error: size has not been stated or below zero[/color]'
            else:
                self.messages.text = '[color=ff1111]Error: choose an image[/color]'

        fp_l = self.ids.file_pick_layout

        self.ids.source_radio.bind(active=source_choose)
        self.ids.gd_radio.bind(active=gd_choose)

        self.text_input = TextInput(text=os.path.dirname(os.path.abspath(__file__)), multiline=False)
        fp_l.add_widget(self.text_input)
        self.browse_button = Button(text='...', on_press=pick_path, size_hint_x=None, width=40)
        fp_l.add_widget(self.browse_button)
        fp_l.add_widget(Button(text='confirm', on_press=confirm_path, size_hint_x=None, width=100))
        self.messages = AlignLabel(text='', markup=True, size_hint=(1.0, 1.0), halign='left', valign='middle')
        fp_l.add_widget(self.messages)

        self.ids.big_purple_button.on_press = big_purple_button_action


class Evaluate(Screen):

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    def evaluate(self):

        def calculate(path, size):
                time.sleep(20)
                print('calculated!')
                ...
                # TODO: get the grain sizes from picture

        calculate(img_path, grain_size)

        APfSEMApp.sm.current = 'result'


class Result(Screen):

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        layout = self.ids.result_screen_layout
        self.pic = KivyImage(source='res/cached_image.png')
        layout.add_widget(self.pic)


class APfSEMApp(App):
    img_prev_source = 'res/blank.png'
    img_prev_size = (0, 0)
    sm = ScreenManager()

    def build(self):
        self.sm.add_widget(Main(name='menu'))
        self.sm.add_widget(Evaluate(name='process'))
        self.sm.add_widget(Result(name='result'))
        return self.sm


if __name__ == '__main__':
    APfSEMApp().run()
