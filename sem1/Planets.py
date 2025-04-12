from PyQt5.QtWidgets import QApplication, QWidget
from PyQt5.QtGui import QPainter, QColor
from PyQt5.QtCore import QTimer, QPoint
import sys
import math
import random
import time  # Импортируем библиотеку для работы со временем


class Planets(QWidget):
    def __init__(self):
        super().__init__()
        self.initUI()  # метод для настройки интерфейса
        self.start_time = time.time()  # запоминаем время начала анимации
        self.initial_angles = [random.uniform(0, 360) for _ in range(8)]

    def initUI(self):  # метод для установки параметров окна
        self.setWindowTitle("Planets")
        self.setGeometry(200, 0, 1000, 1000)
        self.timer = QTimer()  # используется для периодического обновления окна
        self.timer.timeout.connect(self.update)  # подключаем сигнал timeout таймера к слоту update,
        # который вызывает перерисовку окна
        self.timer.start(50)  # перезапускаем каждые 50 миллисекунд

    def paintEvent(self, event):  # автоматически вызывается при необходимости перерисовки окна (при вызове update)
        painter = QPainter(self)  # объект QPainter используется для рисования на виджете
        painter.setRenderHint(QPainter.Antialiasing)  # включаем сглаживание (антиалиасинг)
        painter.setPen(QColor(0, 0, 0))  # устанавливаем цвет пера (черный цвет)
        painter.setBrush(QColor(0, 0, 0))  # устанавливаем цвет кисти (черный цвет)

        # Рисуем фон, заполняя прямоугольник размерами 1000x1000 пикселей
        painter.drawRect(0, 0, 1000, 1000)

        # Рисуем Солнце
        painter.setPen(QColor(255, 255, 0, 150))  # меняем цвет пера на желтый
        painter.setBrush(QColor(255, 255, 0, 150))  # устанавливаем цвет кисти (желтый цвет)
        painter.drawEllipse(QPoint(500, 400), 60, 60)  # рисуем желтую окружность (круг) с центром в точке (500, 400)
        # и радиусом 60 пикселей

        elapsed_time = abs(time.time() - self.start_time)  # вычисляем прошедшее время
        r = 70  # радиус орбиты первой планеты
        planets_speed = [1.97, 1.85, 1.8, 1.74, 1.63, 1.597, 1.568, 1.554]
        planets_color = [(194, 202, 175), (255, 165, 0), (70, 130, 180), (195, 88, 23), (255, 197, 148), (255, 191, 85),
                         (0, 191, 255), (30, 144, 255)]

        def coordinates(c_x, c_y, r1, r2, speed=0, angele=0):
            # c_x - x координата центра
            # c_y - y координата центра
            # r1 - радиус орбиты относительно центра
            # r2 - радиус планеты
            angle_c = (elapsed_time * (speed_coefficient + speed) * 360 / (2 * math.pi)) + angele  # вычисляем угол
            # для перемещения планеты по круговой траектории
            x = c_x + r1 * math.cos(math.radians(angle_c))
            y = c_y + r1 * math.sin(math.radians(angle_c))
            painter.drawEllipse(QPoint(int(x), int(y)), r2, r2)  # рисуем планету
            return int(x), int(y)

        for i, speed_coefficient in enumerate(planets_speed):
            painter.setPen(QColor(planets_color[i][0], planets_color[i][1], planets_color[i][2], 150))
            painter.setBrush(QColor(planets_color[i][0], planets_color[i][1], planets_color[i][2], 150))
            coord = coordinates(500, 400, r, 20, angele=self.initial_angles[i])

            if i >= 2:
                # Рисуем спутник
                coordinates(coord[0], coord[1], 30, 3, speed=3)

                if i == 4:
                    # Рисуем второй спутник Юпитера
                    coordinates(coord[0], coord[1], 30, 3, speed=2, angele=self.initial_angles[i])

                if i == 5:
                    # Рисуем кольца у Сатурна
                    painter.setBrush(QColor(planets_color[i][0], planets_color[i][1], planets_color[i][2], 16))
                    painter.drawEllipse(QPoint(coord[0], coord[1]), 30, 30)
                    painter.drawEllipse(QPoint(coord[0], coord[1]), 35, 35)

            r += 20


app = QApplication(sys.argv)
window = Planets()
window.show()
sys.exit(app.exec_())  # app.exec_() позволяет приложению получать события и обрабатывать их до тех пор,
# пока оно не будет закрыто
