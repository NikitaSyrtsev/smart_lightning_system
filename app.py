import random
import time
import requests
from flask import Flask, render_template, request, jsonify
from threading import Thread

# Настройки для API OpenWeatherMap
API_KEY = 'dca475aa5e17cdcb35a1ff43d766be60'
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

# Flask приложение для управления светом
app = Flask(__name__)

# Инициализируем объекты света и датчиков
light = Light()
motion_sensor = MotionSensor()
light_sensor = LightSensor()
controller = Controller(light, motion_sensor, light_sensor)

# Маршрут главной страницы
@app.route('/')
def index():
    return render_template('index.html', light_state=light.state, brightness=light.brightness)

# API для управления светом через интерфейс
@app.route('/light/on', methods=['POST'])
def turn_on_light():
    light.turn_on()
    return jsonify({'state': light.state})

@app.route('/light/off', methods=['POST'])
def turn_off_light():
    light.turn_off()
    return jsonify({'state': light.state})

@app.route('/light/brightness', methods=['POST'])
def set_brightness():
    level = request.form.get('brightness', 100, type=int)
    light.set_brightness(level)
    return jsonify({'brightness': light.brightness})

# Фоновая функция для автоматического управления светом
def auto_control_light():
    while True:
        controller.check_sensors_and_control_light()
        time.sleep(10)  # Проверка каждые 10 секунд
        
        
# import matplotlib.pyplot as plt
# import numpy as np

# # Генерация случайных данных для датчика движения
# time = np.arange(0, 100, 1)  # Время от 0 до 100 секунд
# motion_data = np.random.choice([0, 1], size=len(time))  # 0 - нет движения, 1 - есть движение

# # Генерация случайных данных для датчика освещённости
# brightness_data = np.random.randint(0, 101, size=len(time))  # Яркость от 0 до 100%

# # Создание двух графиков
# fig, axs = plt.subplots(2, 1, figsize=(10, 8))

# # График для данных с датчика движения
# axs[0].plot(time, motion_data, drawstyle='steps-pre', color='blue', label='Движение (0 - нет, 1 - да)')
# axs[0].set_title('Данные с датчика движения')
# axs[0].set_xlabel('Время (с)')
# axs[0].set_ylabel('Движение')
# axs[0].legend()
# axs[0].grid(True)

# # График для данных с датчика освещённости
# axs[1].plot(time, brightness_data, color='orange', label='Яркость (%)')
# axs[1].set_title('Данные с датчика освещённости')
# axs[1].set_xlabel('Время (с)')
# axs[1].set_ylabel('Яркость (%)')
# axs[1].legend()
# axs[1].grid(True)

# # Отображение графиков
# plt.tight_layout()
# plt.show()

if __name__ == "__main__":
    # Запускаем автоматическое управление светом в отдельном потоке
    auto_control_thread = Thread(target=auto_control_light)
    auto_control_thread.daemon = True
    auto_control_thread.start()

    # Запускаем Flask-сервер
    app.run(debug=True)
    
