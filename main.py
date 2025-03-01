import SpeechRecognition as sr
import pyttsx3
import os
import requests
from datetime import datetime
from selenium import webdriver
from sklearn.model_selection import train_test_split
from sklearn.linear_model import LogisticRegression
import pickle
import tkinter as tk
from tkinter import messagebox
from transformers import pipeline
import threading

# Инициализация речи и распознавания
recognizer = sr.Recognizer()
engine = pyttsx3.init()
browser = None  # инициализация браузера позже, если понадобится

# Инициализация модели NLP (использование предобученной модели BERT для анализа текста)
nlp = pipeline('text-classification')

# Базовые функции: озвучивание, распознавание, выполнение команд
def speak(text):
    engine.say(text)
    engine.runAndWait()

def listen():
    with sr.Microphone() as source:
        print("Listening...")
        audio = recognizer.listen(source)
        try:
            command = recognizer.recognize_google(audio, language="ru-RU")
            print(f"User said: {command}")
            return command.lower()
        except sr.UnknownValueError:
            speak("Извините, я не понял.")
            return ""

# Модуль для управления компьютером
def system_command(command):
    if "открой браузер" in command:
        os.system("start chrome")
        speak("Открываю браузер.")
    elif "выключи компьютер" in command:
        os.system("shutdown /s /t 1")
        speak("Выключаю компьютер.")
    elif "время" in command:
        current_time = datetime.now().strftime("%H:%M")
        speak(f"Текущее время: {current_time}")
    elif "громкость" in command:
        if "увеличь" in command:
            os.system("nircmd.exe changesysvolume 2000")
            speak("Громкость увеличена.")
        elif "уменьши" in command:
            os.system("nircmd.exe changesysvolume -2000")
            speak("Громкость уменьшена.")
    else:
        speak("Команда не распознана.")

# Модуль для работы с интернетом
def internet_command(command):
    global browser
    if "проверка интернета" in command:
        try:
            response = requests.get("http://www.google.com")
            if response.status_code == 200:
                speak("Интернет подключен.")
        except requests.ConnectionError:
            speak("Интернет недоступен.")
    elif "поиск" in command:
        speak("Что искать?")
        query = listen()
        if query:
            if not browser:
                browser = webdriver.Chrome()
            url = f"https://www.google.com/search?q={query}"
            browser.get(url)
            speak(f"Вот что я нашел по запросу {query}.")
    else:
        speak("Интернет команда не распознана.")

# Модуль для самообучения
def load_or_train_model():
    try:
        with open("model.pkl", "rb") as file:
            model = pickle.load(file)
        speak("Модель загружена.")
        return model
    except FileNotFoundError:
        speak("Модель не найдена, обучение начнется заново.")
        commands = ["открой браузер", "выключи компьютер", "проверка интернета", "время", "поиск"]
        labels = [0, 1, 2, 3, 4]  # Классы команд
        X_train, X_test, y_train, y_test = train_test_split(commands, labels, test_size=0.2, random_state=42)
        model = LogisticRegression()
        model.fit(X_train, y_train)
        with open("model.pkl", "wb") as file:
            pickle.dump(model, file)
        speak("Модель обучена.")
        return model

# Обработчик команд
def execute_command(command, model):
    command_map = {0: system_command, 1: system_command, 2: internet_command, 3: system_command, 4: internet_command}
    predicted = model.predict([command])[0]
    action = command_map.get(predicted, lambda x: speak("Команда не распознана."))
    action(command)

# Графический интерфейс
def create_gui():
    root = tk.Tk()
    root.title("Гедеон - Ваш голосовой помощник")

    def start_assistant():
        model = load_or_train_model()
        speak("Гедеон готов к работе.")

        def listen_loop():
            while True:
                command = listen()
                if command:
                    execute_command(command, model)

        threading.Thread(target=listen_loop, daemon=True).start()

    def show_info():
        messagebox.showinfo("О программе", "Гедеон - ваш умный голосовой помощник. Он развивается с каждым использованием.")

    start_button = tk.Button(root, text="Запустить", command=start_assistant)
    start_button.pack(pady=20)

    info_button = tk.Button(root, text="О программе", command=show_info)
    info_button.pack(pady=10)

    root.mainloop()

# Основной цикл работы помощника
def run_assistant():
    create_gui()

if __name__ == "__main__":
    run_assistant()
