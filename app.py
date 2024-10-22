import random
import time
import sqlite3
import requests
from flask import Flask, render_template, request, jsonify
from threading import Thread
from dotenv import load_dotenv
import os

# Импортируем функции шифрования из encryption.py
from encryption import encrypt_data, decrypt_data

# Настройки для API OpenWeatherMap
load_dotenv('config.env')
API_KEY = os.getenv('API_KEY')
lat = 47.14
lon = 38.54
WEATHER_URL = f"https://api.openweathermap.org/data/2.5/weather?lat={lat}&lon={lon}&appid={API_KEY}"

# Класс для управления светом
class Light:
    def __init__(self, brightness=100):
        self.state = False  # Свет выключен по умолчанию
        self.brightness = brightness

    def turn_on(self):
        self.state = True
        print("Свет включен")

    def turn_off(self):
        self.state = False
        print("Свет выключен")

    def set_brightness(self, level):
        self.brightness = level
        print(f"Яркость установлена на {level}%")

# Класс для симуляции датчика движения
class MotionSensor:
    def __init__(self):
        self.motion_detected = False

    def detect_motion(self):
        # Симулируем движение с вероятностью 50%
        self.motion_detected = random.choice([True, False])
        if self.motion_detected:
            print("Обнаружено движение")
        else:
            print("Движение не обнаружено")
        return self.motion_detected

# Класс для датчика освещённости (использует данные о погоде)
class LightSensor:
    def __init__(self):
        self.current_brightness = 100

    def fetch_weather(self):
        try:
            response = requests.get(WEATHER_URL)
            weather_data = response.json()
            cloudiness = weather_data['clouds']['all']  # Процент облачности
            return cloudiness
        except Exception as e:
            print("Ошибка при получении данных о погоде:", e)
            return 50  # В случае ошибки возвращаем значение по умолчанию

    def adjust_brightness_based_on_weather(self):
        cloudiness = self.fetch_weather()
        # Если облачно, яркость будет выше, если солнечно — ниже
        self.current_brightness = 100 - int(cloudiness)
        print(f"Облачность: {cloudiness}%, яркость освещения: {self.current_brightness}%")
        return self.current_brightness

# Контроллер для управления светом на основе датчиков
class Controller:
    def __init__(self, light, motion_sensor, light_sensor):
        self.light = light
        self.motion_sensor = motion_sensor
        self.light_sensor = light_sensor

    def check_sensors_and_control_light(self):
        if self.motion_sensor.detect_motion():
            self.light.turn_on()
            # Устанавливаем яркость в зависимости от датчика освещённости
            brightness = self.light_sensor.adjust_brightness_based_on_weather()
            self.light.set_brightness(brightness)
        else:
            self.light.turn_off()

# Работа с базой данных SQLite с шифрованием данных
def init_db():
    conn = sqlite3.connect('lighting_data.db')
    cursor = conn.cursor()
    cursor.execute('''CREATE TABLE IF NOT EXISTS logs
                      (timestamp TEXT, action TEXT, brightness TEXT)''')
    conn.commit()
    conn.close()

def log_to_db(action, brightness):
    encrypted_action = encrypt_data(action)
    encrypted_brightness = encrypt_data(str(brightness))
    timestamp = time.strftime("%Y-%m-%d %H:%M:%S")

    conn = sqlite3.connect('lighting_data.db')
    cursor = conn.cursor()
    cursor.execute('INSERT INTO logs (timestamp, action, brightness) VALUES (?, ?, ?)',
                   (timestamp, encrypted_action, encrypted_brightness))
    conn.commit()
    conn.close()

def read_logs():
    conn = sqlite3.connect('lighting_data.db')
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM logs')
    rows = cursor.fetchall()
    conn.close()

    decrypted_logs = []
    for row in rows:
        timestamp = row[0]
        action = decrypt_data(row[1])
        brightness = decrypt_data(row[2])
        decrypted_logs.append((timestamp, action, brightness))
    return decrypted_logs

# Flask приложение для управления светом
app = Flask(__name__)

# Инициализируем объекты света и датчиков
light = Light()
motion_sensor = MotionSensor()
light_sensor = LightSensor()
controller = Controller(light, motion_sensor, light_sensor)

# Инициализация базы данных
init_db()

# Маршрут главной страницы
@app.route('/')
def index():
    logs = read_logs()
    return render_template('index.html', light_state=light.state, brightness=light.brightness, logs=logs)

# API для управления светом через интерфейс
@app.route('/light/on', methods=['POST'])
def turn_on_light():
    light.turn_on()
    log_to_db('light_on', light.brightness)
    return jsonify({'state': light.state})

@app.route('/light/off', methods=['POST'])
def turn_off_light():
    light.turn_off()
    log_to_db('light_off', light.brightness)
    return jsonify({'state': light.state})

@app.route('/light/brightness', methods=['POST'])
def set_brightness():
    level = request.form.get('brightness', 100, type=int)
    light.set_brightness(level)
    log_to_db('brightness_change', level)
    return jsonify({'brightness': light.brightness})

# Фоновая функция для автоматического управления светом
def auto_control_light():
    while True:
        controller.check_sensors_and_control_light()
        log_to_db('auto_control', light.brightness)
        time.sleep(10)  # Проверка каждые 10 секунд

if __name__ == "__main__":
    # Запускаем автоматическое управление светом в отдельном потоке
    auto_control_thread = Thread(target=auto_control_light)
    auto_control_thread.daemon = True
    auto_control_thread.start()

    # Запускаем Flask-сервер
    app.run(debug=True)
