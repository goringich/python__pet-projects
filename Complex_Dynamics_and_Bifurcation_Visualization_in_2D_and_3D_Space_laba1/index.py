import matplotlib.pyplot as plt
import numpy as np

# Задание 1: Функция для расчета следующей точки в 2D
def point_2d(x, y, a, b):
  x1, y1 = 1 - a * x**2 + y, b * x
  return x1, y1

# Задание 2: Параметры для 2D траекторий
para_2d = [(0.9, -0.3), (1.27, 0.03), (1.42, 0.26)]

# Задание 2: Функция для расчета 2D траекторий
def route_2D(x, y, a, b, step):
  route_x, route_y = [x], [y]
  for i in range(step):
    x, y = point_2d(x, y, a, b)
    route_x.append(x)
    route_y.append(y)
  return route_x, route_y


# Задание 3: Построение 2D траекторий
def plot_2d_trajectories(initial_x, initial_y, parameters, steps=1000):
  route_x_2d, route_y_2d = [], []
  for a, b in parameters:
    route_x, route_y = route_2D(initial_x, initial_y, a, b, steps)
    route_x_2d.append(route_x)
    route_y_2d.append(route_y)

  figure, ax = plt.subplots(figsize=(8, 8))
  colors = ["b", "g", "r"]
  n = len(route_x_2d)
  for i in range(len(parameters)):
    ax.scatter(route_x_2d[i], route_y_2d[i], c=colors[i], s=5 * (n - i),
      label=f"Траектория №{i+1} (a={parameters[i][0]}, b={parameters[i][1]})")
  ax.set_xlabel("x")
  ax.set_ylabel("y")
  ax.set_title("2D Trajectories")
  ax.legend()
  plt.show()

# Задание 4: Функция для расчета следующей точки в 3D
def point_3d(x, y, z, B, M1, M2):
  x1, y1, z1 = y, z, M1 + B * x + M2 * y - z**2.0
  return x1, y1, z1

# Задание 4: Функция для расчета 3D траекторий
def route_3D(x, y, z, B, M1, M2, step):
  route_x, route_y, route_z = [x], [y], [z]
  for i in range(step):
    x, y, z = point_3d(x, y, z, B, M1, M2)
    route_x.append(x)
    route_y.append(y)
    route_z.append(z)
  return route_x, route_y, route_z


# Задание 4: Построение 3D траекторий
def plot_3d_trajectories(initial_x, initial_y, initial_z, parameters, B, steps=1000):
  route_x_3d, route_y_3d, route_z_3d = [], [], []
  for M2, M1 in parameters:
    route_x, route_y, route_z = route_3D(initial_x, initial_y, initial_z, B, M1, M2, steps)
    route_x_3d.append(route_x)
    route_y_3d.append(route_y)
    route_z_3d.append(route_z)

  fig = plt.figure(figsize=(8, 8))
  ax = fig.add_subplot(111, projection='3d')
  colors = ["b", "g", "r"]
  n = len(route_x_3d)
  for i in range(len(parameters)):
    ax.scatter(route_x_3d[i], route_y_3d[i], route_z_3d[i], c=colors[i], s=5 * (n - i), 
               label=f"Траектория №{i+1} (M1={parameters[i][1]}, M2={parameters[i][0]})")
  ax.set_xlabel("x")
  ax.set_ylabel("y")
  ax.set_zlabel("z")
  ax.set_title("3D Trajectories")
  ax.legend()
  plt.show()

# Параметры для построения графиков
parameters = [(0.9, -0.3), (1.27, 0.03), (1.42, 0.26)]
plot_2d_trajectories(0.1, 0.1, parameters)

B = 0.7
para_3d = [(0.06, 0.06), (-0.5, 0.03), (-0.28, 0.23)]
plot_3d_trajectories(0.1, 0.1, 0.1, para_3d, B)

# Задание 5: Логистическое отображение и бифуркационное дерево
def logistic_map(x, r, steps=10000, marked=1000):
  for _ in range(steps - marked):
    x = r * x * (1 - x)
  route = []
  for _ in range(marked):
    x = r * x * (1 - x)
    route.append(x)
  return route

def plot_bifurcation_diagram(r_start=2.4, r_end=4.0, r_steps=1000, x_start=0.5):
  r_values = np.linspace(r_start, r_end, r_steps)
  r_points = []
  x_values = []

  for r in r_values:
    points = logistic_map(x_start, r)
    r_points.extend([r] * len(points))
    x_values.extend(points)

  plt.figure(figsize=(12, 8))
  plt.scatter(r_points, x_values, s=0.1, color='green')
  plt.xlabel('r')
  plt.ylabel('x')
  plt.title('Бифуркационное дерево для логистического отображения')
  plt.show()

plot_bifurcation_diagram()
