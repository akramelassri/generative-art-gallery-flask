import pygame
import pygame_gui
import draw
import os
import datetime
import random

class State():
    def __init__(self, screen, theme_path):
        self._manager = pygame_gui.UIManager(screen.get_size(), theme_path=theme_path)
    def make_ui(self, screen):
        pass

    def handle_events(self, screen, events, pos):
        pass

    def draw_ui(self, screen, time_delta, pos):
        self._manager.update(time_delta)
        self._manager.draw_ui(screen)

class HomePageState(State):
    def __init__(self, screen, theme_path):
        super().__init__(screen, theme_path)

    def make_ui(self, screen):
        self._side_pannel_menu = pygame_gui.elements.UIPanel(
            relative_rect=pygame.Rect(0, 0, 70, screen.get_height()),
            manager=self._manager,
            object_id="side_menu"
        )
            
        self._home_icon = pygame.image.load("./draw/assets/home-icon.png")
        self._gallery_icon = pygame.image.load("./draw/assets/pictures-icon.png")
        self._app_icon = pygame.image.load("./draw/assets/four-squares-icon.png")

        self._home_icon_panel = pygame_gui.elements.UIPanel(
            relative_rect=pygame.Rect(0, 20, 50, 60),
            manager=self._manager,
            container=self._side_pannel_menu,
            anchors={'centerx': 'centerx', 'top': 'top'}
        )
            
        self._home_icon_image = pygame_gui.elements.UIImage(
            relative_rect=pygame.Rect(3, 0, 32, 32),
            image_surface=self._home_icon,
            manager=self._manager,
            container=self._home_icon_panel
        )

        self._home_icon_txt = pygame_gui.elements.UILabel(
            relative_rect=pygame.Rect(1, 3, -1, -1),
            text="Home",
            anchors={'top': 'top', 'top_target': self._home_icon_image},
            container=self._home_icon_panel
        )

        self._gallery_icon_panel = pygame_gui.elements.UIPanel(
            relative_rect=pygame.Rect(0, 20, 55, 60),
            manager=self._manager,
            container=self._side_pannel_menu,
            anchors={'centerx': 'centerx', 'top': 'top', 'top_target': self._home_icon_panel}
        )
            
        self._gallery_icon_image = pygame_gui.elements.UIImage(
            relative_rect=pygame.Rect(3, 0, 32, 32),
            image_surface=self._gallery_icon,
            manager=self._manager,
            container=self._gallery_icon_panel
        )

        self._gallery_icon_txt = pygame_gui.elements.UILabel(
            relative_rect=pygame.Rect(0, 3, -1, -1),
            text="Gallery",
            anchors={'top': 'top', 'top_target': self._gallery_icon_image},
            container=self._gallery_icon_panel
        )

        self._app_icon_panel = pygame_gui.elements.UIPanel(
            relative_rect=pygame.Rect(0, 20, 50, 60),
            manager=self._manager,
            container=self._side_pannel_menu,
            anchors={'centerx': 'centerx', 'top': 'top', 'top_target': self._gallery_icon_panel}
        )
            
        self._app_icon_image = pygame_gui.elements.UIImage(
            relative_rect=pygame.Rect(3, 0, 32, 32),
            image_surface=self._app_icon,
            manager=self._manager,
            container=self._app_icon_panel
        )

        self._app_icon_txt = pygame_gui.elements.UILabel(
            relative_rect=pygame.Rect(3, 3, -1, -1),
            text="Apps",
            anchors={'top': 'top', 'top_target': self._app_icon_image},
            container=self._app_icon_panel
        )
            
        self._apps_txt = pygame_gui.elements.UILabel(
            relative_rect=pygame.Rect(20, 20, -1, -1),
            text="Apps",
            anchors={'top': 'top', 'left': 'left', 'left_target': self._side_pannel_menu},
            object_id="custom_txt"
        )

        self._draw_icon_button = pygame_gui.elements.UIButton(
            relative_rect=pygame.Rect(20, 20, 100, 100),
            manager=self._manager,
            text="",
            anchors={'left': 'left', 'top': 'top', 'top_target': self._apps_txt, 'left_target': self._side_pannel_menu},
            object_id="draw_app"
        )
        self._data_icon_button = pygame_gui.elements.UIButton(
            relative_rect=pygame.Rect(20, 20, 100, 100),
            manager=self._manager,
            text="",
            anchors={'left': 'left', 'top': 'top', 'top_target': self._apps_txt, 'left_target': self._draw_icon_button},
            object_id="data_app"
        )
        self._image_process_icon_button = pygame_gui.elements.UIButton(
            relative_rect=pygame.Rect(20, 20, 100, 100),
            manager=self._manager,
            text="",
            anchors={'left': 'left', 'top': 'top', 'top_target': self._apps_txt, 'left_target': self._data_icon_button},
            object_id="image_app"
        )
        self._audio_process_icon_button = pygame_gui.elements.UIButton(
            relative_rect=pygame.Rect(20, 20, 100, 100),
            manager=self._manager,
            text="",
            anchors={'left': 'left', 'top': 'top', 'top_target': self._apps_txt, 'left_target': self._image_process_icon_button},
            object_id="audio_app"
        )

        self._recent_art_txt = pygame_gui.elements.UILabel(
            relative_rect=pygame.Rect(20, 20, -1, -1),
            text="Recent Artworks",
            manager=self._manager,
            anchors={'top': 'top', 'left': 'left', 'left_target': self._side_pannel_menu, 'top_target': self._draw_icon_button},
            object_id="custom_txt"
        )

    def handle_events(self, screen, events, pos):
        for event in events:
            if event.type == pygame.QUIT:
                return 'quit'
            if event.type == pygame.VIDEORESIZE:
                self._manager.set_window_resolution(screen.get_size())
            if event.type == pygame_gui.UI_BUTTON_PRESSED:
                if event.ui_element == self._draw_icon_button:
                    return 'draw_app'
            self._manager.process_events(event)

class GalleryPageState(State):
    pass

class AppsPageState(State):
    pass

class DrawAppState(State):
    def __init__(self, screen, theme_path):
        super().__init__(screen, theme_path)
        self.drawing_canva = draw.Canva()
        self.drawing_mode = False
        self.select_mode = True
        self._previewed_shape = draw.Circle((0, 0), 20, (255, 0, 0))
        self._selected_shape = None
        self._drag_offset = None

    def make_ui(self, screen):
        # Main side panel (using the same theme as other buttons)
        self._side_pannel_menu = pygame_gui.elements.UIPanel(
            relative_rect=pygame.Rect(0, 0, 70, screen.get_height()),
            manager=self._manager,
            anchors={'top': 'top', 'left': 'left'}
        )
        self._color_picker = pygame_gui.elements.UIDropDownMenu(
            options_list=["test", "testttt"],
            starting_option='test',
            relative_rect=pygame.Rect(80, 20, 100, 30),
            manager=self._manager,
        )
        self._menu_button = pygame_gui.elements.UIButton(
            relative_rect=pygame.Rect(10, 10, 32, 32),
            manager=self._manager,
            text="",
            container=self._side_pannel_menu,
            object_id="menu_button"
        )
        self._select_button = pygame_gui.elements.UIButton(
            relative_rect=pygame.Rect(10, 50, 32, 32),
            manager=self._manager,
            text="",
            container=self._side_pannel_menu,
            object_id="select_button"
        )
        self._shapes_button = pygame_gui.elements.UIButton(
            relative_rect=pygame.Rect(10, 90, 32, 32),
            manager=self._manager,
            text="",
            container=self._side_pannel_menu,
            object_id="shapes_button"
        )
        # Save button (saves only the drawing canvas)
        self._save_button = pygame_gui.elements.UIButton(
            relative_rect=pygame.Rect(10, 130, 32, 32),
            manager=self._manager,
            text="Save",
            container=self._side_pannel_menu,
            object_id="save_button"
        )
        # Pattern buttons placed in the same side panel
        self._circular_button = pygame_gui.elements.UIButton(
            relative_rect=pygame.Rect(10, 170, 32, 32),
            manager=self._manager,
            text="Circ",
            container=self._side_pannel_menu,
            object_id="circular_button"
        )
        self._spirograph_button = pygame_gui.elements.UIButton(
            relative_rect=pygame.Rect(10, 210, 32, 32),
            manager=self._manager,
            text="Spiro",
            container=self._side_pannel_menu,
            object_id="spirograph_button"
        )
        self._rose_button = pygame_gui.elements.UIButton(
            relative_rect=pygame.Rect(10, 250, 32, 32),
            manager=self._manager,
            text="Rose",
            container=self._side_pannel_menu,
            object_id="rose_button"
        )
        self._lissajous_button = pygame_gui.elements.UIButton(
            relative_rect=pygame.Rect(10, 290, 32, 32),
            manager=self._manager,
            text="Lissa",
            container=self._side_pannel_menu,
            object_id="lissajous_button"
        )
        self._fourier_button = pygame_gui.elements.UIButton(
            relative_rect=pygame.Rect(10, 330, 32, 32),
            manager=self._manager,
            text="Four",
            container=self._side_pannel_menu,
            object_id="fourier_button"
        )

    def draw_ui(self, screen, time_delta, pos):            
        screen.fill((110, 120, 110))
        self._manager.update(time_delta)
        if self.drawing_mode:
            self._previewed_shape.set_pos(pos)
            self._previewed_shape.draw(screen)
        if self.select_mode and self._selected_shape is not None:
            self._selected_shape.highlight_shape(screen)
        self.drawing_canva.render(screen)
        self._manager.draw_ui(screen)

    def handle_events(self, screen, events, pos):
        for event in events:
            if event.type == pygame.QUIT:
                return 'quit'
            if event.type == pygame.VIDEORESIZE:
                self._manager.set_window_resolution(screen.get_size())
            if event.type == pygame_gui.UI_BUTTON_PRESSED:
                # Switch modes
                if event.ui_element == self._shapes_button:
                    self.drawing_mode = True
                    self.select_mode = False
                    self._shapes_button.disable()
                    self._menu_button.enable()
                    self._select_button.enable()
                elif event.ui_element == self._select_button:
                    self.drawing_mode = False
                    self.select_mode = True
                    self._shapes_button.enable()
                    self._menu_button.enable()
                    self._select_button.disable()
                # Save button (save only the drawing canvas)
                elif event.ui_element == self._save_button:
                    save_dir = "./static/gallery"
                    os.makedirs(save_dir, exist_ok=True)
                    filename = os.path.join(save_dir, "drawing_" + datetime.datetime.now().strftime("%Y%m%d_%H%M%S") + ".png")
                    canvas_surface = pygame.Surface(screen.get_size())
                    canvas_surface.fill((110, 120, 110))
                    self.drawing_canva.render(canvas_surface)
                    pygame.image.save(canvas_surface, filename)
                # Pattern buttons (generate a pattern and add as an image shape at a random position)
                elif event.ui_element == self._circular_button:
                    pattern_surf = draw.generate_circular_pattern()
                    center = (random.randint(0, screen.get_width()), random.randint(0, screen.get_height()))
                    img_shape = draw.ImageShape(center, pattern_surf)
                    self.drawing_canva.add_shape(img_shape)
                elif event.ui_element == self._spirograph_button:
                    pattern_surf = draw.generate_spirograph_pattern()
                    center = (random.randint(0, screen.get_width()), random.randint(0, screen.get_height()))
                    img_shape = draw.ImageShape(center, pattern_surf)
                    self.drawing_canva.add_shape(img_shape)
                elif event.ui_element == self._rose_button:
                    pattern_surf = draw.generate_rosecurves_pattern()
                    center = (random.randint(0, screen.get_width()), random.randint(0, screen.get_height()))
                    img_shape = draw.ImageShape(center, pattern_surf)
                    self.drawing_canva.add_shape(img_shape)
                elif event.ui_element == self._lissajous_button:
                    pattern_surf = draw.generate_lissajous_pattern()
                    center = (random.randint(0, screen.get_width()), random.randint(0, screen.get_height()))
                    img_shape = draw.ImageShape(center, pattern_surf)
                    self.drawing_canva.add_shape(img_shape)
                elif event.ui_element == self._fourier_button:
                    pattern_surf = draw.generate_fourier_pattern()
                    center = (random.randint(0, screen.get_width()), random.randint(0, screen.get_height()))
                    img_shape = draw.ImageShape(center, pattern_surf)
                    self.drawing_canva.add_shape(img_shape)

            if self._side_pannel_menu.get_abs_rect().collidepoint(pos) and self.drawing_mode:
                self.drawing_mode = False
            elif (not self._side_pannel_menu.get_abs_rect().collidepoint(pos)) and not(self._shapes_button.is_enabled):
                self.drawing_mode = True

            if self.drawing_mode:
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_LSHIFT:
                        self._previewed_shape.resize(2)
                    elif event.key == pygame.K_LCTRL:
                        self._previewed_shape.resize(1 / 2)
                    elif event.key == pygame.K_r:
                        self._previewed_shape.rotate(45)
                    elif event.key == pygame.K_c:
                        draw.change_color(draw.list_colors, self._previewed_shape)
                if event.type == pygame.MOUSEBUTTONDOWN:
                    if event.button == 1:
                        new_shape = self._previewed_shape.copy()
                        self.drawing_canva.add_shape(new_shape)
                    if event.button == 3:
                        self._previewed_shape = draw.change_shapes(pos, self._previewed_shape)
            # Select Mode events (drag to move shape)
            if self.select_mode:
                if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                    self._selected_shape = None
                    self._drag_offset = None
                    for shape in self.drawing_canva._shapes:
                        if shape.contains_point(pos):
                            self._selected_shape = shape
                            self._drag_offset = (pos[0] - shape._center[0], pos[1] - shape._center[1])
                            break
                elif event.type == pygame.MOUSEMOTION:
                    if (self._selected_shape is not None and 
                        self._drag_offset is not None and 
                        pygame.mouse.get_pressed()[0]):
                        new_center = (pos[0] - self._drag_offset[0], pos[1] - self._drag_offset[1])
                        self._selected_shape.set_pos(new_center)
                elif event.type == pygame.MOUSEBUTTONUP and event.button == 1:
                    self._drag_offset = None
            self._manager.process_events(event)
                
class DataAppState(State):
    pass

class ImageAppState(State):
    pass

class AudioAppState(State):
    pass

class StateManager():
    def __init__(self, screen):
        self._states = {
            'home_page': HomePageState(screen, "./draw/themes/home_panel.json"),
            'draw_app': DrawAppState(screen, "./draw/themes/draw_app.json"),
        }
        self._current_state = self._states['home_page']

    def change_screen(self, screen_name):
        self._current_state = self._states[screen_name]

    def make_ui(self, screen):
        for state in self._states:
            self._states[state].make_ui(screen)

    def handle_events(self, screen, events, pos):
        result = self._current_state.handle_events(screen, events, pos)
        if result is not None:
            if result == 'quit':
                return False
            else:
                self.change_screen(result)
                return True
        else:
            return True

    def draw_ui(self, screen, time_delta, pos):
        self._current_state.draw_ui(screen, time_delta, pos)
