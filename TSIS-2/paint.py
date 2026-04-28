import pygame
import sys
from datetime import datetime
from collections import deque

def main():
    pygame.init()
    screen = pygame.display.set_mode((800, 600))
    canvas = pygame.Surface((800, 600))
    canvas.fill((255, 255, 255))
    clock = pygame.time.Clock()
    
    # Brush sizes: small, medium, large
    brush_sizes = [2, 5, 10]
    brush_size_idx = 1  # Start with medium (5)
    
    mode = 'pencil'
    colors = {
        'red': (255, 0, 0),
        'green': (0, 255, 0),
        'blue': (0, 0, 255),
        'yellow': (255, 255, 0),
        'black': (0, 0, 0),
        'white': (255, 255, 255)
    }
    current_color_key = 'black'
    
    drawing = False
    points = []
    start_pos = None
    
    # Text tool variables
    text_mode = False
    text_input = ""
    text_pos = None
    font = pygame.font.SysFont('arial', 24)

    while True:
        screen.fill((255, 255, 255))
        screen.blit(canvas, (0, 0))
        
        mouse_pos = pygame.mouse.get_pos()
        
        # Draw text input in progress
        if text_mode and text_pos:
            preview_text = font.render(text_input + "|", True, colors[current_color_key])
            screen.blit(preview_text, text_pos)
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    if text_mode:
                        text_mode = False
                        text_input = ""
                        text_pos = None
                    else:
                        pygame.quit()
                        sys.exit()
                
                # Text input mode
                if text_mode:
                    if event.key == pygame.K_RETURN:
                        # Render text onto canvas
                        if text_input:
                            rendered_text = font.render(text_input, True, colors[current_color_key])
                            canvas.blit(rendered_text, text_pos)
                        text_mode = False
                        text_input = ""
                        text_pos = None
                    elif event.key == pygame.K_BACKSPACE:
                        text_input = text_input[:-1]
                    else:
                        if event.unicode.isprintable():
                            text_input += event.unicode
                else:
                    # Tool selection (1-8: shapes, 9: pencil, 0: line, F: flood fill, T: text)
                    if event.key == pygame.K_1: mode = 'rect'
                    elif event.key == pygame.K_2: mode = 'circle'
                    elif event.key == pygame.K_3: mode = 'square'
                    elif event.key == pygame.K_4: mode = 'right_triangle'
                    elif event.key == pygame.K_5: mode = 'eq_triangle'
                    elif event.key == pygame.K_6: mode = 'rhombus'
                    elif event.key == pygame.K_7: mode = 'eraser'
                    elif event.key == pygame.K_8: mode = 'pencil'
                    elif event.key == pygame.K_9: mode = 'line'
                    elif event.key == pygame.K_f: mode = 'flood_fill'
                    elif event.key == pygame.K_t: mode = 'text'
                    
                    # Brush size (Q, W, E for small, medium, large)
                    elif event.key == pygame.K_q: brush_size_idx = 0
                    elif event.key == pygame.K_w: brush_size_idx = 1
                    elif event.key == pygame.K_e: brush_size_idx = 2
                    
                    # Color selection (R, G, B, Y, K=black, W=white)
                    elif event.key == pygame.K_r: current_color_key = 'red'
                    elif event.key == pygame.K_g: current_color_key = 'green'
                    elif event.key == pygame.K_b: current_color_key = 'blue'
                    elif event.key == pygame.K_y: current_color_key = 'yellow'
                    elif event.key == pygame.K_k: current_color_key = 'black'
                    
                    # Save canvas (Ctrl+S)
                    if event.key == pygame.K_s and pygame.key.get_mods() & pygame.KMOD_CTRL:
                        save_canvas(canvas)

            if event.type == pygame.MOUSEBUTTONDOWN and not text_mode:
                drawing = True
                start_pos = event.pos
                
                # Flood fill on click
                if mode == 'flood_fill':
                    flood_fill(canvas, event.pos, colors[current_color_key])
                    drawing = False
                
                # Text placement
                elif mode == 'text':
                    text_mode = True
                    text_pos = event.pos
                    text_input = ""
                    drawing = False
                
                # Other drawing modes
                elif mode in ['pencil', 'line', 'eraser']:
                    points = [event.pos]

            if event.type == pygame.MOUSEBUTTONUP and not text_mode:
                if drawing:
                    if mode == 'line':
                        draw_thick_line(canvas, start_pos, event.pos, brush_sizes[brush_size_idx], colors[current_color_key])
                    elif mode not in ['pencil', 'eraser', 'flood_fill', 'text']:
                        draw_shape(canvas, start_pos, event.pos, mode, colors[current_color_key], brush_sizes[brush_size_idx])
                    drawing = False
                    points = []

            if event.type == pygame.MOUSEMOTION and not text_mode:
                if drawing:
                    if mode in ['pencil', 'eraser']:
                        new_point = event.pos
                        points.append(new_point)
                        if len(points) > 1:
                            c = colors['white'] if mode == 'eraser' else colors[current_color_key]
                            draw_thick_line(canvas, points[-2], points[-1], brush_sizes[brush_size_idx], c)
                    elif mode == 'line':
                        pass  # Preview handled below
        
        # Live preview for shapes and line
        if drawing and not text_mode:
            if mode == 'line':
                draw_thick_line(screen, start_pos, mouse_pos, brush_sizes[brush_size_idx], colors[current_color_key])
            elif mode not in ['pencil', 'eraser', 'flood_fill', 'text']:
                draw_shape(screen, start_pos, mouse_pos, mode, colors[current_color_key], brush_sizes[brush_size_idx])
        
        # Display info
        brush_name = ['Small (2px)', 'Medium (5px)', 'Large (10px)'][brush_size_idx]
        status = f"Tool: {mode} | Color: {current_color_key} | Brush: {brush_name}"
        if text_mode:
            status += " | TEXT MODE (Enter=confirm, Escape=cancel)"
        
        title_font = pygame.font.SysFont('arial', 10)
        pygame.display.set_caption(status)
        pygame.display.flip()
        clock.tick(120)

def draw_thick_line(surface, start, end, thickness, color):
    """Draw a smooth line with given thickness"""
    dx = start[0] - end[0]
    dy = start[1] - end[1]
    distance = max(abs(dx), abs(dy))
    
    if distance == 0:
        pygame.draw.circle(surface, color, start, thickness)
        return
    
    for i in range(distance):
        progress = i / distance
        x = int((1 - progress) * start[0] + progress * end[0])
        y = int((1 - progress) * start[1] + progress * end[1])
        pygame.draw.circle(surface, color, (x, y), thickness)

def draw_shape(surface, start, end, mode, color, thickness):
    """Draw shapes with adjustable thickness"""
    x1, y1 = start
    x2, y2 = end
    
    if mode == 'rect':
        rect_x, rect_y = min(x1, x2), min(y1, y2)
        pygame.draw.rect(surface, color, (rect_x, rect_y, abs(x1-x2), abs(y1-y2)), thickness)
    
    elif mode == 'circle':
        rad = int(((x1 - x2)**2 + (y1 - y2)**2)**0.5)
        pygame.draw.circle(surface, color, start, rad, thickness)
    
    elif mode == 'square':
        side = min(abs(x1 - x2), abs(y1 - y2))
        top_left_x = min(x1, x2)
        top_left_y = min(y1, y2)
        pygame.draw.rect(surface, color, (top_left_x, top_left_y, side, side), thickness)
    
    elif mode == 'right_triangle':
        points = [(x1, y1), (x2, y1), (x1, y2)]
        pygame.draw.polygon(surface, color, points, thickness)
    
    elif mode == 'eq_triangle':
        base_length = abs(x2 - x1)
        height = int(base_length * 0.866)
        
        left_x = min(x1, x2)
        top_x = left_x + base_length // 2
        
        top_y = y1
        bottom_y = y1 + height
        
        points = [(top_x, top_y), (left_x, bottom_y), (left_x + base_length, bottom_y)]
        pygame.draw.polygon(surface, color, points, thickness)
    
    elif mode == 'rhombus':
        center_x = (x1 + x2) // 2
        center_y = (y1 + y2) // 2
        
        half_width = abs(x2 - x1) // 2
        half_height = abs(y2 - y1) // 2
        
        points = [
            (center_x, center_y - half_height),
            (center_x + half_width, center_y),
            (center_x, center_y + half_height),
            (center_x - half_width, center_y)
        ]
        pygame.draw.polygon(surface, color, points, thickness)

def flood_fill(surface, start_pos, fill_color):
    """Flood fill algorithm using BFS"""
    if not surface.get_rect().collidepoint(start_pos):
        return
    
    original_color = surface.get_at(start_pos)
    
    # If fill color is same as original, skip
    if original_color == fill_color:
        return
    
    queue = deque([start_pos])
    visited = {start_pos}
    
    while queue:
        x, y = queue.popleft()
        
        # Set current pixel
        surface.set_at((x, y), fill_color)
        
        # Check all 4 neighbors
        for dx, dy in [(0, 1), (0, -1), (1, 0), (-1, 0)]:
            nx, ny = x + dx, y + dy
            
            if 0 <= nx < surface.get_width() and 0 <= ny < surface.get_height():
                if (nx, ny) not in visited and surface.get_at((nx, ny)) == original_color:
                    visited.add((nx, ny))
                    queue.append((nx, ny))

def save_canvas(surface):
    """Save canvas as timestamped PNG"""
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"canvas_{timestamp}.png"
    pygame.image.save(surface, filename)
    print(f"Canvas saved as {filename}")

if __name__ == "__main__":
    main()
