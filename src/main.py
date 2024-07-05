from pygame import *
from tetrimino import *
from copy import deepcopy
import sys

init()

grid_size = 30
row, col = 20, int(input("열의 수를 입력해주세요: "))

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

# undo, redo
undo: list[GridType] = []
redo: list[GridType] = []

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
                    
                # 줄 완성되면 지우기
                for i, row_list in enumerate(grids):
                    if all(cell is not None for cell in row_list):
                        animations.extend([(i, j) for j in range(col)])
                        grids.pop(i)
                        grids.insert(0, [None] * col)
                
                dragging = False
                dragged = None
                projected = None
                clicked_diff_pos = (None, None)
        
        # 미노 돌리기 및 undo, redo
        elif evt.type == KEYDOWN:
            if dragging:
                if evt.key == K_x:
                    dragged.rotate()
                    if projected is not None:
                        projected.rotate()

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
            draw.rect(screen, (25, 25, 25), (c*grid_size, r*grid_size, grid_size, grid_size), width=1)
        
    # 애니메이션 그리기
    if duration > 0:
        for r, c in animations:
            # draw.rect(screen, (255 * duration, 255 * duration, 255 * duration), (c*grid_size, r*grid_size, grid_size, grid_size))
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

    display.flip()
    display.update()

quit()
sys.exit()