from abc import ABC,abstractmethod
import pygame
import math
import numpy as np
from shapely import Polygon, Point

# Base class for shapes
class Shape(ABC):
    def __init__(self, center, color, angle = 0):
        self._center = center
        self._color = color
        self._angle = angle

    def set_pos(self, pos):
        self._center = pos
    
    def move(self, distance):
        self._center = (self._center[0] + distance[0], self._center[1] + distance[1])

    def rotate(self,angle):
        self._angle += angle  
        if self._angle >= 360:
            self._angle = self._angle % 360
    
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

    @abstractmethod
    def resize(self, resize_factor):
        pass

class Rectangle(Shape):
    def __init__(self, center, width, height, color, angle = 0, is_filled = False):
        super().__init__(center, color, angle)
        self._width = width
        self._height = height
        self._is_filled = is_filled

    def draw(self, screen):
        # Calculate the vertices
        self._points = np.array([(self._center[0] - self._width / 2, self._center[1] - self._height / 2), 
                        (self._center[0] + self._width / 2, self._center[1] - self._height / 2), 
                        (self._center[0] + self._width / 2, self._center[1] + self._height / 2), 
                        (self._center[0] - self._width / 2, self._center[1] + self._height / 2)])
        
        center = np.array(self._center)
        
        angle = math.radians(self._angle)
        sin = math.sin(angle)
        cos = math.cos(angle)

        # Applying rotation
        rotation_matrix = np.array([(cos, -sin),(sin, cos)])
        self._points -= center
        self._points = (self._points @ rotation_matrix)
        self._points = (self._points + center).tolist()
        if self._is_filled:
            pygame.draw.polygon(screen,self._color, self._points)
        else:
            pygame.draw.polygon(screen,self._color, self._points, 3)
        
    def copy(self):
        return Rectangle(self._center, self._width, self._height, self._color, self._angle)
    
    def resize(self, resize_factor):
        self._width *= resize_factor
        self._height *= resize_factor
    
    def contains_point(self, pos):
        if self._is_filled:
            band = Polygon(self._points).boundary.buffer(4)
            point = Point(pos)
            return True if band.contains(point) else False      
        else:
            band = Polygon(self._points).boundary.buffer(4)
            point = Point(pos)
            return True if band.contains(point) else False
    def highlight_shape(self,screen):
        pygame.draw.polygon(screen,(108, 180, 238), self._points, 7)
        squares = [Square((self._points[0][0],self._points[0][1]), 8,(108, 180, 238),0,True),
                   Square((self._points[1][0],self._points[1][1]), 8,(108, 180, 238),0,True),
                   Square((self._points[2][0],self._points[2][1]), 8,(108, 180, 238),0,True),
                   Square((self._points[3][0],self._points[3][1]), 8,(108, 180, 238),0,True),
        ]
        angle = math.radians(self._angle)
        sin = math.sin(angle)
        cos = math.cos(angle)
        points_to_rotate = np.array([( self._width / 2,-0),( self._width / 2, +0),(-0, self._height / 2),(0 ,self._height / 2)])
        center = np.array(self._center)
        # Applying rotation
        rotation_matrix = np.array([(cos, -sin),(sin, cos)])
        points_to_rotate -= center
        points_to_rotate = (points_to_rotate @ rotation_matrix)
        points_to_rotate = (points_to_rotate).tolist()
        

        for i,point in enumerate(points_to_rotate):
            new_point = (squares[i]._center[0]+ point[0],squares[i]._center[1]+ point[1] )
            squares.append(Square(new_point, 5,(108, 180, 238),0,True))
        for square in squares:
            square.draw(screen)



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
        self._radius *= resize_factor
    
    def contains_point(self, pos):
        circle = Point(self._center).buffer(self._radius).boundary.buffer(4)
        point = Point(pos)
        return True if circle.contains(point) else False


class Canva:
    def __init__(self):
        self._shapes = []

    def add_shape(self, shape):
        self._shapes.append(shape)
    
    def render(self , surface):
        for shape in self._shapes:
            shape.draw(surface)

list_colors = [
    (0,0,0),
    (255,0,0),
    (0,255,0),
    (0,0,255),
    (255,255,255)]

def change_shapes(mouse_pos, selected_shape):
    if(isinstance(selected_shape, Circle)):
        return Rectangle(mouse_pos, selected_shape._radius * 2, selected_shape._radius * 3,selected_shape.get_color())
    elif(isinstance(selected_shape, Square)):
        return Circle(mouse_pos, selected_shape._height / 2, selected_shape.get_color())
    else:
        return Square(mouse_pos, selected_shape._height * 2 / 3, selected_shape.get_color())

def change_color(list_colors, selected_shape):
    for i, color in enumerate(list_colors):
        if color == selected_shape.get_color():
            selected_shape.set_color (list_colors[(i + 1) % len(list_colors)])
            return