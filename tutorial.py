# tutorial.py
from typing import List, Dict, Any
import pygame


class Tutorial:
    """
    Gestion d'un petit onboarding multi-slides.
    Affiche une carte centrale cosy par-dessus le jeu,
    avec navigation clavier / clic.
    """

    def __init__(self) -> None:
        self.slides: List[Dict[str, Any]] = [
            {
                "title": "Bienvenue dans le Jeu de Dames Cosy",
                "lines": [
                    "Jouez contre l'IA ou un autre joueur.",
                    "Interface animée, mode jour/nuit, conseils de coups.",
                    "",
                    "Appuyez sur la flèche droite ou cliquez pour continuer.",
                ],
            },
            {
                "title": "Comment jouer un coup",
                "lines": [
                    "Cliquez sur l'un de vos pions pour le sélectionner.",
                    "Les cases possibles s'allument en vert.",
                    "Cliquez sur une case en surbrillance pour jouer.",
                    "Les captures obligatoires sont gérées automatiquement.",
                ],
            },
            {
                "title": "Obtenir un conseil (Hint)",
                "lines": [
                    "Appuyez sur la touche H pour demander une suggestion de coup.",
                    "Un halo bleu apparaît autour de la pièce conseillée,",
                    "et la case de destination est mise en avant.",
                ],
            },
            {
                "title": "Jouer contre l'IA",
                "lines": [
                    "L'IA contrôle par défaut les pions noirs.",
                    "Changez la difficulté à la volée :",
                    "- 1 : niveau facile (coups légaux aléatoires)",
                    "- 2 : niveau intermédiaire (captures prioritaires)",
                    "- 3 : niveau difficile (minimax rapide)",
                ],
            },
            {
                "title": "Interface & Thèmes",
                "lines": [
                    "La barre supérieure affiche le joueur actif et les timers.",
                    "Appuyez sur N pour basculer entre le mode Jour et Nuit.",
                    "Animations : glissé des pièces, pulses, glow de promotion,",
                    "feedback visuel en cas d'erreur de coup.",
                ],
            },
            {
                "title": "Fin de partie et rejouer",
                "lines": [
                    "Lorsque l'un des joueurs n'a plus de coup légal,",
                    "le jeu déclare la victoire des Blancs ou des Noirs.",
                    "Utilisez le bouton de redémarrage ou la touche dédiée",
                    "pour lancer une nouvelle partie.",
                    "",
                    "Appuyez sur Echap ou T pour fermer le tutoriel.",
                ],
            },
        ]
        self.current_index: int = 0
        self.active: bool = False

    # État
    def start(self) -> None:
        self.current_index = 0
        self.active = True

    def stop(self) -> None:
        self.active = False

    def toggle(self) -> None:
        if self.active:
            self.stop()
        else:
            self.start()

    def is_active(self) -> bool:
        return self.active

    # Navigation
    def next(self) -> None:
        if self.current_index < len(self.slides) - 1:
            self.current_index += 1
        else:
            # Dernière slide -> fermer
            self.stop()

    def previous(self) -> None:
        if self.current_index > 0:
            self.current_index -= 1

    def handle_event(self, event: pygame.event.Event) -> None:
        """
        À appeler depuis la boucle d'événements quand le tutoriel est actif.
        Intercepte les touches/flèches/clics pour changer de slide.
        """
        if event.type == pygame.KEYDOWN:
            if event.key in (pygame.K_ESCAPE, pygame.K_t):
                self.stop()
            elif event.key in (pygame.K_RIGHT, pygame.K_SPACE, pygame.K_RETURN):
                self.next()
            elif event.key == pygame.K_LEFT:
                self.previous()
        elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            # Un simple clic n'importe où fait avancer le tutoriel
            self.next()

    # Rendu
    def draw(self, screen: pygame.Surface, font: pygame.font.Font, theme: dict) -> None:
        """
        Dessine une carte centrale semi-transparente par-dessus le jeu.
        """
        width, height = screen.get_size()
        overlay = pygame.Surface((width, height), pygame.SRCALPHA)
        # voile global léger
        overlay.fill((0, 0, 0, 150))
        screen.blit(overlay, (0, 0))

        card_width = int(width * 0.8)
        card_height = int(height * 0.6)
        card_x = (width - card_width) // 2
        card_y = (height - card_height) // 2

        card_surface = pygame.Surface((card_width, card_height), pygame.SRCALPHA)

        # fond type "glassmorphism" cosy
        bg_color = theme.get("overlay", (45, 40, 36))
        base = pygame.Color(*bg_color)
        card_surface.fill((base.r, base.g, base.b, 230))

        pygame.draw.rect(
            card_surface,
            (255, 255, 255, 30),
            card_surface.get_rect(),
            border_radius=24,
        )

        # Récup slide
        slide = self.slides[self.current_index]
        title = slide["title"]
        lines = slide["lines"]

        # Titre
        title_font = font
        title_surf = title_font.render(title, True, theme.get("text", (230, 230, 230)))
        title_rect = title_surf.get_rect(center=(card_width // 2, 60))
        card_surface.blit(title_surf, title_rect)

        # Texte
        body_color = theme.get("text", (230, 230, 230))
        y = 110
        for line in lines:
            line_surf = font.render(line, True, body_color)
            rect = line_surf.get_rect(center=(card_width // 2, y))
            card_surface.blit(line_surf, rect)
            y += 30

        # Indicateurs de navigation
        nav_text = "← Précédent    •    → Suivant    •    T / Échap : Fermer"
        nav_surf = font.render(nav_text, True, body_color)
        nav_rect = nav_surf.get_rect(center=(card_width // 2, card_height - 40))
        card_surface.blit(nav_surf, nav_rect)

        # Dessin final
        screen.blit(card_surface, (card_x, card_y))

