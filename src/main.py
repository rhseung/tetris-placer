from pygame import *
from tetrimino import *
from copy import deepcopy
import sys
import os

init()

grid_size = 30
row, col = 20, 10

screen_size = (150 + grid_size*col, grid_size*row)
screen = display.set_mode(screen_size)
display.set_caption("Tetris Placer")

# 그리드 초기화
GridType = list[list[int]]
grids: GridType = [[None] * col for _ in range(row)]

# 가방 스프라이트
bags = [
    TetriminoSprite(tetriminos.I, (screen_size[0] - 75, 50), 30),
    TetriminoSprite(tetriminos.O, (screen_size[0] - 75, 130), 30),
    TetriminoSprite(tetriminos.T, (screen_size[0] - 75, 210), 30),
    TetriminoSprite(tetriminos.J, (screen_size[0] - 75, 290), 30),
    TetriminoSprite(tetriminos.L, (screen_size[0] - 75, 370), 30),
    TetriminoSprite(tetriminos.S, (screen_size[0] - 75, 450), 30),
    TetriminoSprite(tetriminos.Z, (screen_size[0] - 75, 530), 30)
]

# 드래그 관련 상태 변수
running: bool = True
dragging: bool = False
dragged: TetriminoSprite = None
projected: TetriminoSprite = None
clicked_diff_pos: tuple[int, int] = (None, None)

# 키 관련 상태 변수
is_ctrl_pressed: bool = False
is_z_pressed: bool = False
is_y_pressed: bool = False
key_sleep: bool = False
is_mouse_pressed: bool = False

# undo, redo
undo: list[GridType] = []
redo: list[GridType] = []
is_mouse_pressed = [False] * 3

# animation blocks
animations: list[tuple[int, int]] = []  # animation할 좌표를 저장
duration = 0  # animation 지속 시간

while running:
    # 이벤트 처리
    for evt in event.get():
        # 종료 이벤트
        if evt.type == QUIT:
            running = False
        
        # 드래그 시작
        elif evt.type == MOUSEBUTTONDOWN:
            mouse_x, mouse_y = evt.pos
            for mino in bags:
                if mino.rect.collidepoint(mouse_x, mouse_y):
                    dragging = True
                    dragged = deepcopy(mino)
                    projected = deepcopy(mino)
                    clicked_diff_pos = (mouse_x - dragged.rect.x, mouse_y - dragged.rect.y)
        
        # 드래그 끝 
        elif evt.type == MOUSEBUTTONUP:
            if dragging:    # grids에 projected 넣기
                can_place = True
                
                if projected is None or projected.grid_x is None or projected.grid_y is None:
                    can_place = False
                
                # 그리드에 미노가 겹치는지 확인
                if can_place:
                    for i, row_list in enumerate(projected.tetrimino.shape):
                        for j, cell in enumerate(row_list):
                            if cell == 1:
                                if grids[projected.grid_y + i][projected.grid_x + j] is not None:
                                    can_place = False
                                    break
                
                # 그리드에 미노 추가
                if can_place:
                    # 기록 추가
                    undo.append(deepcopy(grids))
                    redo = []
                    
                    # 그리드에 미노 추가
                    for i, row_list in enumerate(projected.tetrimino.shape):
                        for j, cell in enumerate(row_list):
                            if cell == 1:
                                grids[projected.grid_y + i][projected.grid_x + j] = dragged.tetrimino.color
                                animations.append((projected.grid_y + i, projected.grid_x + j))
                    duration = 1
                
                dragging = False
                dragged = None
                projected = None
                clicked_diff_pos = (None, None)
             
                # 줄 완성되면 지우기
                for i, row_list in enumerate(grids):
                    if all(cell is not None for cell in row_list):
                        animations.extend([(i, j) for j in range(col)])
                        grids.pop(i)
                        grids.insert(0, [None] * col)
                # if animations and duration == 0:
                #     duration = 1
        
        # 미노 돌리기 및 undo, redo
        elif evt.type == KEYDOWN:
            if evt.key == K_ESCAPE:
                os.execl(sys.executable, sys.executable, *sys.argv)
            elif dragging:
                if evt.key == K_c:
                    dragged.rotate()
                    if projected is not None:
                        projected.rotate()
                elif evt.key == K_x:
                    dragged.rotate(-1)
                    if projected is not None:
                        projected.rotate(-1)
                elif evt.key == K_a:
                    dragged.rotate(2)
                    if projected is not None:
                        projected.rotate(2)

            if evt.key == K_LCTRL:
                is_ctrl_pressed = True
            if evt.key == K_z:
                is_z_pressed = True
            if evt.key == K_y:
                is_y_pressed = True
                
            if is_ctrl_pressed and is_z_pressed and not key_sleep and len(undo) > 0:
                key_sleep = True
                redo.append(deepcopy(grids))
                grids = undo.pop()
            if is_ctrl_pressed and is_y_pressed and not key_sleep and len(redo) > 0:
                key_sleep = True
                undo.append(deepcopy(grids))
                grids = redo.pop()
        
        elif evt.type == KEYUP:
            if evt.key == K_LCTRL:
                key_sleep = False
                is_ctrl_pressed = False
            if evt.key == K_z:
                key_sleep = False
                is_z_pressed = False
            if evt.key == K_y:
                key_sleep = False
                is_y_pressed = False

    # 화면 그리기
    screen.fill((0, 0, 0))
    
    # 그리드 그리기
    for r in range(row):
        for c in range(col):
            if grids[r][c] is not None:
                draw.rect(screen, grids[r][c], (c*grid_size, r*grid_size, grid_size, grid_size))
            draw.rect(screen, 0x191919, (c*grid_size, r*grid_size, grid_size, grid_size), width=1)
        
    # 애니메이션 그리기
    if duration > 0:
        for r, c in animations:
            # transparent surface를 만들어서 마스크로 사용
            mask = Surface((grid_size, grid_size), SRCALPHA)
            mask.fill((255, 255, 255, 255 * duration))
            screen.blit(mask, (c*grid_size, r*grid_size))
    
        duration -= 1 / 100
        if duration <= 0:
            duration = 0
            animations = []
    
    # 오른쪽에 가방 그리기
    for mino in bags:
        mino.draw_at(screen)

    # 드래그
    if dragging:
        mouse_x, mouse_y = mouse.get_pos()
        
        # 클릭한 위치와의 차이
        mouse_x = mouse_x - clicked_diff_pos[0]
        mouse_y = mouse_y - clicked_diff_pos[1]
        
        # 그리드 안에 있는지 확인
        if 0 <= mouse_x < (col - len(projected.tetrimino.shape[0]) + 1)*grid_size and 0 <= mouse_y < (row - len(projected.tetrimino.shape) + 1)*grid_size:
            # 가장 가까운 그리드 좌표
            grid_x = (mouse_x) // grid_size
            grid_y = (mouse_y) // grid_size
            
            projected.grid_x = grid_x
            projected.grid_y = grid_y
            projected.tetrimino.draw(grid_y, grid_x, screen, darken=True)
        else:
            projected.grid_x = None
            projected.grid_y = None
            dragged.move_to(mouse_x, mouse_y)
            dragged.draw_at(screen)
    
    else:   # 1*1 미노 관리
        mouse_buttons = mouse.get_pressed()
        mouse_x, mouse_y = mouse.get_pos()
        grid_x = mouse_x // grid_size
        grid_y = mouse_y // grid_size
        
        buff = []   # 그리드에 1*1 미노 추가할 좌표
        
        if 0 <= grid_y < row and 0 <= grid_x < col:
            if mouse_buttons[0] == True:    # 배치
                if is_mouse_pressed[0] == False:
                    undo.append(deepcopy(grids))
                    redo = []
                    
                is_mouse_pressed[0] = True
                
                if grids[grid_y][grid_x] is None:                
                    grids[grid_y][grid_x] = 0x323232
                    animations.append((grid_y, grid_x))
            elif is_mouse_pressed[0] == True:
                is_mouse_pressed[0] = False
                if animations and duration == 0:
                    duration = 1
            
            if mouse_buttons[2] == True:    # 지우기
                if is_mouse_pressed[2] == False:
                    undo.append(deepcopy(grids))
                    redo = []
                
                is_mouse_pressed[2] = True
                
                if grids[grid_y][grid_x] is not None:                
                    grids[grid_y][grid_x] = None
                    animations.append((grid_y, grid_x))
            elif is_mouse_pressed[2] == True:
                is_mouse_pressed[2] = False
                if animations and duration == 0:
                    duration = 1
        
        # 줄 완성되면 지우기
        for i, row_list in enumerate(grids):
            if all(cell is not None for cell in row_list):
                animations.extend([(i, j) for j in range(col)])
                grids.pop(i)
                grids.insert(0, [None] * col)
        
        if is_mouse_pressed[0] == False and animations and duration == 0:
            duration = 1
    
    # print(len(undo), len(redo))
    
    display.flip()
    display.update()

quit()
sys.exit()