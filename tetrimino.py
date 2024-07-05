from dataclasses import dataclass
from util import *
from pygame import *
from pygame.sprite import Sprite

@dataclass
class Tetrimino:
    symbol: str
    shape: list[list[int]]
    color: int
    
    def rotate(self, n: int=1):
        if n % 4 == 0:
            return self
        
        new_shape = self.shape
        for _ in range(n % 4):
            new_shape = list(zip(*new_shape[::-1]))
        
        return Tetrimino(self.symbol, new_shape, self.color)
    
    def draw(self, r: int, c: int, screen: Surface, grid_size: int=30, darken: bool=False):
        for i, row in enumerate(self.shape):
            for j, cell in enumerate(row):
                if cell == 1:
                    draw.rect(screen, darken_color(self.color) if darken else self.color, ((c+j)*grid_size, (r+i)*grid_size, grid_size, grid_size))
                    draw.rect(screen, (25, 25, 25), ((c+j)*grid_size, (r+i)*grid_size, grid_size, grid_size), width=1)

    def draw_at(self, x: int, y: int, screen: Surface, grid_size: int=30, darken: bool=False):
        r = len(self.shape)
        c = len(self.shape[0])
        
        # 중앙 기준으로 그리기
        for i, row in enumerate(self.shape):
            for j, cell in enumerate(row):
                if cell == 1:
                    draw.rect(screen, darken_color(self.color) if darken else self.color, (x - c/2*grid_size + j*grid_size, y - r/2*grid_size + i*grid_size, grid_size, grid_size))
                    draw.rect(screen, (25, 25, 25), (x - c/2*grid_size + j*grid_size, y - r/2*grid_size + i*grid_size, grid_size, grid_size), width=1)

class Tetriminos(SingleTon):
    I: Tetrimino
    O: Tetrimino
    T: Tetrimino
    J: Tetrimino
    L: Tetrimino
    S: Tetrimino
    Z: Tetrimino
    
    def aslist(self):
        return [self.I, self.O, self.T, self.J, self.L, self.S, self.Z]

    def __iter__(self):
        return iter(self.aslist())

tetriminos = Tetriminos()
tetriminos.T = Tetrimino('T', [
    [1, 1, 1],
    [0, 1, 0]
], 0x800080)
tetriminos.I = Tetrimino('I', [
    [1, 1, 1, 1]
], 0x00FFFF)   
tetriminos.O = Tetrimino('O', [
    [1, 1],
    [1, 1]
], 0xFFFF00)  
tetriminos.L = Tetrimino('L', [
    [1, 1, 1],
    [1, 0, 0]
], 0xFF7F00)  
tetriminos.J = Tetrimino('J', [
    [1, 1, 1],
    [0, 0, 1]
], 0x0000FF)
tetriminos.S = Tetrimino('S', [
    [0, 1, 1],
    [1, 1, 0]
], 0x00FF00)
tetriminos.Z = Tetrimino('Z', [
    [1, 1, 0],
    [0, 1, 1]
], 0xFF0000)

class TetriminoSprite(Sprite):
    def __init__(self, tetrimino: Tetrimino, center: tuple[int, int], grid_size: int):
        super().__init__()
        self.tetrimino = tetrimino
        
        r = len(tetrimino.shape)
        c = len(tetrimino.shape[0])
        self.rect = Rect(center[0] - c/2*grid_size, center[1] - r/2*grid_size, c*grid_size, r*grid_size)
        
        self.grid_x = None
        self.grid_y = None
        
        self.grid_size = grid_size
        
    def draw_at(self, screen: Surface):
        self.tetrimino.draw_at(self.rect.centerx, self.rect.centery, screen, self.grid_size)
        
    def rotate(self, n: int=1):
        self.tetrimino = self.tetrimino.rotate(n)
        
        r = len(self.tetrimino.shape)
        c = len(self.tetrimino.shape[0])
        self.rect = Rect(self.rect.centerx - c/2*self.grid_size, self.rect.centery - r/2*self.grid_size, c*self.grid_size, r*self.grid_size)
        
    def move(self, dx: int, dy: int):
        self.rect.x += dx
        self.rect.y += dy
        
    def move_to(self, x: int, y: int):
        self.rect.x = x
        self.rect.y = y

__all__ = ['tetriminos', 'Tetrimino', 'TetriminoSprite']
