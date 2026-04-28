"""
Helper module for TSIS-2 Paint Application
Contains drawing utilities and tool functions
"""

import pygame
from collections import deque
from datetime import datetime


def draw_thick_line(surface, start, end, thickness, color):
    """Draw a smooth line with given thickness using interpolation"""
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


def flood_fill(surface, start_pos, fill_color):
    """
    Flood fill algorithm using BFS
    Fills connected area of same color with fill_color
    """
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
        
        # Check all 4 neighbors (up, down, left, right)
        for dx, dy in [(0, 1), (0, -1), (1, 0), (-1, 0)]:
            nx, ny = x + dx, y + dy
            
            if 0 <= nx < surface.get_width() and 0 <= ny < surface.get_height():
                if (nx, ny) not in visited and surface.get_at((nx, ny)) == original_color:
                    visited.add((nx, ny))
                    queue.append((nx, ny))


def save_canvas(surface, filename=None):
    """
    Save canvas as PNG file with optional timestamp
    If no filename provided, uses timestamp
    """
    if filename is None:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"canvas_{timestamp}.png"
    
    pygame.image.save(surface, filename)
    print(f"Canvas saved as {filename}")


def get_brush_info(brush_size_idx):
    """Get brush size in pixels from index"""
    sizes = [2, 5, 10]
    names = ['Small (2px)', 'Medium (5px)', 'Large (10px)']
    return sizes[brush_size_idx], names[brush_size_idx]
