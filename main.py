import math
import pygame
from typing import List, Optional, Tuple

from engine import Engine, color, get_captures, get_simple_moves
from ai import AI
from theme import DAY, NIGHT
from tutorial import Tutorial
from animation import (
    Animation,
    CapturePulseAnimation,
    EndGameAnimation,
    LastMoveFadeAnimation,
    MoveAnimation,
    PromotionGlowAnimation,
    SelectPulseAnimation,
    ShakeAnimation,
    StartupFadeAnimation,
    draw_piece_shape,
)

current_theme = DAY


# CONSTANTES UI
CELL = 80
WIDTH = CELL * 8
HEIGHT = CELL * 8 + 60  # espace pour overlay
FPS = 60

HINT_SOURCE = (0, 130, 255)
HINT_TARGET = (0, 200, 255)
CAPTURE_PULSE_COLOR = (0, 170, 150)
SHAKE_AMPLITUDE = 4
OFFSET_Y = 50


def format_time(t: float) -> str:
    m = int(t // 60)
    s = int(t % 60)
    return f"{m:02d}:{s:02d}"


def has_legal_moves(engine: Engine) -> bool:
    capture_available = engine._any_capture_available()
    for r in range(8):
        for c in range(8):
            p = engine.board.grid[r][c]
            if color(p) != engine.turn:
                continue
            if capture_available:
                if get_captures(engine.board, r, c):
                    return True
            else:
                if get_simple_moves(engine.board, r, c):
                    return True
    return False


def capture_cells(engine: Engine) -> List[Tuple[int, int]]:
    cells = []
    if not engine._any_capture_available():
        return cells
    for r in range(8):
        for c in range(8):
            p = engine.board.grid[r][c]
            if color(p) != engine.turn:
                continue
            if get_captures(engine.board, r, c):
                cells.append((r, c))
    return cells


def draw_board(
    screen,
    engine: Engine,
    selected: Optional[Tuple[int, int]],
    moves: List[Tuple[int, int]],
    hint,
    hint_alpha,
    font,
    timer_white,
    timer_black,
    animations: List[Animation],
    moving_targets: set,
    shake_offsets,
):
    BG_COLOR = current_theme["bg"]
    OVERLAY_COLOR = current_theme["overlay"]
    BOARD_LIGHT = current_theme["light"]
    BOARD_DARK = current_theme["dark"]
    TEXT_COLOR = current_theme["text"]
    WHITE_PIECE = current_theme["piece_white"]
    BLACK_PIECE = current_theme["piece_black"]
    CROWN_COLOR = current_theme["crown"]
    is_night = current_theme == NIGHT

    # fond général
    screen.fill(BG_COLOR)

    # OVERLAY TOP BAR
    pygame.draw.rect(screen, OVERLAY_COLOR, pygame.Rect(0, 0, WIDTH, 50))

    # Tour du joueur
    turn_text = "Tour des Blancs" if engine.turn == 1 else "Tour des Noirs"
    tr = font.render(turn_text, True, TEXT_COLOR)
    screen.blit(tr, (10, 12))

    # Timers
    txt_w = font.render(f"Blancs : {format_time(timer_white)}", True, TEXT_COLOR)
    txt_b = font.render(f"Noirs   : {format_time(timer_black)}", True, TEXT_COLOR)
    screen.blit(txt_w, (WIDTH - 230, 10))
    screen.blit(txt_b, (WIDTH - 230, 28))

    # ZONE DU PLATEAU
    offset_y = OFFSET_Y

    for r in range(8):
        for c in range(8):
            x = c * CELL
            y = offset_y + r * CELL
            is_dark = (r + c) % 2 == 1
            base = BOARD_DARK if is_dark else BOARD_LIGHT
            pygame.draw.rect(screen, base, (x, y, CELL, CELL))

            # léger shading sur cases foncées
            if is_dark:
                pygame.draw.rect(screen, (0, 0, 0, 40), (x + 2, y + 2, CELL - 4, CELL - 4), 1)

            # highlight sélection
            if selected == (r, c):
                surf = pygame.Surface((CELL, CELL), pygame.SRCALPHA)
                pygame.draw.rect(surf, (0, 200, 255, 90), (3, 3, CELL - 6, CELL - 6), border_radius=10)
                pygame.draw.rect(surf, (255, 255, 255, 50), (8, 8, CELL - 16, CELL - 16), border_radius=10)
                screen.blit(surf, (x, y))

    # possible moves
    for (mr, mc) in moves:
        cx = mc * CELL + CELL // 2
        cy = offset_y + mr * CELL + CELL // 2
        pygame.draw.circle(screen, (40, 200, 120), (cx, cy), 9)
        pygame.draw.circle(screen, (160, 255, 200), (cx, cy), 4)

    # pions avec ombres
    for r in range(8):
        for c in range(8):
            piece = engine.board.grid[r][c]
            if piece == 0:
                continue

            if (r, c) in moving_targets:
                continue

            dx, dy = shake_offsets.get((r, c), (0, 0))
            cx = c * CELL + CELL // 2 + dx
            cy = offset_y + r * CELL + CELL // 2 + dy

            draw_piece_shape(
                screen,
                (cx, cy),
                piece,
                CELL,
                {
                    "piece_white": WHITE_PIECE,
                    "piece_black": BLACK_PIECE,
                    "crown": CROWN_COLOR,
                },
                is_night,
                font,
            )

    # HINT animé
    if hint and hint_alpha > 0:
        sr, sc, tr, tc = hint

        t = pygame.time.get_ticks() / 1000
        pulse = 0.5 + 0.5 * math.sin(4 * t)

        a_src = int(hint_alpha * (0.7 + 0.3 * pulse))
        a_trg = int(hint_alpha * (0.5 + 0.5 * pulse))

        # halo source
        sx = sc * CELL
        sy = offset_y + sr * CELL
        surf = pygame.Surface((CELL, CELL), pygame.SRCALPHA)
        pygame.draw.circle(surf, (0, 140, 255, a_src), (CELL // 2, CELL // 2), CELL // 2 - 6, 3)
        screen.blit(surf, (sx, sy))

        # halo cible
        cx = tc * CELL + CELL // 2
        cy = offset_y + tr * CELL + CELL // 2
        pygame.draw.circle(screen, (0, 200, 255, a_trg), (cx, cy), 15, 3)

        # texte indicatif
        lbl = font.render("Suggestion de coup (H)", True, (0, 190, 255))
        screen.blit(lbl, (10, HEIGHT - 24))

    if current_theme == NIGHT:
        veil = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
        t = pygame.time.get_ticks() / 1000
        alpha = int(18 + 4 * math.sin(t * 0.5))
        veil.fill((20, 15, 13, alpha))
        screen.blit(veil, (0, 0))

    for anim in animations:
        anim.draw(screen)


def main():
    global current_theme
    pygame.init()
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption("Jeu de Dames – Premium UI")

    font = pygame.font.SysFont("segoe ui", 20)
    clock = pygame.time.Clock()

    engine = Engine()
    ai = AI(engine, level=1)
    ai_plays = -1  # -1 = noirs, 1 = blancs
    animations: List[Animation] = [StartupFadeAnimation()]
    end_animation: Optional[EndGameAnimation] = None
    tutorial = Tutorial()
    tutorial.start()

    selected = None
    moves = []

    last_move = None

    hint = None
    hint_alpha = 0

    timer_white = 0.0
    timer_black = 0.0

    game_over = False

    def reset_game():
        nonlocal engine, ai, selected, moves, last_move, hint, hint_alpha, timer_white, timer_black, animations, end_animation, game_over
        level = ai.level
        engine = Engine()
        ai = AI(engine, level=level)
        selected = None
        moves = []
        last_move = None
        hint = None
        hint_alpha = 0
        timer_white = 0.0
        timer_black = 0.0
        animations = [StartupFadeAnimation()]
        end_animation = None
        game_over = False

    running = True

    while running:
        dt = clock.tick(FPS) / 1000.0

        # update timers
        if not game_over and not tutorial.is_active():
            if engine.turn == 1:
                timer_white += dt
            else:
                timer_black += dt

        for e in pygame.event.get():
            if e.type == pygame.QUIT:
                running = False

            elif tutorial.is_active():
                tutorial.handle_event(e)
                if e.type == pygame.KEYDOWN and e.key == pygame.K_n:
                    current_theme = NIGHT if current_theme == DAY else DAY
                    print("Night mode activé" if current_theme == NIGHT else "Day mode activé")
                continue

            elif e.type == pygame.KEYDOWN:
                if e.key == pygame.K_h and not game_over:
                    hint = engine.get_hint()
                    if hint:
                        hint_alpha = 255
                elif e.key == pygame.K_n:
                    current_theme = NIGHT if current_theme == DAY else DAY
                    print("Night mode activé" if current_theme == NIGHT else "Day mode activé")
                elif e.key == pygame.K_1:
                    ai.level = 1
                    print("IA niveau 1 actif")
                elif e.key == pygame.K_2:
                    ai.level = 2
                    print("IA niveau 2 actif")
                elif e.key == pygame.K_3:
                    ai.level = 3
                    print("IA niveau 3 actif")
                elif e.key == pygame.K_r and game_over:
                    reset_game()
                elif e.key == pygame.K_t:
                    tutorial.toggle()

            elif e.type == pygame.MOUSEBUTTONDOWN and e.button == 1:
                mx, my = e.pos

                if end_animation and end_animation.button_rect and end_animation.button_rect.collidepoint(mx, my):
                    reset_game()
                    continue

                if game_over:
                    continue

                if my < 50:
                    continue  # ignore overlay

                c = mx // CELL
                r = (my - 50) // CELL
                if not (0 <= r < 8 and 0 <= c < 8):
                    continue

                piece = engine.board.grid[r][c]

                if selected is None:
                    if color(piece) == engine.turn:
                        captures = engine._any_capture_available()
                        if captures:
                            caps = get_captures(engine.board, r, c)
                            moves = [(r2, c2) for r2, c2, _, _ in caps]
                        else:
                            moves = get_simple_moves(engine.board, r, c)

                        if moves:
                            selected = (r, c)
                            pulse = SelectPulseAnimation((r, c), CELL, OFFSET_Y, current_theme["text"])
                            animations.append(pulse)
                            hint_alpha = 0
                            hint = None
                        else:
                            animations.append(ShakeAnimation((r, c), SHAKE_AMPLITUDE))
                    else:
                        animations.append(ShakeAnimation((r, c), SHAKE_AMPLITUDE))
                else:
                    if (r, c) in moves:
                        piece_before = engine.board.grid[selected[0]][selected[1]]
                        if engine.move_piece(selected[0], selected[1], r, c):
                            piece_after = engine.board.grid[r][c]
                            last_move = (selected[0], selected[1], r, c)
                            move_anim = MoveAnimation(
                                (selected[1], selected[0]), (c, r), piece_after,
                                CELL, OFFSET_Y,
                                current_theme,
                                current_theme == NIGHT,
                                font,
                            )
                            animations.append(move_anim)
                            lastmove_anim = LastMoveFadeAnimation([
                                (selected[1] * CELL, OFFSET_Y + selected[0] * CELL, CELL),
                                (c * CELL, OFFSET_Y + r * CELL, CELL),
                            ])
                            animations.append(lastmove_anim)
                            if abs(piece_before) == 1 and abs(piece_after) == 2:
                                promo_anim = PromotionGlowAnimation((r, c), CELL, OFFSET_Y, current_theme["crown"])
                                animations.append(promo_anim)
                            selected = None
                            moves = []
                            hint_alpha = 0
                            hint = None
                        else:
                            animations.append(ShakeAnimation((r, c), SHAKE_AMPLITUDE))
                    else:
                        animations.append(ShakeAnimation((r, c), SHAKE_AMPLITUDE))
                        selected = None
                        moves = []

        # fade du hint
        if hint_alpha > 0 and not tutorial.is_active():
            hint_alpha = max(0, hint_alpha - 120 * dt)

        # update animations
        for anim in animations[:]:
            anim.update(dt)
            if anim.finished:
                animations.remove(anim)

        # pulses de capture
        active_capture_cells = capture_cells(engine) if not game_over else []
        existing_capture = {a.cell for a in animations if isinstance(a, CapturePulseAnimation)}
        accent_color = CAPTURE_PULSE_COLOR if current_theme != NIGHT else (120, 210, 190)
        for cell in active_capture_cells:
            if cell not in existing_capture:
                animations.append(CapturePulseAnimation(cell, CELL, OFFSET_Y, accent_color))
        for anim in animations:
            if isinstance(anim, CapturePulseAnimation) and anim.cell not in active_capture_cells:
                anim.finished = True

        # tour de l'IA
        if not game_over and not tutorial.is_active() and engine.turn == ai_plays and has_legal_moves(engine):
            move = ai.choose_move()
            if move:
                r, c, r2, c2 = move
                piece_before = engine.board.grid[r][c]
                if engine.move_piece(r, c, r2, c2):
                    piece_after = engine.board.grid[r2][c2]
                    last_move = (r, c, r2, c2)
                    move_anim = MoveAnimation(
                        (c, r), (c2, r2), piece_after,
                        CELL, OFFSET_Y,
                        current_theme,
                        current_theme == NIGHT,
                        font,
                    )
                    animations.append(move_anim)
                    lastmove_anim = LastMoveFadeAnimation([
                        (c * CELL, OFFSET_Y + r * CELL, CELL),
                        (c2 * CELL, OFFSET_Y + r2 * CELL, CELL),
                    ])
                    animations.append(lastmove_anim)
                    if abs(piece_before) == 1 and abs(piece_after) == 2:
                        promo_anim = PromotionGlowAnimation(
                            (r2, c2), CELL, OFFSET_Y, current_theme["crown"]
                        )
                        animations.append(promo_anim)
            selected = None
            moves = []
            hint = None
            hint_alpha = 0

        # détection fin de partie
        if not game_over and not has_legal_moves(engine):
            winner = "Victoire des Blancs" if engine.turn == -1 else "Victoire des Noirs"
            end_animation = EndGameAnimation(winner, (WIDTH, HEIGHT), current_theme["text"])
            animations.append(end_animation)
            game_over = True

        shake_offsets = {}
        for anim in animations:
            if isinstance(anim, ShakeAnimation):
                shake_offsets[anim.cell] = anim.offset()

        moving_targets = {
            (anim.end_cell[1], anim.end_cell[0])
            for anim in animations
            if isinstance(anim, MoveAnimation) and not anim.finished
        }

        draw_board(
            screen,
            engine,
            selected,
            moves,
            hint,
            hint_alpha,
            font,
            timer_white,
            timer_black,
            animations,
            moving_targets,
            shake_offsets,
        )

        if tutorial.is_active():
            tutorial.draw(screen, font, current_theme)

        pygame.display.flip()

    pygame.quit()


if __name__ == "__main__":
    main()
