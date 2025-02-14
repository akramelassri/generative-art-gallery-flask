from abc import ABC, abstractmethod
import pygame
import pygame.gfxdraw
import math
import numpy as np
import random
from shapely import Polygon, Point

# Base class for shapes
class Shape(ABC):
    def __init__(self, center, color, angle=0):
        self._center = center
        self._color = color
        self._angle = angle

    def set_pos(self, pos):
        self._center = pos
    
    def move(self, distance):
        self._center = (self._center[0] + distance[0], self._center[1] + distance[1])

    def rotate(self, angle):
        self._angle += angle  
        if self._angle >= 360:
            self._angle %= 360
    
    def set_color(self, color):
        self._color = color

    def get_color(self):
        return self._color
    
    @abstractmethod 
    def contains_point(self, pos):
        pass

    @abstractmethod
    def draw(self, screen):
        pass

    def resize(self, resize_factor):
        pass

class Rectangle(Shape):
    def __init__(self, center, width, height, color, angle=0, is_filled=False):
        super().__init__(center, color, angle)
        self._width = width
        self._height = height
        self._is_filled = is_filled

    def draw(self, screen):
        # Calculate the vertices
        self._points = np.array([
            (self._center[0] - self._width / 2, self._center[1] - self._height / 2), 
            (self._center[0] + self._width / 2, self._center[1] - self._height / 2), 
            (self._center[0] + self._width / 2, self._center[1] + self._height / 2), 
            (self._center[0] - self._width / 2, self._center[1] + self._height / 2)
        ])
        
        center = np.array(self._center)
        angle = math.radians(self._angle)
        sin = math.sin(angle)
        cos = math.cos(angle)
        rotation_matrix = np.array([(cos, -sin), (sin, cos)])
        self._points = self._points - center
        self._points = (self._points @ rotation_matrix)
        self._points = (self._points + center).tolist()
        if self._is_filled:
            pygame.draw.polygon(screen, self._color, self._points)
        else:
            pygame.draw.polygon(screen, self._color, self._points, 3)
        
    def copy(self):
        return Rectangle(self._center, self._width, self._height, self._color, self._angle)
    
    def resize(self, resize_factor):
        self._width *= resize_factor
        self._height *= resize_factor
    
    def contains_point(self, pos):
        band = Polygon(self._points).boundary.buffer(4)
        point = Point(pos)
        return band.contains(point)
    
    def highlight_shape(self, screen):
        pygame.draw.polygon(screen, (108, 180, 238), self._points, 7)
        # Draw small square handles at the vertices
        for p in self._points:
            pygame.draw.rect(screen, (108, 180, 238), (p[0]-3, p[1]-3, 6, 6))

class Square(Rectangle):
    def __init__(self, center, side, color, angle=0, is_filled=False):
        super().__init__(center, side, side, color, angle, is_filled)

class Circle(Shape):
    def __init__(self, center, radius, color, angle=0):
        super().__init__(center, color, angle)
        self._radius = radius

    def draw(self, screen):
        pygame.draw.circle(screen, self._color, self._center, self._radius, 3)
        
    def copy(self):
        return Circle(self._center, self._radius, self._color, self._angle)
    
    def resize(self, resize_factor):
        self._radius = int(self._radius * resize_factor)
    
    def contains_point(self, pos):
        circle = Point(self._center).buffer(self._radius).boundary.buffer(4)
        point = Point(pos)
        return circle.contains(point)
    
    # Updated highlight method for circle:
    def highlight_shape(self, screen):
        # Draw a circle slightly larger than the original with a thick border
        pygame.draw.circle(screen, (108, 180, 238), self._center, self._radius + 2, 7)
        # Draw small square handles at the cardinal points
        points = [
            (self._center[0] + self._radius, self._center[1]),
            (self._center[0] - self._radius, self._center[1]),
            (self._center[0], self._center[1] + self._radius),
            (self._center[0], self._center[1] - self._radius)
        ]
        for p in points:
            pygame.draw.rect(screen, (108, 180, 238), (p[0]-3, p[1]-3, 6, 6))

# New class to hold an image (for pattern shapes)
class ImageShape(Shape):
    def __init__(self, center, image):
        super().__init__(center, (255,255,255))
        self.image = image
        self.rect = self.image.get_rect(center=center)
    def draw(self, screen):
        screen.blit(self.image, self.rect)
    def contains_point(self, pos):
        return self.rect.collidepoint(pos)
    def set_pos(self, pos):
        self._center = pos
        self.rect.center = pos
    def highlight_shape(self, screen):
        pygame.draw.rect(screen, (108, 180, 238), self.rect, 4)
    def move(self, distance):
        self._center = (self._center[0] + distance[0], self._center[1] + distance[1])
        self.rect.center = (self.rect.center[0] + distance[0], self.rect.center[1] + distance[1])

class Canva:
    def __init__(self):
        self._shapes = []

    def add_shape(self, shape):
        self._shapes.append(shape)
    
    def render(self, surface):
        for shape in self._shapes:
            shape.draw(surface)

list_colors = [
    (0, 0, 0),
    (255, 0, 0),
    (0, 255, 0),
    (0, 0, 255),
    (255, 255, 255)
]

def change_shapes(mouse_pos, selected_shape):
    if isinstance(selected_shape, Circle):
        return Rectangle(mouse_pos, selected_shape._radius * 2, selected_shape._radius * 3, selected_shape.get_color())
    elif isinstance(selected_shape, Square):
        return Circle(mouse_pos, int(selected_shape._height / 2), selected_shape.get_color())
    else:
        return Square(mouse_pos, selected_shape._height * 2 / 3, selected_shape.get_color())

def change_color(list_colors, selected_shape):
    for i, color in enumerate(list_colors):
        if color == selected_shape.get_color():
            selected_shape.set_color(list_colors[(i + 1) % len(list_colors)])
            return
def random_color():
    return (random.randint(0, 255), random.randint(0, 255), random.randint(0, 255))
def generate_circular_pattern():
    size = (200, 200)
    surf = pygame.Surface(size, pygame.SRCALPHA)
    surf.fill((0, 0, 0, 0))
    center = (size[0] // 2, size[1] // 2)
    num_circles = 8  # number of circles around the anchor
    anchor_radius = random.randint(20,60)  # distance from the center for placing circles
    
    for i in range(num_circles):
        angle = 2 * math.pi * i / num_circles
        x = center[0] + int(anchor_radius * math.cos(angle))
        y = center[1] + int(anchor_radius * math.sin(angle))
        circle_radius = random.randint(20, 50)
        color = random_color()
        pygame.draw.circle(surf, color, (x, y), circle_radius,4)
        
    return surf

def generate_spirograph_pattern():
    size = (300, 300)
    surf = pygame.Surface(size, pygame.SRCALPHA)
    surf.fill((0, 0, 0, 0))
    center = (size[0] // 2, size[1] // 2)
    num_points = 500
    radius = random.randint(50, 100)
    freq = random.uniform(3, 5)
    points = []
    
    for i in range(num_points):
        t = 2 * math.pi * i / num_points
        x = center[0] + int(radius * math.cos(t) + radius/2 * math.cos(freq * t))
        y = center[1] + int(radius * math.sin(t) + radius/2 * math.sin(freq * t))
        points.append((x, y))
        
    # Draw a smooth connecting line
    pygame.draw.lines(surf, random_color(), False, points, 2)
    return surf

def generate_rosecurves_pattern():
    size = (300, 300)
    surf = pygame.Surface(size, pygame.SRCALPHA)
    surf.fill((0, 0, 0, 0))
    center = (size[0] // 2, size[1] // 2)
    num_points = 500
    amplitude = random.randint(60, 100)
    k = random.randint(2, 5)
    points = []
    
    for i in range(num_points):
        t = 2 * math.pi * i / num_points
        r = amplitude * math.cos(k * t)
        x = center[0] + int(r * math.cos(t))
        y = center[1] + int(r * math.sin(t))
        points.append((x, y))
        
    pygame.draw.lines(surf, random_color(), False, points, 2)
    return surf