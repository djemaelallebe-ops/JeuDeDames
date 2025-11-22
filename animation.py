import math
import pygame


class Animation:
    def __init__(self, duration: float):
        self.duration = duration
        self.t = 0.0
        self.finished = False

    def update(self, dt: float):
        if self.finished:
            return
        self.t += dt
        if self.t >= self.duration:
            self.t = self.duration
            self.finished = True

    def progress(self) -> float:
        return min(1.0, max(0.0, self.t / self.duration))


def _specular_color(is_night: bool):
    return (255, 255, 255, 70) if not is_night else (220, 220, 255, 50)


def draw_piece_shape(
    surface: pygame.Surface,
    center,
    piece_value: int,
    cell_size: int,
    colors,
    is_night: bool,
    font,
):
    cx, cy = center
    base_col = colors["piece_white"] if piece_value > 0 else colors["piece_black"]

    # Shadow
    shadow = pygame.Surface((cell_size, cell_size), pygame.SRCALPHA)
    pygame.draw.circle(
        shadow,
        (0, 0, 0, 120),
        (cell_size // 2 + 3, cell_size // 2 + 5),
        cell_size // 2 - 20,
    )
    surface.blit(shadow, (cx - cell_size // 2, cy - cell_size // 2))

    main = pygame.Surface((cell_size, cell_size), pygame.SRCALPHA)
    pygame.draw.circle(main, base_col, (cell_size // 2, cell_size // 2), cell_size // 2 - 16)

    # texture douce
    texture = pygame.Surface((cell_size, cell_size), pygame.SRCALPHA)
    for y in range(0, cell_size, 6):
        for x in range(0, cell_size, 6):
            if (x * 3 + y * 5) % 19 == 0:
                pygame.draw.circle(texture, (255, 255, 255, 18), (x, y), 1)
    main.blit(texture, (0, 0))

    # specular
    specular = pygame.Surface((cell_size, cell_size), pygame.SRCALPHA)
    pygame.draw.ellipse(
        specular,
        _specular_color(is_night),
        (cell_size // 2 - 16, cell_size // 2 - 26, 28, 14),
    )
    specular = pygame.transform.rotate(specular, -25)
    main.blit(specular, (-6, 0))

    # anneaux
    pygame.draw.circle(main, (0, 0, 0, 90), (cell_size // 2, cell_size // 2), cell_size // 2 - 16, 2)
    pygame.draw.circle(main, (255, 255, 255, 50), (cell_size // 2, cell_size // 2), cell_size // 2 - 22, 1)

    surface.blit(main, (cx - cell_size // 2, cy - cell_size // 2))

    if abs(piece_value) == 2:
        crown = font.render("♕", True, colors["crown"])
        rect = crown.get_rect(center=(cx, cy))
        surface.blit(crown, rect)


class MoveAnimation(Animation):
    def __init__(
        self,
        start_cell,
        end_cell,
        piece_value,
        cell_size,
        offset_y,
        theme_colors,
        is_night: bool,
        font,
        duration: float = 0.15,
    ):
        super().__init__(duration)
        self.start_cell = start_cell
        self.end_cell = end_cell
        self.cell_size = cell_size
        self.offset_y = offset_y
        self.theme_colors = theme_colors
        self.is_night = is_night
        self.font = font

        sx, sy = start_cell
        ex, ey = end_cell
        self.start_pos = (
            sx * cell_size + cell_size // 2,
            offset_y + sy * cell_size + cell_size // 2,
        )
        self.end_pos = (
            ex * cell_size + cell_size // 2,
            offset_y + ey * cell_size + cell_size // 2,
        )
        self.piece_value = piece_value

    @property
    def target_cell(self):
        return self.end_cell

    def draw(self, screen):
        p = self.progress()
        x = self.start_pos[0] + (self.end_pos[0] - self.start_pos[0]) * p
        y = self.start_pos[1] + (self.end_pos[1] - self.start_pos[1]) * p
        draw_piece_shape(
            screen,
            (int(x), int(y)),
            self.piece_value,
            self.cell_size,
            self.theme_colors,
            self.is_night,
            self.font,
        )


class SelectPulseAnimation(Animation):
    def __init__(self, cell, cell_size, offset_y, color, duration: float = 0.15):
        super().__init__(duration)
        self.cell = cell
        self.cell_size = cell_size
        self.offset_y = offset_y
        self.color = color

    def draw(self, screen):
        p = self.progress()
        scale = 1.0 + 0.1 * math.sin(p * math.pi)
        r, c = self.cell
        cx = c * self.cell_size + self.cell_size // 2
        cy = self.offset_y + r * self.cell_size + self.cell_size // 2
        radius = int((self.cell_size // 2 - 10) * scale)
        surface = pygame.Surface((self.cell_size, self.cell_size), pygame.SRCALPHA)
        pygame.draw.circle(surface, (*self.color, 60), (self.cell_size // 2, self.cell_size // 2), radius, 3)
        screen.blit(surface, (c * self.cell_size, self.offset_y + r * self.cell_size))


class CapturePulseAnimation(Animation):
    def __init__(self, cell, cell_size, offset_y, color, duration: float = 1.2):
        super().__init__(duration)
        self.cell = cell
        self.cell_size = cell_size
        self.offset_y = offset_y
        self.color = color

    def update(self, dt: float):
        # boucle continue tant que présente dans la liste
        if self.finished:
            return
        self.t = (self.t + dt) % self.duration

    def draw(self, screen):
        p = self.progress()
        pulse = 0.6 + 0.4 * math.sin(p * math.pi * 2)
        alpha = int(70 + 50 * pulse)
        radius = int((self.cell_size // 2 - 8) * (0.8 + 0.2 * pulse))
        r, c = self.cell
        cx = c * self.cell_size + self.cell_size // 2
        cy = self.offset_y + r * self.cell_size + self.cell_size // 2
        surf = pygame.Surface((self.cell_size, self.cell_size), pygame.SRCALPHA)
        pygame.draw.circle(surf, (*self.color, alpha), (self.cell_size // 2, self.cell_size // 2), radius, 2)
        screen.blit(surf, (c * self.cell_size, self.offset_y + r * self.cell_size))


class LastMoveFadeAnimation(Animation):
    def __init__(self, cells, duration: float = 0.4):
        super().__init__(duration)
        self.cells = cells

    def draw(self, screen):
        alpha = int(90 * (1 - self.progress()))
        if alpha <= 0:
            return
        for (x, y, size) in self.cells:
            surf = pygame.Surface((size, size), pygame.SRCALPHA)
            pygame.draw.rect(surf, (0, 150, 255, alpha), (4, 4, size - 8, size - 8), border_radius=8)
            screen.blit(surf, (x, y))


class PromotionGlowAnimation(Animation):
    def __init__(self, cell, cell_size, offset_y, color, duration: float = 0.3):
        super().__init__(duration)
        self.cell = cell
        self.cell_size = cell_size
        self.offset_y = offset_y
        self.color = color

    def draw(self, screen):
        p = self.progress()
        r, c = self.cell
        cx = c * self.cell_size + self.cell_size // 2
        cy = self.offset_y + r * self.cell_size + self.cell_size // 2
        radius = int((self.cell_size // 2) * (0.5 + 0.7 * p))
        alpha = int(160 * (1 - p))
        surf = pygame.Surface((self.cell_size * 2, self.cell_size * 2), pygame.SRCALPHA)
        pygame.draw.circle(
            surf,
            (*self.color, alpha),
            (self.cell_size, self.cell_size),
            radius,
            4,
        )
        screen.blit(surf, (cx - self.cell_size, cy - self.cell_size))


class ShakeAnimation(Animation):
    def __init__(self, cell, amplitude: int, duration: float = 0.12):
        super().__init__(duration)
        self.cell = cell
        self.amplitude = amplitude

    def offset(self):
        p = self.progress()
        return (
            int(self.amplitude * math.sin(p * math.pi * 10)),
            int(self.amplitude * 0.4 * math.sin(p * math.pi * 8)),
        )

    def draw(self, screen):
        # le shake est appliqué via l'offset ; aucun dessin direct nécessaire
        return


class StartupFadeAnimation(Animation):
    def __init__(self, duration: float = 0.4):
        super().__init__(duration)

    def update(self, dt: float):
        # garder finished True à la fin pour retrait normal
        super().update(dt)

    def draw(self, screen):
        base = screen.copy()
        p = self.progress()
        scale = 1.04 - 0.04 * p
        w, h = base.get_size()
        sw, sh = int(w * scale), int(h * scale)
        scaled = pygame.transform.smoothscale(base, (sw, sh))
        screen.fill((0, 0, 0))
        screen.blit(scaled, ((w - sw) // 2, (h - sh) // 2))
        overlay = pygame.Surface((w, h), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, int(180 * (1 - p))))
        screen.blit(overlay, (0, 0))


class EndGameAnimation(Animation):
    def __init__(self, winner_text: str, screen_size, text_color, duration: float = 1.8):
        super().__init__(duration)
        self.winner_text = winner_text
        self.screen_size = screen_size
        self.text_color = text_color
        self.button_rect = None
        self.font_cache = pygame.font.SysFont("segoe ui", 26)

    def update(self, dt: float):
        # l'animation reste active pour conserver l'overlay
        if self.t < self.duration:
            self.t = min(self.duration, self.t + dt)

    def draw(self, screen):
        w, h = self.screen_size
        p = self.progress()
        overlay = pygame.Surface((w, h), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, int(160 * p)))
        screen.blit(overlay, (0, 0))

        center = (w // 2, h // 2 - 20)
        halo = pygame.Surface((w, h), pygame.SRCALPHA)
        pulse = 0.5 + 0.5 * math.sin(p * math.pi * 2)
        radius = int(min(w, h) * 0.22 * (0.9 + 0.2 * pulse))
        pygame.draw.circle(halo, (*self.text_color, int(45 * (0.6 + 0.4 * pulse))), center, radius, 3)
        screen.blit(halo, (0, 0))

        title = self.font_cache.render(self.winner_text, True, self.text_color)
        title_rect = title.get_rect(center=center)
        screen.blit(title, title_rect)

        btn_width, btn_height = 180, 42
        self.button_rect = pygame.Rect(0, 0, btn_width, btn_height)
        self.button_rect.center = (w // 2, h // 2 + 36)
        btn_surf = pygame.Surface((btn_width, btn_height), pygame.SRCALPHA)
        pygame.draw.rect(btn_surf, (*self.text_color, 40), btn_surf.get_rect(), border_radius=10)
        pygame.draw.rect(btn_surf, (*self.text_color, 90), btn_surf.get_rect(), 2, border_radius=10)
        label = self.font_cache.render("Rejouer", True, self.text_color)
        btn_surf.blit(label, label.get_rect(center=btn_surf.get_rect().center))
        screen.blit(btn_surf, self.button_rect.topleft)

