import pygame
import random
import math
from typing import List, Tuple

pygame.init()

WINDOW_WIDTH = 800
WINDOW_HEIGHT = 600
BOX_WIDTH = 400
BOX_HEIGHT = 300
PARTICLE_RADIUS = 5
NUM_PARTICLES = 50
MIN_SPEED = 1
MAX_SPEED = 5
TEMPERATURE_FACTOR = 0.5
WALL_THICKNESS = 4
PARTICLE_MASS = 1.0
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
BLUE = (0, 0, 255)
RED = (255, 0, 0)
GRAY = (128, 128, 128)
YELLOW = (255, 255, 0)
LIGHT_YELLOW = (255, 255, 200)
LIGHT_RED = (255, 200, 200)
DARK_YELLOW = (200, 200, 0)
DARK_RED = (200, 0, 0)
CONTAINER_COLOR = (200, 200, 220)
CONTAINER_BORDER = (100, 100, 120)
CONTAINER_SHADOW = (180, 180, 200)
BUTTON_WIDTH = 50
BUTTON_HEIGHT = 50
BUTTON_MARGIN = 20
BUTTON_RADIUS = 10
CONTAINER_SHADOW_SIZE = 5

class Button:
    def __init__(self, x: int, y: int, width: int, height: int, text: str, color: Tuple[int, int, int], hover_color: Tuple[int, int, int], dark_color: Tuple[int, int, int], label: str = ""):
        self.rect = pygame.Rect(x, y, width, height)
        self.text = text
        self.color = color
        self.hover_color = hover_color
        self.dark_color = dark_color
        self.is_hovered = False
        self.font = pygame.font.Font(None, 36)
        self.label = label
        self.label_font = pygame.font.Font(None, 24)

    def draw(self, screen):
        shadow_rect = self.rect.copy()
        shadow_rect.x += 2
        shadow_rect.y += 2
        pygame.draw.rect(screen, self.dark_color, shadow_rect, border_radius=BUTTON_RADIUS)
        
        pygame.draw.rect(screen, self.hover_color if self.is_hovered else self.color, 
                        self.rect, border_radius=BUTTON_RADIUS)
        

        pygame.draw.rect(screen, self.dark_color, self.rect, 2, border_radius=BUTTON_RADIUS)

        if self.text in ["↑", "↓"]:
            center_x = self.rect.centerx
            center_y = self.rect.centery
            arrow_size = 20
            
            if self.text == "↑":
                points = [
                    (center_x, center_y - arrow_size),
                    (center_x - arrow_size, center_y + arrow_size//2),
                    (center_x + arrow_size, center_y + arrow_size//2)
                ]
            else:
                points = [
                    (center_x, center_y + arrow_size),
                    (center_x - arrow_size, center_y - arrow_size//2),
                    (center_x + arrow_size, center_y - arrow_size//2)
                ]
            
            pygame.draw.polygon(screen, self.dark_color, points)
        else:
            text_surface = self.font.render(self.text, True, self.dark_color)
            text_rect = text_surface.get_rect(center=self.rect.center)
            screen.blit(text_surface, text_rect)
        
        if self.label:
            label_surface = self.label_font.render(self.label, True, BLACK)
            label_rect = label_surface.get_rect(centerx=self.rect.centerx, top=self.rect.bottom + 5)
            screen.blit(label_surface, label_rect)

    def is_clicked(self, pos) -> bool:
        self.is_hovered = self.rect.collidepoint(pos)
        return self.is_hovered

class Particle:
    def __init__(self, x: float, y: float):
        self.x = x
        self.y = y
        angle = random.uniform(0, 2 * math.pi)
        speed = random.uniform(MIN_SPEED, MAX_SPEED)
        self.dx = speed * math.cos(angle)
        self.dy = speed * math.sin(angle)
        self.mass = PARTICLE_MASS
        
    def move(self, box_x: float, box_y: float, box_width: float, box_height: float):
        new_x = self.x + self.dx
        new_y = self.y + self.dy

        if new_x - PARTICLE_RADIUS < box_x:
            new_x = box_x + PARTICLE_RADIUS
            self.dx = abs(self.dx)
        elif new_x + PARTICLE_RADIUS > box_x + box_width:
            new_x = box_x + box_width - PARTICLE_RADIUS
            self.dx = -abs(self.dx)
            
        if new_y - PARTICLE_RADIUS < box_y:
            new_y = box_y + PARTICLE_RADIUS
            self.dy = abs(self.dy)
        elif new_y + PARTICLE_RADIUS > box_y + box_height:
            new_y = box_y + box_height - PARTICLE_RADIUS
            self.dy = -abs(self.dy)
        
        self.x = new_x
        self.y = new_y
        
    def get_speed(self) -> float:
        return math.sqrt(self.dx**2 + self.dy**2)
    
    def set_speed(self, factor: float):
        current_speed = self.get_speed()
        if current_speed == 0:
            return
        self.dx = self.dx * factor / current_speed
        self.dy = self.dy * factor / current_speed

    def get_kinetic_energy(self) -> float:
        speed = self.get_speed()
        return 0.5 * self.mass * speed**2

class GasSimulator:
    def __init__(self):
        self.screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT), pygame.RESIZABLE)
        pygame.display.set_caption("Kinetic Gas Simulator")
        self.clock = pygame.time.Clock()
        self.particles: List[Particle] = []
        self.temperature = 1.0  
        self.collisions = 0
        self.pressure_history: List[int] = []
        self.font = pygame.font.Font(None, 36)
        self.window_width = WINDOW_WIDTH
        self.window_height = WINDOW_HEIGHT
        self.box_scale = 0.8
        self.pressure_unit = "Pa"
        self.speed_unit = "m/s"
        self.energy_unit = "J"
        self.temp_unit = "T"  
        
        self.update_button_positions()
        self.initialize_particles()
        
    def update_button_positions(self):
        right_margin = 50
        button_spacing = 80  
        
        temp_x = self.window_width - right_margin - BUTTON_WIDTH
        self.temp_up = Button(temp_x, 50, BUTTON_WIDTH, BUTTON_HEIGHT, "↑", 
                            YELLOW, LIGHT_YELLOW, DARK_YELLOW, "")
        self.temp_down = Button(temp_x, 50 + BUTTON_HEIGHT + BUTTON_MARGIN, 
                              BUTTON_WIDTH, BUTTON_HEIGHT, "↓", 
                              YELLOW, LIGHT_YELLOW, DARK_YELLOW, "Temp")
        
        box_x = temp_x - button_spacing - BUTTON_WIDTH
        self.box_increase = Button(box_x, 50, BUTTON_WIDTH, BUTTON_HEIGHT, "+", 
                                 RED, LIGHT_RED, DARK_RED, "")
        self.box_decrease = Button(box_x, 50 + BUTTON_HEIGHT + BUTTON_MARGIN, 
                                 BUTTON_WIDTH, BUTTON_HEIGHT, "-", 
                                 RED, LIGHT_RED, DARK_RED, "Size")

    def handle_resize(self, new_width: int, new_height: int):
        self.window_width = new_width
        self.window_height = new_height
        self.screen = pygame.display.set_mode((new_width, new_height), pygame.RESIZABLE)
        self.update_button_positions()
        self.reposition_particles()

    def reposition_particles(self):
        box_width = min(self.window_width * 0.8, self.window_height * 0.8)
        box_height = box_width * 0.75
        box_x = (self.window_width - box_width) // 2
        box_y = (self.window_height - box_height) // 2
        
        for particle in self.particles:
            #so particles dont move out of the box
            particle.x = max(box_x + PARTICLE_RADIUS, 
                           min(box_x + box_width - PARTICLE_RADIUS, particle.x))
            particle.y = max(box_y + PARTICLE_RADIUS, 
                           min(box_y + box_height - PARTICLE_RADIUS, particle.y))

    def get_box_dimensions(self):
        box_width = min(self.window_width * self.box_scale, self.window_height * self.box_scale)
        box_height = box_width * 0.75
        box_x = (self.window_width - box_width) // 2
        box_y = (self.window_height - box_height) // 2
        return box_width, box_height, box_x, box_y

    def initialize_particles(self):
        box_width, box_height, box_x, box_y = self.get_box_dimensions()
        
        for _ in range(NUM_PARTICLES):
            x = random.uniform(box_x + PARTICLE_RADIUS, box_x + box_width - PARTICLE_RADIUS)
            y = random.uniform(box_y + PARTICLE_RADIUS, box_y + box_height - PARTICLE_RADIUS)
            self.particles.append(Particle(x, y))

    def adjust_box_size(self, change: float):
        old_scale = self.box_scale
        self.box_scale = max(0.3, min(0.9, self.box_scale + change/1000))  
        
        old_width, old_height, old_x, old_y = self.get_box_dimensions()
        new_width, new_height, new_x, new_y = self.get_box_dimensions()
        
        #for maximizing the screen
        for particle in self.particles:
            rel_x = (particle.x - old_x) / old_width
            rel_y = (particle.y - old_y) / old_height
            
            particle.x = new_x + rel_x * new_width
            particle.y = new_y + rel_y * new_height
            
            particle.x = max(new_x + PARTICLE_RADIUS, min(new_x + new_width - PARTICLE_RADIUS, particle.x))
            particle.y = max(new_y + PARTICLE_RADIUS, min(new_y + new_height - PARTICLE_RADIUS, particle.y))

    def adjust_temperature(self, change: float):
        self.temperature = max(0.1, min(2.0, self.temperature + change))
        factor = math.sqrt(self.temperature)
        for particle in self.particles:
            particle.set_speed(factor * MAX_SPEED)
    
    def calculate_average_speed(self) -> float:
        return sum(p.get_speed() for p in self.particles) / len(self.particles)
    
    def calculate_pressure(self) -> float:
        self.pressure_history.append(self.collisions)
        if len(self.pressure_history) > 60:
            self.pressure_history.pop(0)
        return sum(self.pressure_history) / len(self.pressure_history)
    
    def calculate_total_ke(self) -> float:
        return sum(p.get_kinetic_energy() for p in self.particles)
    
    def calculate_average_ke(self) -> float:
        return self.calculate_total_ke() / len(self.particles)
    
    def handle_collisions(self):
        box_width, box_height, box_x, box_y = self.get_box_dimensions()
        
        for i, particle in enumerate(self.particles):
            particle.x = max(box_x + PARTICLE_RADIUS, min(box_x + box_width - PARTICLE_RADIUS, particle.x))
            particle.y = max(box_y + PARTICLE_RADIUS, min(box_y + box_height - PARTICLE_RADIUS, particle.y))
            
            #collision between particle n wall
            if particle.x - PARTICLE_RADIUS <= box_x:
                particle.dx = abs(particle.dx)
                self.collisions += 1
            elif particle.x + PARTICLE_RADIUS >= box_x + box_width:
                particle.dx = -abs(particle.dx)
                self.collisions += 1
            
            if particle.y - PARTICLE_RADIUS <= box_y:
                particle.dy = abs(particle.dy)
                self.collisions += 1
            elif particle.y + PARTICLE_RADIUS >= box_y + box_height:
                particle.dy = -abs(particle.dy)
                self.collisions += 1
                
            #collision between aprticles
            for j in range(i + 1, len(self.particles)):
                other = self.particles[j]
                dx = other.x - particle.x
                dy = other.y - particle.y
                distance = math.sqrt(dx**2 + dy**2)
                
                if distance < 2 * PARTICLE_RADIUS:
                    angle = math.atan2(dy, dx)
                    particle.dx, other.dx = other.dx, particle.dx
                    particle.dy, other.dy = other.dy, particle.dy
                    
                    overlap = 2 * PARTICLE_RADIUS - distance
                    particle.x -= overlap * math.cos(angle) / 2
                    particle.y -= overlap * math.sin(angle) / 2
                    other.x += overlap * math.cos(angle) / 2
                    other.y += overlap * math.sin(angle) / 2

    def draw(self):
        self.screen.fill(WHITE)  
        
        box_width, box_height, box_x, box_y = self.get_box_dimensions()
        
        shadow_rect = pygame.Rect(
            box_x + CONTAINER_SHADOW_SIZE,
            box_y + CONTAINER_SHADOW_SIZE,
            box_width,
            box_height
        )
        pygame.draw.rect(self.screen, CONTAINER_SHADOW, shadow_rect, border_radius=10)
        
        for i in range(WALL_THICKNESS):
            border_rect = pygame.Rect(
                box_x - i,
                box_y - i,
                box_width + 2*i,
                box_height + 2*i
            )
            gradient_factor = 1 - (i / WALL_THICKNESS) * 0.3
            border_color = (
                int(CONTAINER_BORDER[0] * gradient_factor),
                int(CONTAINER_BORDER[1] * gradient_factor),
                int(CONTAINER_BORDER[2] * gradient_factor)
            )
            pygame.draw.rect(self.screen, border_color, border_rect, 1, border_radius=10)
        
        container_rect = pygame.Rect(box_x, box_y, box_width, box_height)
        pygame.draw.rect(self.screen, CONTAINER_COLOR, container_rect, border_radius=10)
        
        for particle in self.particles:
            for i in range(3):
                glow_radius = PARTICLE_RADIUS + i
                glow_color = (BLUE[0]//2, BLUE[1]//2, BLUE[2]//2)
                pygame.draw.circle(self.screen, glow_color,
                                 (int(particle.x), int(particle.y)), glow_radius)
            
            pygame.draw.circle(self.screen, BLUE, 
                             (int(particle.x), int(particle.y)), PARTICLE_RADIUS)
        
        avg_speed = self.calculate_average_speed()
        pressure = self.calculate_pressure()
        avg_ke = self.calculate_average_ke()
        total_ke = self.calculate_total_ke()
        
        stats = [
            f"Average Speed: {avg_speed:.2f} {self.speed_unit}",
            f"Temperature: {self.temperature:.2f} {self.temp_unit} (×{self.temperature:.1f})",
            f"Pressure: {pressure:.2f} {self.pressure_unit}",
            f"Avg KE: {int(avg_ke)} {self.energy_unit}",
            f"Total KE: {int(total_ke)} {self.energy_unit}"
        ]
        
        for i, text in enumerate(stats):
            surface = self.font.render(text, True, BLACK)
            self.screen.blit(surface, (10, 10 + i * 40))
        
        # Draw buttons
        self.temp_up.draw(self.screen)
        self.temp_down.draw(self.screen)
        self.box_increase.draw(self.screen)
        self.box_decrease.draw(self.screen)
        
        pygame.display.flip()
    
    #fps max 60
    def run(self):
        running = True
        while running:
            self.clock.tick(60)
            self.collisions = 0
            
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_UP:
                        self.adjust_temperature(0.1)
                    elif event.key == pygame.K_DOWN:
                        self.adjust_temperature(-0.1)
                elif event.type == pygame.MOUSEBUTTONDOWN:
                    pos = pygame.mouse.get_pos()
                    if self.temp_up.is_clicked(pos):
                        self.adjust_temperature(0.1)
                    elif self.temp_down.is_clicked(pos):
                        self.adjust_temperature(-0.1)
                    elif self.box_increase.is_clicked(pos):
                        self.adjust_box_size(20)
                    elif self.box_decrease.is_clicked(pos):
                        self.adjust_box_size(-20)
                elif event.type == pygame.VIDEORESIZE:
                    self.handle_resize(event.w, event.h)
            
            #box size
            box_width, box_height, box_x, box_y = self.get_box_dimensions()
            
            #move dlm box
            for particle in self.particles:
                particle.move(box_x, box_y, box_width, box_height)
            
            self.handle_collisions()
            self.draw()
        
        pygame.quit()

if __name__ == "__main__":
    simulator = GasSimulator()
    simulator.run()
