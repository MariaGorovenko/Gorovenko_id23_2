from PyQt5.QtWidgets import QApplication, QWidget, QPushButton
from PyQt5.QtGui import QPainter, QColor
from PyQt5.QtCore import QTimer, QPoint, QCoreApplication
import sys
import math
import time  # импортируем библиотеку для работы со временем


class CircleWindow(QWidget):
    def __init__(self, speed_coefficient=1, direction_coefficient=1):
        super().__init__()
        self.initUI()  # метод для настройки интерфейса
        self.start_time = time.time()  # запоминаем время начала анимации
        self.speed_coefficient = speed_coefficient  # коэффициент скорости вращения
        self.direction_coefficient = direction_coefficient  # коэффициент направления вращения
        # (поумолчанию по часовой стрелке)

        # Добавляем кнопку, при нажатии которой завершается приложение.
        button = QPushButton('Complete the application', self)
        button.clicked.connect(QCoreApplication.instance().quit)
        button.resize(button.sizeHint())
        button.move(10, 10)

    def initUI(self):  # метод для установки параметров окна
        self.setWindowTitle("Circle Window")
        self.setGeometry(100, 100, 600, 600)
        self.timer = QTimer()  # используется для периодического обновления окна
        self.timer.timeout.connect(self.update)  # подключаем сигнал timeout таймера к слоту update,
        # который вызывает перерисовку окна
        self.timer.start(25)  # перезапускаем каждые 50 миллисекунд

    def paintEvent(self, event):  # автоматически вызывается при необходимости перерисовки окна (при вызове update)
        painter = QPainter(self)  # объект QPainter используется для рисования на виджете
        painter.setPen(QColor(255, 255, 255))  # устанавливаем цвет пера (белый цвет)
        painter.setBrush(QColor(255, 255, 255))  # устанавливаем цвет кисти (белый цвет)

        # Рисуем фон, заполняя прямоугольник размерами 600x600 пикселей
        painter.drawRect(0, 0, 600, 600)

        # Рисуем окружность
        painter.setPen(QColor(0, 0, 0))  # меняем цвет пера на черный
        painter.drawEllipse(QPoint(300, 300), 200, 200)  # рисуем черную окружность (круг) с центром в точке (300, 300)
        # и радиусом 200 пикселей

        # Рисуем движущуюся точку
        elapsed_time = abs(time.time() - self.start_time) * self.direction_coefficient  # вычисляем прошедшее время
        angle = elapsed_time * self.speed_coefficient * 360 / 6.28  # вычисляем угол для перемещения
        # точки по круговой траектории
        x = 300 + 200 * math.cos(math.radians(angle))
        y = 300 + 200 * math.sin(math.radians(angle))
        painter.drawEllipse(QPoint(int(x), int(y)), 10, 10)  # рисуем небольшую окружность (точку)


app = QApplication(sys.argv)
window = CircleWindow()
window.show()
sys.exit(app.exec_())  # app.exec_() позволяет приложению получать события и обрабатывать их до тех пор,
# пока оно не будет закрыто
