import sys
import json
import math
import time
from PyQt5.QtWidgets import QApplication, QWidget, QLineEdit, QPushButton
from PyQt5.QtGui import QPainter, QColor
from PyQt5.QtCore import QTimer, Qt, QPoint


class Asteroid:
    def __init__(self, position, radius, direction, speed):
        self.position = position
        self.radius = radius
        self.direction = direction  # угол в градусах
        self.speed = speed
        self.x_pos = int(self.position.x())
        self.y_pos = int(self.position.y())

    def update_position(self):
        # Обновляем позицию астероида на основе его скорости и направления
        dx = self.speed * math.cos(math.radians(self.direction))
        dy = self.speed * math.sin(math.radians(self.direction))
        # Преобразуем dx и dy в int перед созданием нового QPoint
        self.x_pos += int(dx)
        self.y_pos += int(dy)
        self.position = QPoint(self.x_pos, self.y_pos)


class Planets(QWidget):
    def __init__(self):
        super().__init__()
        self.asteroids = []
        self.initUI()  # Метод для настройки интерфейса
        self.start_time = time.time()
        self.is_paused = False  # Переменная для отслеживания состояния паузы
        self.pause_start_time = 0  # Время начала паузы
        self.total_pause_time = 0 # Общее время паузы
        self.elapsed_time = 0 # Время анимации (работающей)

        with open('solar_system.json', 'r') as f:
            self.planets = json.load(f)

    def initUI(self):
        # Создаем поле для отрисовки планет (основное поле)
        self.setWindowTitle("Planets")
        self.setGeometry(200, 0, 1000, 1000)
        self.timer = QTimer()
        self.timer.timeout.connect(self.update)
        self.timer.start(10)

        # Создаем поля для ввода параметров астероида
        self.data_input = QLineEdit(self)
        self.data_input.setPlaceholderText("Radius, Direction (degrees), Speed")
        self.data_input.setGeometry(10, 10, 250, 40)
        # Стилизируем поле ввода
        self.data_input.setStyleSheet("""
            QLineEdit {
                background-color: #000000; /* Цвет фона */
                color: white; /* Цвет текста */
            }""")
        # Скрываем поля ввода изначально
        self.data_input.hide()

        # Создаем кнопку для паузы
        self.pause_button = QPushButton('Pause', self)
        self.pause_button.setGeometry(900, 10, 90, 40)
        self.pause_button.clicked.connect(self.toggle_pause)
        # Стилизируем кнопку паузы
        self.pause_button.setStyleSheet("""
            QPushButton {
                color: white;  /* Белый текст */
                border: none;  /* Без границы */
                border-radius: 20px; /* Закругленные углы */
            }
            QPushButton:hover {
                background-color: #007ba7; /* Цвет при наведении */
            }""")

    def paintEvent(self, event):  # Основной метод отрисовки
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        painter.setPen(QColor(0, 0, 0))
        painter.setBrush(QColor(0, 0, 0))
        painter.drawRect(0, 0, 1000, 1000)

        if not self.is_paused:
            self.elapsed_time = abs(time.time() - self.start_time) - self.total_pause_time

        # Функция для отрисовки объектов
        def coordinates(c_x, c_y, r1, r2, speed_coefficient, angele):
            angle_c = (self.elapsed_time * speed_coefficient * 360 / (2 * math.pi)) + angele
            x = c_x + r1 * math.cos(math.radians(angle_c))
            y = c_y + r1 * math.sin(math.radians(angle_c))
            painter.drawEllipse(QPoint(int(x), int(y)), r2, r2)
            return int(x), int(y)

        sun = True
        r = 0
        planets_coords = []

        # Рисуем планеты и их спутники
        for i in range(len(self.planets)):
            painter.setPen(QColor(*self.planets[i]['color'], self.planets[i]['density_coefficient']))
            painter.setBrush(QColor(*self.planets[i]['color'], self.planets[i]['density_coefficient']))
            if sun:
                coord = coordinates(500, 400, r, self.planets[i]['radius'],
                                    self.planets[i]['speed_coefficient'], self.planets[i]['rotation_angle'])
                sun = False
                planets_coords.append(coord)
                continue

            r += self.planets[i-1]['radius'] + 5 + self.planets[i]['radius']
            coord = coordinates(500, 400, r, self.planets[i]['radius'],
                                self.planets[i]['speed_coefficient'], self.planets[i]['rotation_angle'])
            planets_coords.append(coord)

            if 'satellite' in self.planets[i].keys():
                for satellite in self.planets[i]['satellite']:
                    painter.setPen(QColor(*satellite['color'], satellite['density_coefficient']))
                    painter.setBrush(QColor(*satellite['color'], satellite['density_coefficient']))
                    coordinates(coord[0], coord[1], self.planets[i]['radius']+10, satellite['radius'],
                                satellite['speed_coefficient'], satellite['rotation_angle'])

            if self.planets[i]['name'] == 'Saturn':
                painter.setBrush(QColor(*self.planets[i]['color'], 16))
                painter.drawEllipse(QPoint(coord[0], coord[1]), self.planets[i]['radius'] + 10,
                                    self.planets[i]['radius'] + 10)
                painter.drawEllipse(QPoint(coord[0], coord[1]), self.planets[i]['radius'] + 15,
                                    self.planets[i]['radius'] + 15)

        # Рисуем астероиды
        for asteroid in self.asteroids:
            for i in range(len(self.planets)):
                # Проверяем коллизии астероидов с планетами
                if self.check_collision(planets_coords, self.planets[i], asteroid, i):
                    self.planets[i]['radius'] += asteroid.radius // 2  # Увеличиваем радиус планеты
                    self.asteroids.remove(asteroid)  # Удаляем астероид из списка
                else:
                    painter.setBrush(QColor(255, 255, 255))
                    painter.drawEllipse(asteroid.position.x() - asteroid.radius,
                                        asteroid.position.y() - asteroid.radius,
                                        asteroid.radius * 2,
                                        asteroid.radius * 2)

            if not self.is_paused:
                asteroid.update_position()  # Обновляем позицию астероида

    # Функция для проверки коллизий
    def check_collision(self, planets_coords, planet, asteroid, i):
        is_collision = (abs(asteroid.x_pos - planets_coords[i][0]) < asteroid.radius + planet['radius']) and \
                       (abs(asteroid.y_pos - planets_coords[i][1]) < asteroid.radius + planet['radius'])
        return is_collision

    # Функция для задания координат и параметров астероидов
    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            # Показываем поля ввода при клике мыши
            self.data_input.show()
            self.asteroid_position = QPoint(event.x(), event.y())
            # Подключаем событие нажатия клавиши Enter
            self.data_input.returnPressed.connect(self.create_asteroid)

    # Функция для создания астероидов
    def create_asteroid(self):
        try:
            radius = int(self.data_input.text().split(",")[0])
            direction = int(self.data_input.text().split(",")[1])
            speed = int(self.data_input.text().split(",")[2])

            # Создаем астероид в позиции клика мыши
            asteroid = Asteroid(self.asteroid_position, radius, direction, speed)  # Создаем астероид
            self.asteroids.append(asteroid)  # Добавляем астероид в список

            # Скрываем и очищаем поля ввода после создания астероида
            self.data_input.hide()
            self.data_input.clear()

        except ValueError:
            print("Введите корректные значения")
        except IndexError:
            print("Введите корректные значения")

    # Функция для постановки анимации на паузу
    def toggle_pause(self):
        self.is_paused = not self.is_paused  # Переключаем состояние паузы
        if self.is_paused:
            self.pause_button.setText("Resume")  # Меняем текст кнопки на 'Resume'
            self.pause_start_time = time.time()  # Запоминаем время начала паузы
        else:
            self.pause_button.setText("Pause")  # Меняем текст кнопки на 'Pause'
            self.total_pause_time += time.time() - self.pause_start_time  # Обновляем общее время паузы


app = QApplication(sys.argv)
window = Planets()
window.show()
sys.exit(app.exec_())