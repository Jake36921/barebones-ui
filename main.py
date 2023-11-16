import requests
import json
from kivy.lang import Builder
from kivymd.app import MDApp
from kivy.uix.scrollview import ScrollView
from kivy.uix.boxlayout import BoxLayout
from kivymd.uix.button import MDIconButton
from kivymd.uix.textfield import MDTextField
from kivy.animation import Animation
from kivy.uix.label import Label
from kivy.clock import Clock
from kivy.uix.modalview import ModalView
from kivy.uix.button import Button
from kivy.uix.filechooser import FileChooserIconView
import tkinter as tk
from tkinter import filedialog
import os

# API settings, replace with openai api key
url = "https://cute-z-glasgow-compressed.trycloudflare.com/v1/chat/completions/v1/chat/completions"
headers = {"Content-Type": "application/json"}
history = []

KV = '''
BoxLayout:
    orientation: 'vertical'

    ScrollView:

        MDList:
            id: chat_history

    BoxLayout:
        size_hint_y: None
        height: "40dp"

        MDTextField:
            id: user_input
            hint_text: "Type your message"

        MDIconButton:
            icon: "dots-vertical"
            on_release: app.open_menu()

        MDIconButton:
            icon: "send"
            on_release: app.send_message()
'''

class ChatApp(MDApp):
    def build(self):
        return Builder.load_string(KV)

    def send_message(self):
        user_message = self.root.ids.user_input.text
        history.append({"role": "user", "content": user_message})

        user_label = Label(text='User: ' + user_message, size_hint_y=None, color=(0, 0, 0, 1), halign='left')
        user_label.bind(texture_size=user_label.setter('size'), width=lambda instance, value: setattr(instance, 'text_size', (value, None)))
        self.root.ids.chat_history.add_widget(user_label)
        #anim = Animation(opacity=0, duration=0.5) + Animation(opacity=1, duration=0.5)
        #anim.start(user_label) #it looks horrible since user text will fade when getting response

        typing_label = Label(text='...', size_hint_y=None, color=(0, 0, 0, 1), halign='left')
        typing_label.bind(texture_size=typing_label.setter('size'), width=lambda instance, value: setattr(instance, 'text_size', (value, None)))
        self.root.ids.chat_history.add_widget(typing_label)
        anim = Animation(opacity=0, duration=0.5) + Animation(opacity=1, duration=0.5)
        anim.start(typing_label)

        def get_response(dt):
            data = {
                "mode": "chat",
                "character": "Example",
                "messages": history
            }
            response = requests.post(url, headers=headers, json=data, verify=False)
            assistant_message = response.json()['choices'][0]['message']['content']
            history.append({"role": "assistant", "content": assistant_message})

            self.root.ids.chat_history.remove_widget(typing_label)

            assistant_label = Label(text='Assistant: ' + assistant_message, size_hint_y=None, color=(0, 0, 0, 1), halign='left')
            assistant_label.bind(texture_size=assistant_label.setter('size'), width=lambda instance, value: setattr(instance, 'text_size', (value, None)))
            assistant_label.opacity=0
            self.root.ids.chat_history.add_widget(assistant_label)
            anim = Animation(opacity=0, duration=0.5) + Animation(opacity=1, duration=0.5)
            anim.start(assistant_label)

        Clock.schedule_once(get_response, 0.1)

        self.root.ids.user_input.text = ''

    

    def open_menu(self): #opens a menu duh
        box_layout = BoxLayout(orientation='vertical')
        box_layout.add_widget(Button(text='Save Chat', on_release=self.save_chat, background_color=(1, 1, 1, 1), color=(0, 0, 0, 1)))
        box_layout.add_widget(Button(text='Load Chat', on_release=self.load_chat, background_color=(1, 1, 1, 1), color=(0, 0, 0, 1)))
        box_layout.add_widget(Button(text='Clear Chat', on_release=self.clear_chat, background_color=(1, 1, 1, 1), color=(0, 0, 0, 1)))
    
        menu = ModalView(size_hint=(0.5, 0.5), background_color=(1, 1, 1, 1))
        menu.add_widget(box_layout)
        menu.open()

    def save_chat(self, instance): #self explanatory
        root = tk.Tk()
        root.withdraw() 
        file_path = filedialog.asksaveasfilename(defaultextension=".json")
        if file_path:
            with open(file_path, 'w') as f:
                json.dump(history, f)


    def load_chat(self, instance): #replaces history/context and deletes current chat
        root = tk.Tk()
        root.withdraw()
        file_path = filedialog.askopenfilename(filetypes=[("JSON files", "*.json")])
        if file_path:
            with open(file_path, 'r') as f:
                loaded_history = json.load(f)
            history.clear() 
            history.extend(loaded_history)
            self.root.ids.chat_history.clear_widgets()
            for message in loaded_history:
                label = Label(text=message['role'].capitalize() + ': ' + message['content'], size_hint_y=None, color=(0, 0, 0, 1), halign='left')
                label.bind(texture_size=label.setter('size'), width=lambda instance, value: setattr(instance, 'text_size', (value, None)))
                self.root.ids.chat_history.add_widget(label)
            data = {
                "mode": "chat",
                "character": "Example",
                "messages": history 
            }
            response = requests.post(url, headers=headers, json=data, verify=False)


    def clear_chat(self, instance): #self explanatory
        self.root.ids.chat_history.clear_widgets()
        history.clear() 
    
        data = {
            "mode": "chat",
            "character": "Example",
            "messages": history 
        }
        response = requests.post(url, headers=headers, json=data, verify=False)
        if instance.parent and instance.parent.parent:
            instance.parent.parent.dismiss()


ChatApp().run()
