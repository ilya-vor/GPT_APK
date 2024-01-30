from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.textinput import TextInput
from kivy.uix.scrollview import ScrollView
from kivy.core.window import Window
from openai import OpenAI
import pickle

class ChatGPTApp(App):

    def build(self):
        # Основной контейнер
        main_layout = BoxLayout(orientation='vertical', spacing=10)

        # Верхняя панель кнопок
        buttons_box = BoxLayout(orientation='horizontal', spacing=10, size_hint_y=None, height=100)
        set_button = Button(text='Установить API', size_hint_x=0.5)
        set_button.bind(on_press=self.set_api_button)
        delete_button = Button(text='Удалить API', size_hint_x=0.5)
        delete_button.bind(on_press=self.delete_api_button)
        load_button = Button(text='Загрузить API', size_hint_x=0.5)
        load_button.bind(on_press=self.load_api_button)
        buttons_box.add_widget(set_button)
        buttons_box.add_widget(delete_button)
        buttons_box.add_widget(load_button)
        main_layout.add_widget(buttons_box)

        # Сообщения
        scroll_view = ScrollView()
        self.messages_layout = BoxLayout(orientation='vertical', spacing=5, size_hint_y=None)
        label = 'Добро пожаловать в ChatGPT! Просто отправь мне свой вопрос и я на него отвечу! \
Перед использованием не забудь включить VPN и нажать на "Загрузить API"!'
        message_label = TextInput(text=label,multiline=True, readonly=True, size_hint_y=None, height=300)
        self.messages_layout.add_widget(message_label)
        self.messages_layout.bind(minimum_height=self.messages_layout.setter('height'))
        scroll_view.add_widget(self.messages_layout)
        main_layout.add_widget(scroll_view)

        # Панель ввода
        input_box = BoxLayout(orientation='horizontal', spacing=5, size_hint_y=None, height=100)
        self.text_input = TextInput(multiline=True, size_hint_x=0.7)
        Window.softinput_mode = 'pan'  # Режим поднятия экрана
        send_button = Button(text='Отправить', size_hint_x=0.3)
        send_button.bind(on_press=self.on_send_button_press)
        input_box.add_widget(self.text_input)
        input_box.add_widget(send_button)
        main_layout.add_widget(input_box)

        global gpt
        gpt = GPT()

        return main_layout

    def on_send_button_press(self, instance):
        message_text = self.text_input.text
        self.send_message(f"Вы: {message_text}")
        self.text_input.text = ""

        try:
            ans = gpt.request(message_text)
        except Exception as e:
            ans = f"Произошла ошибка: {e}\n***ИСТОРИЯ СООБЩЕНИЙ ОЧИЩЕНА***"
            gpt.messages = [{"role": "system", "content": "You're a useful assistant."}]

        self.send_message(text=f"GPT: {ans}")

    def send_message(self, text):
        sendMessage = TextInput(text=text, readonly=True, multiline=True, size_hint_y=None)
        sendMessage.bind(minimum_height=sendMessage.setter('height'))
        self.messages_layout.add_widget(sendMessage)

    def load_api_button(self, instance):
        try:
            with open('api.pkl', 'rb') as file:
                api_key = pickle.load(file)['ключ']
            gpt.start(api_key)
            self.send_message(f"Api ключ \"{api_key}\" установлен")
        except:
            self.send_message("API ключ не найден. Сначала установите API ключ чтобы мы могли пообщаться")
            self.send_message("Для этого вставьте в поле ниже API ключ и нажмите на \"Установить API\"")

    def set_api_button(self, instanse):
        api = self.text_input.text
        gpt.start(api)
        self.text_input.text = ""
        data_to_save = {'ключ': api}
        with open('api.pkl', 'wb') as file:
            pickle.dump(data_to_save, file, protocol=4, fix_imports=False)
        self.send_message("Ключ OpenAI установлен и сохранен")

    def delete_api_button(self, instanse):
        with open('api.pkl', 'wb') as file:
            file.truncate()
        gpt.start("")
        self.send_message("Ключ OpenAI удален и очищен")

class GPT():

    def __init__(self, messages = None):
        if messages == None:
            messages = [{"role": "system", "content": "You're a useful assistant."}]
        self.messages = messages

    def start(self, api):
        self.client = OpenAI(api_key=api)

    def request(self, message):
        self.messages.append({"role": "user", "content": message})

        completion = self.client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=self.messages
        )

        chat_response = completion.choices[0].message.content
        self.messages.append({"role": "assistant", "content": chat_response})
        return chat_response

if __name__ == '__main__':
    ChatGPTApp().run()
