import pygame

def main():
    pygame.init()
    screen = pygame.display.set_mode((800, 600))
    canvas = pygame.Surface((800, 600))
    clock = pygame.time.Clock()
    
    radius = 15
    mode = 'line' 
    # Словарь цветов для быстрого доступа
    colors = {
        'red': (255, 0, 0),
        'green': (0, 255, 0),
        'blue': (0, 0, 255),
        'yellow': (255, 255, 0),
        'black': (0, 0, 0)
    }
    current_color_key = 'blue'
    
    drawing = False
    points = [] 
    start_pos = None 

    while True:
        screen.fill((0, 0, 0))
        screen.blit(canvas, (0, 0))
        
        mouse_pos = pygame.mouse.get_pos()
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE: return
                
                # Выбор инструментов (1-4)
                if event.key == pygame.K_1: mode = 'line'
                if event.key == pygame.K_2: mode = 'rect'
                if event.key == pygame.K_3: mode = 'circle'
                if event.key == pygame.K_4: mode = 'eraser'
                
                # Выбор цветов (R, G, B, Y)
                if event.key == pygame.K_r: current_color_key = 'red'
                elif event.key == pygame.K_g: current_color_key = 'green'
                elif event.key == pygame.K_b: current_color_key = 'blue'
                elif event.key == pygame.K_y: current_color_key = 'yellow'

            if event.type == pygame.MOUSEBUTTONDOWN:
                drawing = True
                start_pos = event.pos
                if mode in ['line', 'eraser']:
                    points = [event.pos]

            if event.type == pygame.MOUSEBUTTONUP:
                if drawing:
                    if mode in ['rect', 'circle']:
                        draw_shape(canvas, start_pos, event.pos, mode, colors[current_color_key])
                    drawing = False
                    points = []

            if event.type == pygame.MOUSEWHEEL:
                radius = max(1, min(100, radius + event.y * 2))

            if event.type == pygame.MOUSEMOTION:
                if drawing:
                    if mode in ['line', 'eraser']:
                        new_point = event.pos
                        points.append(new_point)
                        if len(points) > 1:
                            # Если ластик - рисуем черным, иначе выбранным цветом
                            c = colors['black'] if mode == 'eraser' else colors[current_color_key]
                            draw_smooth_line(canvas, points[-2], points[-1], radius, c)
        
        # Отрисовка превью для фигур
        if drawing and mode in ['rect', 'circle']:
            draw_shape(screen, start_pos, mouse_pos, mode, colors[current_color_key])

        pygame.display.set_caption(f"Инструмент: {mode} | Цвет: {current_color_key} | Радиус: {radius}")
        pygame.display.flip()
        clock.tick(120)

def draw_smooth_line(surface, start, end, radius, color):
    dx = start[0] - end[0]
    dy = start[1] - end[1]
    iterations = max(abs(dx), abs(dy))
    
    for i in range(iterations):
        progress = i / iterations
        x = int((1 - progress) * start[0] + progress * end[0])
        y = int((1 - progress) * start[1] + progress * end[1])
        pygame.draw.circle(surface, color, (x, y), radius)

def draw_shape(surface, start, end, mode, color):
    x1, y1 = start
    x2, y2 = end
    if mode == 'rect':
        rect_x, rect_y = min(x1, x2), min(y1, y2)
        pygame.draw.rect(surface, color, (rect_x, rect_y, abs(x1-x2), abs(y1-y2)), 2)
    elif mode == 'circle':
        rad = int(((x1 - x2)**2 + (y1 - y2)**2)**0.5)
        pygame.draw.circle(surface, color, start, rad, 2)

if __name__ == "__main__":
    main()