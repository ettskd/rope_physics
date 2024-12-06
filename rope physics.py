import pygame
import math

# Initialize Pygame
pygame.init()

# Screen dimensions
WIDTH, HEIGHT = 800, 600
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Interactive Physics Rope Simulation")

# Clock for controlling frame rate
clock = pygame.time.Clock()
FPS = 60

# Colors
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)

# Rope parameters
NUM_PARTICLES = 20
PARTICLE_RADIUS = 5
ROPE_LENGTH = 300
GRAVITY = 0.5
FRICTION = 0.99
ANCHOR = (WIDTH // 2, 50)  # Fixed anchor point

class Particle:
    def __init__(self, x, y, fixed=False):
        self.x = x
        self.y = y
        self.prev_x = x
        self.prev_y = y
        self.fixed = fixed  # If fixed, the particle doesn't move

    def apply_gravity(self):
        if not self.fixed:
            self.y += GRAVITY

    def update_position(self):
        if not self.fixed:
            velocity_x = (self.x - self.prev_x) * FRICTION
            velocity_y = (self.y - self.prev_y) * FRICTION
            self.prev_x = self.x
            self.prev_y = self.y
            self.x += velocity_x
            self.y += velocity_y

    def constrain_within_bounds(self):
        self.x = max(PARTICLE_RADIUS, min(WIDTH - PARTICLE_RADIUS, self.x))
        self.y = max(PARTICLE_RADIUS, min(HEIGHT - PARTICLE_RADIUS, self.y))

class Rope:
    def __init__(self, anchor, length, num_particles):
        self.particles = []
        self.segment_length = length / (num_particles - 1)

        # Create particles
        for i in range(num_particles):
            x = anchor[0]
            y = anchor[1] + i * self.segment_length
            fixed = (i == 0)  # Anchor point is fixed
            self.particles.append(Particle(x, y, fixed))

    def update(self):
        # Apply gravity and update positions
        for particle in self.particles:
            particle.apply_gravity()
            particle.update_position()

        # Solve constraints
        for _ in range(5):  # Iterate to make the rope stable
            self.solve_constraints()

    def solve_constraints(self):
        for i in range(len(self.particles) - 1):
            p1 = self.particles[i]
            p2 = self.particles[i + 1]

            # Calculate distance and correction
            dx = p2.x - p1.x
            dy = p2.y - p1.y
            distance = math.sqrt(dx**2 + dy**2)
            error = self.segment_length - distance
            correction = error / distance * 0.5

            if not p1.fixed:
                p1.x -= correction * dx
                p1.y -= correction * dy
            if not p2.fixed:
                p2.x += correction * dx
                p2.y += correction * dy

    def render(self, screen):
        for i in range(len(self.particles) - 1):
            p1 = self.particles[i]
            p2 = self.particles[i + 1]
            pygame.draw.line(screen, WHITE, (p1.x, p1.y), (p2.x, p2.y), 2)
        for particle in self.particles:
            pygame.draw.circle(screen, WHITE, (int(particle.x), int(particle.y)), PARTICLE_RADIUS)

# Create rope instance
rope = Rope(ANCHOR, ROPE_LENGTH, NUM_PARTICLES)

# Interaction variables
dragging_particle = None

# Game loop
running = True
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

        # Mouse press: Check if a particle is clicked
        if event.type == pygame.MOUSEBUTTONDOWN:
            mouse_x, mouse_y = event.pos
            for particle in rope.particles:
                distance = math.sqrt((particle.x - mouse_x) ** 2 + (particle.y - mouse_y) ** 2)
                if distance <= PARTICLE_RADIUS:
                    dragging_particle = particle
                    break

        # Mouse release: Stop dragging
        if event.type == pygame.MOUSEBUTTONUP:
            dragging_particle = None

    # Update dragging particle position
    if dragging_particle:
        mouse_x, mouse_y = pygame.mouse.get_pos()
        dragging_particle.x = mouse_x
        dragging_particle.y = mouse_y

    # Update rope
    rope.update()

    # Draw everything
    screen.fill(BLACK)
    rope.render(screen)
    pygame.display.flip()

    # Cap the frame rate
    clock.tick(FPS)

pygame.quit()
