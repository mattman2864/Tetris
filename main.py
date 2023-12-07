import pygame
from copy import copy
from random import randint, choice

RESOLUTION = 600, 600
BOARD_BOUNDS = 300, 600
SQUARE_SIZE = BOARD_BOUNDS[0]/10
FPS = 60
class Board:
    def __init__(self):
        self.pieces = [Piece(random_piece())]
        self.active_piece = self.pieces[-1]
        self.pixel_map = [[0 for i in range(10)] for i in range(20)]
        self.points = 0
    def draw(self, screen):
        for piece in self.pieces:
            piece.draw(screen)
    def update(self):
        self.active_piece = self.pieces[-1]
        self.active_piece.update()
        self.update_pixel_map()
        if not self.active_piece.active:
            self.pieces.append(Piece(random_piece()))
            return
        if self.detect_collision(self.active_piece, (1, 0)):
            self.active_piece.active = False
            return
        self.check_clear()
        self.active_piece.y += 1
        
    def update_pixel_map(self):
        '''
        Updates a 2D binary array of where inactive squares are
        '''
        self.pixel_map = [[0 for i in range(10)] for i in range(20)]
        for piece in self.pieces:
            if piece == self.active_piece:
                continue
            for square in piece.squares:
                self.pixel_map[piece.y + square[0]][piece.x + square[1]] = 1
    def detect_collision(self, piece, dir):
        for square in piece.squares:
            checksquare_y = clamp(piece.y + square[0] + dir[0], 0, 19)
            checksquare_x = clamp(piece.x + square[1] + dir[1], 0, 9)
            if self.pixel_map[checksquare_y][checksquare_x] == 1:
                return True
        return False
    def strafe(self, dist):
        if self.detect_collision(self.active_piece, (0, dist)) or not self.active_piece.active:
            return
        self.active_piece.strafe(dist)
    def rotate(self):
        self.active_piece.rotate(1)
        for square in self.active_piece.squares:
            if not (0 <= self.active_piece.y + square[0] <= 19 and 0 <= self.active_piece.x + square[1] <= 9):
                self.active_piece.rotate(-1)
                return
            if self.pixel_map[self.active_piece.y + square[0]][self.active_piece.x + square[1]] == 1:
                print(2)
                self.active_piece.rotate(-1)
                return
    def check_clear(self):
        combo = 0
        for i, row in enumerate(self.pixel_map):
            if row == [1 for i in range(10)]:
                combo += 1
                for piece in self.pieces.copy():
                    piece.destroy_row(i)
                    piece.y += 1
                    if len(piece.squares) == 0:
                        self.pieces.remove(piece)
                self.pixel_map.remove(row)
                self.pixel_map.insert(0, [0 for i in range(10)])
        self.points += {0:0, 1:40, 2:100, 3:300, 4:1200}[combo]
    
class Piece:
    def __init__(self, type):
        self.type = type
        self.x = 5
        self.y = 0
        self.active = True
        match self.type:
            case 'L':
                self.color = 'orange'
                self.squares = [
                    (0, -2), (0, -1), (0, 0), (1, -2)
                ]
                self.rotations = [
                    [()]
                ]
            case 'I':
                self.color = 'cyan'
                self.squares = [
                    (0, -2), (0, -1), (0, 0), (0, 1)
                ]
            case 'S':
                self.color = 'green'
                self.squares = [
                    (1, -1), (1, 0), (0, 0), (0, 1)
                ]
            case 'Z':
                self.color = 'red'
                self.squares = [
                    (0, -1), (1, 0), (0, 0), (1, 1)
                ]
            case 'J':
                self.color = 'blue'
                self.squares = [
                    (1, 1), (0, -1), (0, 0), (0, 1)
                ]
            case 'T':
                self.color = 'purple'
                self.squares = [
                    (0, -1), (1, 0), (0, 0), (0, 1)
                ]
            case 'O':
                self.color = 'yellow'
                self.squares = [
                    (0, 0), (1, 0), (0, 1), (1, 1)
                ]
    def update(self):
        if not self.active:
            return
        for square in self.squares:
            if square[0] + self.y == 19:
                self.active = False
                return
    def strafe(self, dist):
        for square in self.squares:
            if self.x + square[1] + dist > 9 or self.x + square[1] + dist < 0:
                return
        self.x += dist
    def rotate(self, dir):
        if self.type == 'O':
            return
        squares = self.squares.copy()
        self.squares = []
        for square in squares:
            self.squares.append((-square[1]*dir, square[0]*dir))
    def destroy_row(self, row):
        for square in self.squares.copy():
            if self.y + square[0] == row:
                self.squares.remove(square)
    def draw(self, screen):
        for square in self.squares:
            pygame.draw.rect(screen, self.color, pygame.Rect(150 + SQUARE_SIZE*(self.x+square[1]),
                                                        SQUARE_SIZE * (self.y + square[0]),
                                                        SQUARE_SIZE, SQUARE_SIZE))
            pygame.draw.rect(screen, 'black', pygame.Rect(150 + SQUARE_SIZE*(self.x+square[1]),
                                                        SQUARE_SIZE * (self.y + square[0]),
                                                        SQUARE_SIZE, SQUARE_SIZE), width=1)

def update_board(board: list[Piece]):
    for piece in board:
        piece.update()

def random_piece():
    return choice(['I', 'S', 'L', 'Z', 'J', 'T', 'O'])

clamp = lambda value, minv, maxv: max(min(value, maxv), minv)

pygame.init()
screen = pygame.display.set_mode(RESOLUTION)
clock = pygame.time.Clock()

board = Board()

down = pygame.USEREVENT + 1
pygame.time.set_timer(down, 200)

new_piece = pygame.event.Event(pygame.USEREVENT + 2)

running = True
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        if event.type == down:
            board.update()
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_LEFT:
                board.strafe(-1)
            if event.key == pygame.K_RIGHT:
                board.strafe(1)
            if event.key == pygame.K_UP:
                board.rotate()
            if event.key == pygame.K_DOWN:
                board.update()

    screen.fill('#111111')
    pygame.draw.rect(screen, 'black', pygame.Rect(150, 0, 300, 600))
    board.draw(screen)
    print(board.points)

    clock.tick(FPS)
    pygame.display.update()