from abc import ABC, abstractmethod
from math import sqrt, sin, radians, pi, cos, acos, tan, degrees
import matplotlib.pyplot as plt
import numpy as np

class InvalidShapeError(Exception):
    """Исключение для неверных параметров фигуры"""
    pass

class Shapes(ABC):
    """
    Абстрактный базовый класс для геометрических фигур

    Атрибуты:
        n_angles - Количество углов у фигуры
        angles - Список значений углов в градусах
        sides - Список длин сторон
    """
    def __init__(self, n_angles, angles, sides):
        # _ перед переменной означает условный private
        self._n_angles = n_angles
        self.angles = angles
        self.sides = sides

    @property
    def n_angles(self):
        return self._n_angles

    @property
    def angles(self):
        return self._angles

    @angles.setter
    def angles(self, angles):
        """
        - Углы должны быть в виде списка
        - Количество углов должно соответствовать n_angles
        - Каждый угол должен быть положительным и меньше 360 градусов
        """

        if len(angles) != self.n_angles:
            raise InvalidShapeError(f"Количество углов должно быть {self.n_angles}")
        for angle in angles:
            if not (0 < angle < 360):
                raise InvalidShapeError("Каждый угол должен быть положительным и меньше 360 градусов")
        self._angles = angles

    def get_perimetr(self):
        if self.n_angles == 0:
            return 2 * pi * self.sides[0]  # длина окружности
        return sum(self.sides)
    
    @abstractmethod
    def get_info(self):
        info = f"Углы: {self.angles}\n"
        info += f"Стороны: {self.sides}\n"
        info += f"Периметр: {self.get_perimetr():.2f}\n"
        print(info)

    @property
    def sides(self):
        return self._sides

    @sides.setter
    def sides(self, sides):
        """
        - Стороны должны быть в виде списка
        - Для круга (n_angles == 0) должна быть только одна сторона (радиус)
        - Для других фигур количество сторон должно соответствовать n_angles
        - Длины сторон должны быть положительными
        """
        try:
            if not isinstance(sides, list):
                raise InvalidShapeError("Стороны должны быть в виде списка")
            if self.n_angles == 0:
                if len(sides) != 1:
                    raise InvalidShapeError("У круга должна быть только одна сторона (радиус)")
            else:
                if len(sides) != self.n_angles:
                    raise InvalidShapeError(f"Количество сторон должно быть {self.n_angles}")
            for side in sides:
                if side <= 0:
                    raise InvalidShapeError("Длины сторон должны быть положительными")
            self._sides = sides
        except InvalidShapeError as e:
            print(f"Ошибка при установке сторон: {e}")


class Circle(Shapes): 
    """
        Атрибуты:
            radius (float): Радиус круга
    """
    def __init__(self, radius):
        super().__init__(0, [], [radius]) # конструктор базового класса
        if radius <= 0: 
            raise InvalidShapeError("Радиус должен быть положительным")
        self.name = 'круг'
    
    # площадь
    def get_sq(self):
        radius = self.sides[0]
        return pi * radius ** 2
    
    def set_sides(self, sides):
        # Устанавливает новый радиус круга с проверкой
        if len(sides) != 1:
            raise InvalidShapeError("У круга должна быть только одна сторона (радиус)")
        if sides[0] <= 0:   
            raise InvalidShapeError("Радиус должен быть положительным")
        self._sides = sides  # Прямое присваивание, так как сеттер уже проверял

    def set_angles(self, angles):
        # Пытаться установить углы для круга приведёт к ошибке, так как у круга нет углов
        if angles:
            raise InvalidShapeError("У круга нет углов")
    
    def get_info(self): # overdrive
        info = f"Название: {self.name}\n"
        info += f"Радиус: {self.sides[0]}\n"
        info += f"Периметр (длина окружности): {self.get_perimetr():.2f}\n"
        info += f"Площадь: {self.get_sq():.2f}\n"
        print(info)
        
        
class Triangle(Shapes):
    """
    Атрибуты:
        angles (list): Список из трех углов в градусах
        sides (list): Список из трех длин сторон
    """
    def __init__(self, angles, sides):
        super().__init__(3, angles, sides)  # вызов конструктора базового класса
        self.angles = angles  # Установка углов через сеттер
        self.sides = sides  # Установка сторон через сеттер
        if not self._validate_angles():
            raise InvalidShapeError("Сумма углов треугольника должна быть 180 градусов")
        if not self._validate_sides():
            raise InvalidShapeError("Стороны не удовлетворяют неравенству треугольника")
        self.name = "Треугольник"

    
    # Проверка, что сумма углов треугольника равна 180 градусов
    def _validate_angles(self):
        total = sum(self.angles)
        if abs(total - 180) < 1e-5:
            return True
        elif self.angles.count(0) == 1:
            # Восстанавливаем недостающий угол
            missing = 180 - sum(angle for angle in self.angles if angle > 0)
            if 0 < missing < 180:
                missing_index = self.angles.index(0)
                self._angles = self.angles.copy()
                self._angles[missing_index] = missing
                return True
        return False

    # проверка неравенство треугольника для длин сторон
    def _validate_sides(self):
        a, b, c = self.sides
        return a + b > c and a + c > b and b + c > a
    
    # Модифицированный метод get_sq с тремя формулами
    def get_sq(self):
        # Проверяем, какие данные у нас есть для выбора подходящей формулы
        a, b, c = self.sides
        A, B, C = self.angles

        # 1. Формула Герона (если известны все стороны)
        if all(self.sides):
            s = self.get_perimetr() / 2
            try:
                area = sqrt(s * (s - a) * (s - b) * (s - c))
                return area
            except ValueError:
                print("Не удалось вычислить площадь по формуле Герона.")
        
        # 2. Площадь через две стороны и угол между ними
        if a > 0 and b > 0 and C > 0:
            area = 0.5 * a * b * sin(radians(C))
            return area
        if a > 0 and c > 0 and B > 0:
            area = 0.5 * a * c * sin(radians(B))
            return area
        if b > 0 and c > 0 and A > 0:
            area = 0.5 * b * c * sin(radians(A))
            return area
        
        # 3. Площадь через основание и высоту
        # Предположим, что сторона 'a' является основанием, а высоту необходимо вычислить
        if a > 0 and B > 0 and C > 0:
            h = b * sin(radians(A))
            area = 0.5 * a * h
            return area
        
        print("Не удалось вычислить площадь треугольника по имеющимся данным.")
        return None

    def set_angles(self, angles):
        if len(angles) != 3:
            raise InvalidShapeError("Треугольник должен иметь 3 угла")
        for angle in angles:
            if not (0 < angle < 180):
                raise InvalidShapeError("Каждый угол треугольника должен быть положительным и меньше 180 градусов")
        if abs(sum(angles) - 180) > 1e-5:
            raise InvalidShapeError("Сумма углов треугольника должна быть 180 градусов")
        self._angles = angles  # Прямое присваивание, так как сеттер уже проверял
        
    
    def set_sides(self, sides):
        if len(sides) != 3:
            raise InvalidShapeError("Треугольник должен иметь 3 стороны.")
        a, b, c = sides
        if a + b <= c or a + c <= b or b + c <= a:
            raise InvalidShapeError("Стороны не удовлетворяют неравенству треугольника.")
        self._sides = sides  
    
    def get_info(self): #override
        info = f"Название: {self.name}\n"
        info += f"Углы (градусы): {self.angles}\n"
        info += f"Стороны: {self.sides}\n"
        info += f"Периметр: {self.get_perimetr():.2f}\n"
        area = self.get_sq()
        if area is not None:
            info += f"Площадь: {area:.2f}\n"
        else:
            info += "Площадь: Не вычислима\n"
        print(info)

    def draw(self):
        x = [0]
        y = [0]
        for i in range(3):
            angle_sum = sum(self.angles[:i+1])
            x.append(x[-1] + self.sides[i] * cos(radians(angle_sum)))
            y.append(y[-1] + self.sides[i] * sin(radians(angle_sum)))
        x.append(0)
        y.append(0)
        plt.plot(x, y, marker='o')
        plt.title(self.name)
        plt.gca().set_aspect('equal', adjustable='box')
        plt.show()
        
        
class Quadrangle(Shapes):
    """    
    Атрибуты:
        angles (list): Список из четырёх углов в градусах
        sides (list): Список из четырёх длин сторон
    """
    def __init__(self, angles, sides):
        super().__init__(4, angles, sides)
        self._sides = sides 
        self._angles = angles
        if not self._validate_angles():
            raise InvalidShapeError("Сумма углов четырёхугольника должна быть 360 градусов")
        if not self._validate_sides():
            raise InvalidShapeError("Некорректные длины сторон для четырёхугольника")
        self.name = "Четырёхугольник"

    def _validate_angles(self):
        total = sum(self.angles)
        if abs(total - 360) < 1e-5:
            return True
        elif self.angles.count(0) == 1:
            # Восстанавливаем недостающий угол
            missing = 360 - sum(angle for angle in self.angles if angle > 0)
            if 0 < missing < 360:
                missing_index = self.angles.index(0)
                self._angles = self.angles.copy()
                self._angles[missing_index] = missing
                return True
        return False

    def _validate_sides(self):
        return all(side > 0 for side in self.sides)
    

    def get_sq(self):
        angles = self.angles
        sides = self.sides
        a, b, c, d = sides

        # Проверка на квадрат
        if all(angle == 90 for angle in angles) and len(set(sides)) == 1:
            return sides[0] ** 2

        # Проверка на прямоугольник
        if all(angle == 90 for angle in angles) and len(set([sides[0], sides[2]])) == 1 and len(set([sides[1], sides[3]])) == 1:
            return sides[0] * sides[1]

        # Проверка на ромб
        if len(set(sides)) == 1 and len(set(angles)) == 2:
            angle = angles[0]
            area = sides[0] ** 2 * sin(radians(angle))
            return area

        # Проверка на параллелограмм
        if angles[0] == angles[2] and angles[1] == angles[3] and sides[0] == sides[2] and sides[1] == sides[3]:
            base = sides[0]
            side = sides[1]
            angle = angles[1]
            height = side * sin(radians(angle))
            return base * height

        # Проверка на трапецию (одна пара сторон параллельна)
        if self.is_trapezoid():
            # Предположим, что a и c — параллельные стороны
            h = self.get_trapezoid_height()
            area = 0.5 * (a + c) * h
            return area

        # Если фигура произвольная, используем формулу через диагонали и угол между ними
        try:
            d1, d2, angle_between_diagonals = self.get_diagonals_and_angle()
            area = 0.5 * d1 * d2 * sin(radians(angle_between_diagonals))
            return area
        except:
            print("Не удалось вычислить площадь произвольного четырёхугольника")
            return None

    # Метод для проверки, является ли четырёхугольник трапецией
    def is_trapezoid(self):
        # Для упрощения, проверим параллельность сторон по равенству противоположных углов
        return self.angles[0] == self.angles[2] or self.angles[1] == self.angles[3]

    # Метод для вычисления высоты трапеции
    def get_trapezoid_height(self):
        # Предположим, что стороны a и c — основания
        a, b, c, d = self.sides
        angle = self.angles[1]
        h = b * sin(radians(angle))
        return h

    def get_diagonals_and_angle(self):
        x = [0]
        y = [0]
        for i in range(4):
            x.append(x[-1] + self.sides[i] * cos(radians(sum(self.angles[:i + 1]))))
            y.append(y[-1] + self.sides[i] * sin(radians(sum(self.angles[:i + 1]))))
        # Вычисляем длины диагоналей
        d1 = sqrt((x[2] - x[0])**2 + (y[2] - y[0])**2)
        d2 = sqrt((x[3] - x[1])**2 + (y[3] - y[1])**2)
        # Вычисляем угол между диагоналями
        vector_1 = (x[2] - x[0], y[2] - y[0])
        vector_2 = (x[3] - x[1], y[3] - y[1])
        dot_product = vector_1[0] * vector_2[0] + vector_1[1] * vector_2[1]
        magnitude_1 = sqrt(vector_1[0]**2 + vector_1[1]**2)
        magnitude_2 = sqrt(vector_2[0]**2 + vector_2[1]**2)
        angle = degrees(acos(dot_product / (magnitude_1 * magnitude_2)))
        return d1, d2, angle

    def set_angles(self, angles):
        if len(angles) != 4:
            raise InvalidShapeError("Четырёхугольник должен иметь 4 угла")
        positive_angles = [angle for angle in angles if angle > 0]
        if len(positive_angles) == 4:
            if abs(sum(angles) - 360) > 1e-5:
                raise InvalidShapeError("Сумма углов четырёхугольника должна быть 360 градусов")
            self._angles = angles
        elif len(positive_angles) == 3:
            missing = 360 - sum(positive_angles)
            if not (0 < missing < 360):
                raise InvalidShapeError("Недостающий угол некорректен")
            angles = angles.copy()
            missing_index = angles.index(0)
            angles[missing_index] = missing
            self._angles = angles
        else:
            raise InvalidShapeError("Четырёхугольник должен иметь 3 или 4 заданных угла")

    def set_sides(self, sides):
        if len(sides) != 4:
            raise InvalidShapeError("Четырёхугольник должен иметь 4 стороны")
        if not all(side > 0 for side in sides):
            raise InvalidShapeError("Длины сторон должны быть положительными")
        self._sides = sides
    
    def draw(self):
        x = [0]
        y = [0]
        for i in range(4):
            x.append(x[-1] + self.sides[i] * cos(radians(sum(self.angles[:i + 1]))))
            y.append(y[-1] + self.sides[i] * sin(radians(sum(self.angles[:i + 1]))))
        x.append(0)
        y.append(0)
        plt.plot(x, y, marker='o')
        plt.title(self.name)
        plt.gca().set_aspect('equal', adjustable='box')
        plt.show()

    def get_info(self):
        info = f"Название: {self.name}\n"
        info += f"Углы (градусы): {self.angles}\n"
        info += f"Стороны: {self.sides}\n"
        info += f"Периметр: {self.get_perimetr():.2f}\n"
        area = self.get_sq()
        if area is not None:
            info += f"Площадь: {area:.2f}\n"
        else:
            info += "Площадь: Не вычислима\n"
        print(info)



class Nangle(Shapes):
    """
    N-угольник (n >= 5).
    Атрибуты:
        n (int): Количество углов (n >= 5).
        angles (list): Список углов (должен быть полностью задан или полностью стороны)
        sides (list): Список длин сторон (должен быть полностью задан или полностью углы)
    """
    def __init__(self, n, angles=None, sides=None):
        if n < 5:
            raise InvalidShapeError("Используйте специализированные классы для фигур с количеством углов меньше 5")
        
        if angles is None and sides is None:
            raise InvalidShapeError("Должен быть указан хотя бы один из параметров: углы или стороны")
        
        # Устанавливаем значения по умолчанию, если ничего не передано
        angles = angles if angles else [0] * n
        sides = sides if sides else [0] * n

        super().__init__(n, angles, sides)

        # Дополнительная проверка корректности углов или сторон
        if angles and all(angle > 0 for angle in angles):
            if len(angles) != n:
                raise InvalidShapeError(f"N-угольник должен иметь {n} углов")
            if abs(sum(angles) - (n - 2) * 180) > 1e-5:
                raise InvalidShapeError(f"Сумма углов {n}-угольника должна быть {(n - 2) * 180} градусов")
        
        if sides and all(side > 0 for side in sides):
            if len(sides) != n:
                raise InvalidShapeError(f"N-угольник должен иметь {n} сторон")
            for side in sides:
                if side <= 0:
                    raise InvalidShapeError("Длины сторон должны быть положительными")
        
        self.name = f"{n}-угольник"

    def get_sq(self):
        # Реализуем площадь для правильного многоугольника
        if all(side == self.sides[0] for side in self.sides) and all(angle == self.angles[0] for angle in self.angles):
            n = self.n_angles
            a = self.sides[0]
            area = (n * a ** 2) / (4 * tan(pi / n))
            return area
        else:
            print("Площадь для произвольного N-угольника не реализована")
            return None

    def set_angles(self, angles):
        if self.n_angles != len(angles):
            raise InvalidShapeError(f"N-угольник должен иметь {self.n_angles} углов")
        if abs(sum(angles) - (self.n_angles - 2) * 180) > 1e-5:
            raise InvalidShapeError(f"Сумма углов должна быть {(self.n_angles - 2) * 180} градусов")
        for angle in angles:
            if not (0 < angle < 360):
                raise InvalidShapeError("Каждый угол должен быть положительным и меньше 360 градусов")
        self._angles = angles
        self._sides = [0]*self.n_angles  # Удаляем стороны, если были

    def set_sides(self, sides):
        if self.n_angles != len(sides):
            raise InvalidShapeError(f"N-угольник должен иметь {self.n_angles} сторон")
        for side in sides:
            if side <= 0:
                raise InvalidShapeError("Длины сторон должны быть положительными")
        self._sides = sides
        self._angles = [0]*self.n_angles 

    def get_info(self):
        info = f"Название: {self.name}\n"
        if self.angles and all(angle > 0 for angle in self.angles):
            info += f"Углы (градусы): {self.angles}\n"
        if self.sides and all(side > 0 for side in self.sides):
            info += f"Стороны: {self.sides}\n"
            info += f"Периметр: {self.get_perimetr():.2f}\n"
        area = self.get_sq()
        if area is not None:
            info += f"Площадь: {area:.2f}\n"
        else:
            info += "Площадь: Не вычислима\n"
        print(info)

if __name__ == "__main__":
    # Создание круга
    try:
        circle = Circle(radius=5)
        circle.get_info()
    except InvalidShapeError as e:
        print(f"Ошибка: {e}")
    print("-" * 40)

    # Создание треугольника с известными сторонами
    try:
        triangle = Triangle(angles=[60, 60, 60], sides=[10, 10, 10])
        triangle.get_info()
    except InvalidShapeError as e:
        print(f"Ошибка: {e}")
    print("-" * 40)

    # Создание треугольника с двумя сторонами и углом между ними
    try:
        triangle = Triangle(angles=[0, 45, 135], sides=[5, 7, 0])
        triangle.set_angles([45, 90, 45])
        triangle.set_sides([5, 7, 8.6])
        triangle.get_info()
    except InvalidShapeError as e:
        print(f"Ошибка при создании треугольника: {e}")

    # Работает
    try:
        triangle = Triangle(angles=[45, 90, 45], sides=[5, 7, 8.6])
        triangle.get_info()
    except InvalidShapeError as e:
        print(f"Ошибка при создании треугольника: {e}")


    # Создание прямоугольника
    try:
        rectangle = Quadrangle(angles=[90, 90, 90, 90], sides=[5, 10, 5, 10])
        rectangle.get_info()
    except InvalidShapeError as e:
        print(f"Ошибка: {e}")
    print("-" * 40)

    # Создание трапеции
    try:
        trapezoid = Quadrangle(angles=[90, 60, 90, 120], sides=[10, 5, 6, 5])
        trapezoid.get_info()
    except InvalidShapeError as e:
        print(f"Ошибка: {e}")
    print("-" * 40)

    # Создание параллелограмма
    try:
        parallelogram = Quadrangle(angles=[60, 120, 60, 120], sides=[8, 5, 8, 5])
        parallelogram.get_info()
    except InvalidShapeError as e:
        print(f"Ошибка: {e}")
    print("-" * 40)

    # Создание ромба
    try:
        rhombus = Quadrangle(angles=[60, 120, 60, 120], sides=[7, 7, 7, 7])
        rhombus.get_info()
    except InvalidShapeError as e:
        print(f"Ошибка: {e}")
    print("-" * 40)

    # Создание правильного пятиугольника
    try:
        pentagon = Nangle(n=5, angles=[108, 108, 108, 108, 108], sides=[6, 6, 6, 6, 6])
        pentagon.get_info()
    except InvalidShapeError as e:
        print(f"Ошибка: {e}")

    # Создание неправильного пятиугольника
    try:
        irregular_pentagon = Nangle(n=5, angles=[100, 110, 90, 30, 30], sides=[0]*5)
        irregular_pentagon.get_info()
    except InvalidShapeError as e:
        print(f"Ошибка: {e}")

    # Пример с ошибкой: неверная сумма углов треугольника
    try:
        invalid_triangle = Triangle(angles=[90, 90, 90], sides=[10, 10, 10])
        invalid_triangle.get_info()
    except InvalidShapeError as e:
        print(f"Ошибка: {e}")
    print("-" * 40)
    
    try:
        # Создание четырёхугольника
        quadrangle = Quadrangle(angles=[90, 90, 90, 90], sides=[5, 10, 5, 10])
        quadrangle.get_info()
        quadrangle.draw()
    except InvalidShapeError as e:
        print(f"Ошибка при создании четырёхугольника: {e}")
    
    print("-" * 40)

    try:
        # Создание четырёхугольника с некорректными сторонами
        invalid_quadrangle = Quadrangle(angles=[90, 90, 90, 90], sides=[-5, 10, 5, 10])
        invalid_quadrangle.get_info()
    except InvalidShapeError as e:
        print(f"Ошибка при создании четырёхугольника: {e}")
    
    print("-" * 40)

    try:
        # Создание четырёхугольника с углом, который должен быть восстановлен
        incomplete_quadrangle = Quadrangle(angles=[90, 90, 90, 0], sides=[5, 10, 5, 10])
        incomplete_quadrangle.get_info()
    except InvalidShapeError as e:
        print(f"Ошибка при создании четырёхугольника: {e}")

    try:
        # Создание произвольного четырёхугольника и демонстрация нахождения диагоналей и угла между ними
        arbitrary_quadrangle = Quadrangle(angles=[70, 110, 80, 100], sides=[7, 8, 6, 9])
        arbitrary_quadrangle.get_info()
        d1, d2, angle = arbitrary_quadrangle.get_diagonals_and_angle()
        print(f"Диагонали: {d1:.2f}, {d2:.2f}\nУгол между диагоналями: {angle:.2f} градусов")
    except InvalidShapeError as e:
        print(f"Ошибка при создании четырёхугольника: {e}")
