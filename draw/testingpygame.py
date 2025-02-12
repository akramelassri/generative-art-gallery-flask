import pygame
import screens
import draw

# TO DO 
    # NOT ALLOW INSERT AND MODIFY
def main():
    # Initialize Pygame
    pygame.init()

    # Setting up window icon (linux specific)
    win_icon = pygame.image.load("./draw/assets/paint-brush-drawing-icon.png")
    pygame.display.set_icon(win_icon)

    # Set up the screen
    display_info = pygame.display.Info()
    screen_width = int(display_info.current_w)
    screen_height = int(display_info.current_h)
    screen = pygame.display.set_mode((screen_width, screen_height), pygame.RESIZABLE)
    pygame.display.set_caption("Generative Art Project")

    # Setting up clock
    clock = pygame.time.Clock()

    # Setting background color for main page
    background_color = (239, 243, 234)

    # Setting up canva
    canva = draw.Canva()
    
    ui_manager = screens.StateManager(screen)

    # Main loop
    running = True

    ui_manager.make_ui(screen)

    while running:

        time_delta = clock.tick(60) / 1000

        pos = pygame.mouse.get_pos()
        
        events = pygame.event.get()

        running = ui_manager.handle_events(screen,events,pos)

        # Fill the screen with the background color
        screen.fill(background_color)
        
        ui_manager.draw_ui(screen,time_delta,pos)

        # Update the display
        pygame.display.flip()


    # Quit Pygame
    pygame.quit()
    
def draw_circular_shapes():
    pass

def draw_spirograph_patterns():
    pass

def draw_rosecurves_patterns():
    pass

def draw_lissajouscurves_patterns():
    pass

def draw_fourier_cycles():
    pass

def main_menu():
    pass

if __name__ == "__main__":
    main()
