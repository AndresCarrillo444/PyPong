import random
import pygame
from pygame.locals import QUIT

VENTANA_HORI = 640  
VENTANA_VERT = 480  
FPS = 60  
PUNTAJE     = (255, 255, 255)
GRIS_MEDIO  = (120, 120, 120)
GRIS_OSCURO = (40,  40,  40)
BORDE_GROSOR = 2
PANEL_ALTO   = 70
CANCHA_IZQ = 0
CANCHA_DER = VENTANA_HORI
CANCHA_ARR = PANEL_ALTO + BORDE_GROSOR
CANCHA_ABA = VENTANA_VERT - BORDE_GROSOR
BOLA_VEL_INICIAL      = 2.0
BOLA_VEL_MAXIMA       = 8.0
BOLA_GOLPES_POR_NIVEL = 3      
BOLA_FACTOR_AUMENTO   = 0.4   
RAQUETA_VEL_JUGADOR   = 5.0   
RAQUETA_VEL_IA_BASE   = 3.0   
RAQUETA_VEL_IA_MAXIMA = 6.5   
RAQUETA_IA_GOLPES_POR_NIVEL = 4   
RAQUETA_IA_FACTOR_AUMENTO   = 0.4 

def crear_fondo():
    superficie = pygame.Surface((VENTANA_HORI, VENTANA_VERT))
    for y in range(VENTANA_VERT):
        intensidad = int(18 * (y / VENTANA_VERT))
        pygame.draw.line(superficie, (intensidad, intensidad, intensidad),
                         (0, y), (VENTANA_HORI, y))
    return superficie

def dibujar_campo(ventana):
    cx = VENTANA_HORI // 2
    cy = (CANCHA_ARR + CANCHA_ABA) // 2

    for y in range(CANCHA_ARR, CANCHA_ABA, 18):
        pygame.draw.line(ventana, GRIS_OSCURO, (cx, y), (cx, min(y + 9, CANCHA_ABA)), 1)

    pygame.draw.circle(ventana, GRIS_OSCURO, (cx, cy), 48, 1)
    pygame.draw.line(ventana, GRIS_OSCURO,
                     (0, CANCHA_ABA), (VENTANA_HORI, CANCHA_ABA), BORDE_GROSOR)

def dibujar_scoreboard(ventana, fuente_grande, fuente_pequeña, fuente_vel,
                       puntos_jugador, puntos_ia, golpes, vel_bola):
    cx = VENTANA_HORI // 2

    panel = pygame.Surface((VENTANA_HORI, PANEL_ALTO), pygame.SRCALPHA)
    panel.fill((255, 255, 255, 12))
    ventana.blit(panel, (0, 0))

    pygame.draw.line(ventana, GRIS_OSCURO,
                     (0, PANEL_ALTO), (VENTANA_HORI, PANEL_ALTO), BORDE_GROSOR)

    label = fuente_pequeña.render("SCOREBOARD", True, GRIS_MEDIO)
    ventana.blit(label, (cx - label.get_width() // 2, 6))

    texto_jugador = fuente_grande.render(str(puntos_jugador), True, PUNTAJE)
    texto_ia      = fuente_grande.render(str(puntos_ia),      True, PUNTAJE)
    separador     = fuente_grande.render(":",                 True, GRIS_MEDIO)

    sep_x = cx - separador.get_width() // 2
    ventana.blit(separador,     (sep_x, 24))
    ventana.blit(texto_jugador, (sep_x - 20 - texto_jugador.get_width(), 24))
    ventana.blit(texto_ia,      (sep_x + separador.get_width() + 20, 24))

    label_j = fuente_pequeña.render("TU",  True, GRIS_MEDIO)
    label_i = fuente_pequeña.render("CPU", True, GRIS_MEDIO)
    ventana.blit(label_j, (sep_x - 20 - texto_jugador.get_width() // 2 - label_j.get_width() // 2, 56))
    ventana.blit(label_i, (sep_x + separador.get_width() + 20 + texto_ia.get_width() // 2 - label_i.get_width() // 2, 56))

    nivel = golpes // BOLA_GOLPES_POR_NIVEL
    color_vel = (255, max(255 - nivel * 40, 80), 80) if nivel > 0 else GRIS_MEDIO
    txt_vel = fuente_vel.render(f"bola x{vel_bola:.1f}  [{golpes} golpes]", True, color_vel)
    ventana.blit(txt_vel, (VENTANA_HORI - txt_vel.get_width() - 10, 8))

class pelota:
    def __init__(self, fichero_imagen):
        self.image = pygame.image.load(fichero_imagen).convert_alpha()
        self.ancho, self.alto = self.image.get_size()
        self.puntuacion    = 0
        self.puntuacion_ia = 0
        self.golpes        = 0
        self.vel           = BOLA_VEL_INICIAL
        self.reiniciar()

    def reiniciar(self):
        self.x      = VENTANA_HORI / 2 - self.ancho / 2
        self.y      = (CANCHA_ARR + CANCHA_ABA) / 2 - self.alto / 2
        self.vel    = BOLA_VEL_INICIAL
        self.golpes = 0
        self.dir_x  = random.choice([-self.vel, self.vel])
        self.dir_y  = random.choice([-self.vel, self.vel])

    def registrar_golpe(self):
        self.golpes += 1
        nueva_vel = min(
            BOLA_VEL_INICIAL + (self.golpes // BOLA_GOLPES_POR_NIVEL) * BOLA_FACTOR_AUMENTO,
            BOLA_VEL_MAXIMA
        )
        if nueva_vel != self.vel:
            self.vel   = nueva_vel
            self.dir_x = nueva_vel * (1 if self.dir_x > 0 else -1)
            self.dir_y = nueva_vel * (1 if self.dir_y > 0 else -1)

    def mover(self):
        self.x += self.dir_x
        self.y += self.dir_y

    def rebotar(self):
        if self.x + self.ancho <= CANCHA_IZQ:
            self.puntuacion_ia += 1
            self.reiniciar()
            return
        if self.x >= CANCHA_DER:
            self.puntuacion += 1
            self.reiniciar()
            return

        if self.y <= CANCHA_ARR:
            self.y     = CANCHA_ARR
            self.dir_y = abs(self.dir_y)
        if self.y + self.alto >= CANCHA_ABA:
            self.y     = CANCHA_ABA - self.alto
            self.dir_y = -abs(self.dir_y)


class raqueta:
    def __init__(self):
        self.image = pygame.image.load("raqueta.png").convert_alpha()
        self.ancho, self.alto = self.image.get_size()
        self.x     = 0
        self.y     = (CANCHA_ARR + CANCHA_ABA) / 2 - self.alto / 2
        self.dir_y = 0   

    def mover(self):
        """Velocidad fija del jugador, independiente de la pelota."""
        self.y += self.dir_y * RAQUETA_VEL_JUGADOR
        self._limitar()

    def mover_ia(self, bola):
        vel_ia = min(
            RAQUETA_VEL_IA_BASE + (bola.golpes // RAQUETA_IA_GOLPES_POR_NIVEL) * RAQUETA_IA_FACTOR_AUMENTO,
            RAQUETA_VEL_IA_MAXIMA
        )

        centro_raqueta = self.y + self.alto / 2
        centro_bola    = bola.y  + bola.alto  / 2

        if centro_raqueta > centro_bola:
            self.dir_y = -1
        elif centro_raqueta < centro_bola:
            self.dir_y = 1
        else:
            self.dir_y = 0

        self.y += self.dir_y * vel_ia
        self._limitar()

    def _limitar(self):
        if self.y < CANCHA_ARR:
            self.y = CANCHA_ARR
        if self.y + self.alto > CANCHA_ABA:
            self.y = CANCHA_ABA - self.alto

    def golpear(self, bola):
        if not (
            bola.x < self.x + self.ancho
            and bola.x + bola.ancho > self.x
            and bola.y < self.y + self.alto
            and bola.y + bola.alto > self.y
        ):
            return

        solap_derecha   = (self.x + self.ancho) - bola.x
        solap_izquierda = (bola.x + bola.ancho) - self.x
        solap_abajo     = (self.y + self.alto)   - bola.y
        solap_arriba    = (bola.y + bola.alto)   - self.y

        if min(solap_derecha, solap_izquierda) < min(solap_abajo, solap_arriba):
            bola.dir_x = abs(bola.vel)
            bola.x     = self.x + self.ancho
        else:
            if solap_abajo < solap_arriba:
                if not (bola.dir_y < 0 and self.dir_y < 0 and abs(self.dir_y * RAQUETA_VEL_JUGADOR) >= abs(bola.dir_y)):
                    bola.dir_y = abs(bola.vel)
                bola.y = self.y + self.alto
            else:
                if not (bola.dir_y > 0 and self.dir_y > 0 and abs(self.dir_y * RAQUETA_VEL_JUGADOR) >= abs(bola.dir_y)):
                    bola.dir_y = -abs(bola.vel)
                bola.y = self.y - bola.alto

        bola.registrar_golpe()

    def golpear_ia(self, bola):
        if not (
            bola.x + bola.ancho > self.x
            and bola.x < self.x + self.ancho
            and bola.y + bola.alto > self.y
            and bola.y < self.y + self.alto
        ):
            return

        vel_ia_actual = min(
            RAQUETA_VEL_IA_BASE + (bola.golpes // RAQUETA_IA_GOLPES_POR_NIVEL) * RAQUETA_IA_FACTOR_AUMENTO,
            RAQUETA_VEL_IA_MAXIMA
        )

        solap_derecha   = (self.x + self.ancho) - bola.x
        solap_izquierda = (bola.x + bola.ancho) - self.x
        solap_abajo     = (self.y + self.alto)   - bola.y
        solap_arriba    = (bola.y + bola.alto)   - self.y

        if min(solap_derecha, solap_izquierda) < min(solap_abajo, solap_arriba):
            bola.dir_x = -abs(bola.vel)
            bola.x     = self.x - bola.ancho
        else:
            if solap_abajo < solap_arriba:
                if not (bola.dir_y < 0 and self.dir_y < 0 and abs(self.dir_y * vel_ia_actual) >= abs(bola.dir_y)):
                    bola.dir_y = abs(bola.vel)
                bola.y = self.y + self.alto
            else:
                if not (bola.dir_y > 0 and self.dir_y > 0 and abs(self.dir_y * vel_ia_actual) >= abs(bola.dir_y)):
                    bola.dir_y = -abs(bola.vel)
                bola.y = self.y - bola.alto

        bola.registrar_golpe()

class Boton:
    def __init__(self, x, y, ancho, alto, texto, fuente):
        self.rect   = pygame.Rect(x, y, ancho, alto)
        self.texto  = texto
        self.fuente = fuente

    def dibujar(self, ventana, mouse_pos):
        hover = self.rect.collidepoint(mouse_pos)
        color_fondo  = (60, 60, 60) if hover else (30, 30, 30)
        color_borde  = (200, 200, 200) if hover else (80, 80, 80)
        pygame.draw.rect(ventana, color_fondo, self.rect, border_radius=6)
        pygame.draw.rect(ventana, color_borde, self.rect, width=1, border_radius=6)
        superficie = self.fuente.render(self.texto, True, PUNTAJE if hover else GRIS_MEDIO)
        ventana.blit(superficie, (
            self.rect.centerx - superficie.get_width()  // 2,
            self.rect.centery - superficie.get_height() // 2,
        ))

    def fue_clickeado(self, event):
        return (event.type == pygame.MOUSEBUTTONDOWN
                and event.button == 1
                and self.rect.collidepoint(event.pos))

def pantalla_fin(ventana, fondo_surface, fuente_titulo, fuente_sub, fuente_btn,
                 puntos_jugador, puntos_ia):
    """Muestra el resultado y devuelve True si el jugador quiere volver a jugar."""

    cx = VENTANA_HORI // 2
    ganador = "¡GANASTE!" if puntos_jugador > puntos_ia else "¡PERDISTE!"
    color_ganador = (180, 255, 160) if puntos_jugador > puntos_ia else (255, 120, 120)

    ancho_btn, alto_btn = 200, 46
    btn_jugar = Boton(cx - ancho_btn - 20, 310, ancho_btn, alto_btn, "VOLVER A JUGAR", fuente_btn)
    btn_salir = Boton(cx + 20,             310, ancho_btn, alto_btn, "SALIR",          fuente_btn)

    clock = pygame.time.Clock()
    while True:
        mouse_pos = pygame.mouse.get_pos()

        for event in pygame.event.get():
            if event.type == QUIT:
                return False
            if btn_jugar.fue_clickeado(event):
                return True
            if btn_salir.fue_clickeado(event):
                return False
            
        ventana.blit(fondo_surface, (0, 0))
        overlay = pygame.Surface((VENTANA_HORI, VENTANA_VERT), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 160))
        ventana.blit(overlay, (0, 0))
        txt_ganador = fuente_titulo.render(ganador, True, color_ganador)
        ventana.blit(txt_ganador, (cx - txt_ganador.get_width() // 2, 160))
        txt_score = fuente_sub.render(f"{puntos_jugador}  —  {puntos_ia}", True, PUNTAJE)
        ventana.blit(txt_score, (cx - txt_score.get_width() // 2, 230))
        txt_label = fuente_btn.render("TU          CPU", True, GRIS_MEDIO)
        ventana.blit(txt_label, (cx - txt_label.get_width() // 2, 268))
        btn_jugar.dibujar(ventana, mouse_pos)
        btn_salir.dibujar(ventana, mouse_pos)

        pygame.display.flip()
        clock.tick(FPS)

def jugar(ventana, fondo_surface, fuente_grande, fuente_pequeña, fuente_vel):

    meta_puntos = 5
    bola = pelota("pelota.png")
    raqueta_1 = raqueta()
    raqueta_1.x = 60
    raqueta_2 = raqueta()
    raqueta_2.x = VENTANA_HORI - 60 - raqueta_2.ancho

    teclas_presionadas = set()
    clock = pygame.time.Clock()

    jugando = True
    while jugando:
        arriba = pygame.K_w in teclas_presionadas
        abajo  = pygame.K_s in teclas_presionadas
        if arriba and not abajo:
            raqueta_1.dir_y = -1
        elif abajo and not arriba:
            raqueta_1.dir_y = 1
        else:
            raqueta_1.dir_y = 0

        bola.mover()
        bola.rebotar()
        raqueta_1.mover()
        raqueta_2.mover_ia(bola)
        raqueta_1.golpear(bola)
        raqueta_2.golpear_ia(bola)

        ventana.blit(fondo_surface, (0, 0))
        dibujar_campo(ventana)
        ventana.blit(bola.image,      (bola.x,      bola.y))
        ventana.blit(raqueta_1.image, (raqueta_1.x, raqueta_1.y))
        ventana.blit(raqueta_2.image, (raqueta_2.x, raqueta_2.y))
        dibujar_scoreboard(ventana, fuente_grande, fuente_pequeña, fuente_vel,
                           bola.puntuacion, bola.puntuacion_ia,
                           bola.golpes, bola.vel)

        for event in pygame.event.get():
            if event.type == QUIT:
                return bola.puntuacion, bola.puntuacion_ia, False  

            if event.type == pygame.KEYDOWN:
                if event.key in (pygame.K_w, pygame.K_s):
                    teclas_presionadas.add(event.key)

            if event.type == pygame.KEYUP:
                if event.key in (pygame.K_w, pygame.K_s):
                    teclas_presionadas.discard(event.key)

        if bola.puntuacion >= meta_puntos or bola.puntuacion_ia >= meta_puntos:
            jugando = False

        pygame.display.flip()
        clock.tick(FPS)

    return bola.puntuacion, bola.puntuacion_ia, True 

def main():
    pygame.init()

    ventana = pygame.display.set_mode((VENTANA_HORI, VENTANA_VERT))
    pygame.display.set_caption("pyPong")

    fuente_grande  = pygame.font.SysFont("Arial", 36, bold=True)
    fuente_pequeña = pygame.font.SysFont("Arial", 14)
    fuente_vel     = pygame.font.SysFont("Arial", 12)
    fuente_titulo  = pygame.font.SysFont("Arial", 54, bold=True)
    fuente_sub     = pygame.font.SysFont("Arial", 42, bold=True)
    fuente_btn     = pygame.font.SysFont("Arial", 18, bold=True)
    fondo_surface = crear_fondo()

    corriendo = True
    while corriendo:
        puntos_j, puntos_ia, normal = jugar(
            ventana, fondo_surface, fuente_grande, fuente_pequeña, fuente_vel
        )
        if not normal:
            break  
        corriendo = pantalla_fin(
            ventana, fondo_surface, fuente_titulo, fuente_sub, fuente_btn,
            puntos_j, puntos_ia
        )
    pygame.quit()


if __name__ == "__main__":
    main()