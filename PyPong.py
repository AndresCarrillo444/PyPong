import random
import math
import pygame
from pygame.locals import QUIT

pygame.init()

VENTANA_HORI = 900
VENTANA_VERT = 660
FPS          = 60

BLANCO      = (255, 255, 255)
NEGRO       = (0,   0,   0)
GRIS_MEDIO  = (140, 140, 140)
GRIS_OSCURO = (35,  35,  35)
CYAN        = (0,   220, 255)
MAGENTA     = (255, 60,  180)
AMARILLO    = (255, 210, 50)
VERDE       = (80,  255, 130)
ROJO        = (255, 80,  80)
NARANJA     = (255, 140, 0)
VIOLETA     = (160, 80,  255)
TURQUESA    = (0,   200, 160)

PANEL_ALTO   = 70
BORDE        = 2
CANCHA_ARR   = PANEL_ALTO + BORDE
CANCHA_ABA   = VENTANA_VERT - BORDE
CANCHA_IZQ   = BORDE
CANCHA_DER   = VENTANA_HORI - BORDE

RAQUETA_GROSOR  = 14
RAQUETA_LARGO   = 80
RAQUETA_LARGO_H = 80
BOLA_R          = 9

VEL_BOLA_INI     = 4.5
VEL_BOLA_MAX     = 14.0
GOLPES_POR_NIVEL = 4
FACTOR_AUMENTO   = 0.5

VEL_J          = 6.5
VEL_IA_BASE    = 3.8
VEL_IA_MAX     = 6.8
IA_GOLPES_NIV  = 5
IA_FACTOR      = 0.35

MODO_VS_CPU   = "VS_CPU"
MODO_1V1      = "1V1"
MODO_RAPIDO   = "RAPIDO"
MODO_CRONO    = "CRONO"
MODO_4J       = "4J"
MODO_SUPERVIV = "SUPERVIV"
MODO_BOLAS2   = "BOLAS2"
MODO_TURBO    = "TURBO"

META_NORMAL  = 7
META_RAPIDO  = 3
META_4J      = 5
TIEMPO_CRONO = 60
TIEMPO_TURBO = 45

PALETA_MODOS = {
    MODO_VS_CPU:   CYAN,
    MODO_1V1:      AMARILLO,
    MODO_RAPIDO:   NARANJA,
    MODO_CRONO:    MAGENTA,
    MODO_4J:       VERDE,
    MODO_SUPERVIV: ROJO,
    MODO_BOLAS2:   VIOLETA,
    MODO_TURBO:    TURQUESA,
}

NOMBRE_MODOS = {
    MODO_VS_CPU:   "VS CPU",
    MODO_1V1:      "1 vs 1",
    MODO_RAPIDO:   "MODO RAPIDO",
    MODO_CRONO:    "CONTRARRELOJ",
    MODO_4J:       "4 JUGADORES",
    MODO_SUPERVIV: "SUPERVIVENCIA",
    MODO_BOLAS2:   "DOBLE BOLA",
    MODO_TURBO:    "TURBO",
}

class Particula:
    def __init__(self, x, y, color):
        a         = random.uniform(0, 2 * math.pi)
        sp        = random.uniform(2, 7)
        self.x    = float(x)
        self.y    = float(y)
        self.vx   = math.cos(a) * sp
        self.vy   = math.sin(a) * sp
        self.vida = random.randint(18, 36)
        self.max_v = self.vida
        self.color = color
        self.r    = random.randint(2, 5)

    def tick(self):
        self.x  += self.vx
        self.y  += self.vy
        self.vy += 0.2
        self.vx *= 0.96
        self.vida -= 1

    def draw(self, surf):
        a = int(255 * self.vida / self.max_v)
        s = pygame.Surface((self.r * 2, self.r * 2), pygame.SRCALPHA)
        pygame.draw.circle(s, (*self.color[:3], a), (self.r, self.r), self.r)
        surf.blit(s, (int(self.x) - self.r, int(self.y) - self.r))

    @property
    def viva(self): return self.vida > 0


class Particulas:
    def __init__(self): self.pool = []

    def emitir(self, x, y, color, n=18):
        self.pool += [Particula(x, y, color) for _ in range(n)]

    def update_draw(self, surf):
        self.pool = [p for p in self.pool if p.viva]
        for p in self.pool:
            p.tick()
            p.draw(surf)

def fondo_gradiente():
    s = pygame.Surface((VENTANA_HORI, VENTANA_VERT))
    for y in range(VENTANA_VERT):
        t = y / VENTANA_VERT
        pygame.draw.line(s, (int(7+t*6), int(7+t*6), int(16+t*12)),
                         (0, y), (VENTANA_HORI, y))
    return s


def draw_raqueta(surf, x, y, w, h, color, horizontal=False):
    rx, ry, rw, rh = int(x), int(y), w, h
    gs = pygame.Surface((rw + 16, rh + 16), pygame.SRCALPHA)
    for i in range(6, 0, -1):
        pygame.draw.rect(gs, (*color, 18 * i),
                         pygame.Rect(6-i, 6-i, rw+i*2, rh+i*2), border_radius=5)
    surf.blit(gs, (rx-6, ry-6))
    pygame.draw.rect(surf, color, pygame.Rect(rx, ry, rw, rh), border_radius=5)
    bx = rx + (4 if horizontal else 2)
    by = ry + 4
    bw = (rw - 8) if horizontal else 4
    bh = 4 if horizontal else (rh - 8)
    bs = pygame.Surface((max(1, bw), max(1, bh)), pygame.SRCALPHA)
    bs.fill((255, 255, 255, 55))
    surf.blit(bs, (bx, by))


def draw_bola(surf, x, y, r, color, trail):
    for i, pos in enumerate(trail):
        a  = int(110 * i / max(len(trail), 1))
        rt = max(2, int(r * i / max(len(trail), 1)))
        s  = pygame.Surface((rt*2+4, rt*2+4), pygame.SRCALPHA)
        pygame.draw.circle(s, (*color, a), (rt+2, rt+2), rt)
        surf.blit(s, (int(pos[0])-rt-2, int(pos[1])-rt-2))
    glow = pygame.Surface((r*4, r*4), pygame.SRCALPHA)
    for rg in range(r*2, 0, -1):
        pygame.draw.circle(glow, (*color, int(80*(1-rg/(r*2)))), (r*2, r*2), rg)
    surf.blit(glow, (int(x)-r, int(y)-r))
    pygame.draw.circle(surf, color, (int(x), int(y)), r)
    pygame.draw.circle(surf, BLANCO, (int(x)-r//3, int(y)-r//3), max(2, r//4))


def draw_campo_2j(surf, modo):
    cx = VENTANA_HORI // 2
    cy = (CANCHA_ARR + CANCHA_ABA) // 2
    for y in range(CANCHA_ARR, CANCHA_ABA, 20):
        s = pygame.Surface((2, 10), pygame.SRCALPHA)
        s.fill((255, 255, 255, 40))
        surf.blit(s, (cx-1, y))
    pygame.draw.circle(surf, (45, 45, 75), (cx, cy), 62, 1)
    pygame.draw.circle(surf, (45, 45, 75), (cx, cy), 6)
    pygame.draw.line(surf, GRIS_OSCURO, (0, CANCHA_ABA), (VENTANA_HORI, CANCHA_ABA), BORDE)
    pygame.draw.line(surf, GRIS_OSCURO, (0, CANCHA_ARR), (VENTANA_HORI, CANCHA_ARR), BORDE)


def draw_campo_4j(surf):
    cx = VENTANA_HORI // 2
    cy = (CANCHA_ARR + CANCHA_ABA) // 2
    pygame.draw.line(surf, GRIS_OSCURO, (0, CANCHA_ARR),      (VENTANA_HORI, CANCHA_ARR), BORDE)
    pygame.draw.line(surf, GRIS_OSCURO, (0, CANCHA_ABA),      (VENTANA_HORI, CANCHA_ABA), BORDE)
    pygame.draw.line(surf, GRIS_OSCURO, (CANCHA_IZQ, CANCHA_ARR), (CANCHA_IZQ, CANCHA_ABA), BORDE)
    pygame.draw.line(surf, GRIS_OSCURO, (CANCHA_DER, CANCHA_ARR), (CANCHA_DER, CANCHA_ABA), BORDE)
    pygame.draw.circle(surf, (45, 45, 75), (cx, cy), 70, 1)
    pygame.draw.circle(surf, (45, 45, 75), (cx, cy), 7)
    for i in range(CANCHA_ARR, CANCHA_ABA, 20):
        s = pygame.Surface((2, 10), pygame.SRCALPHA)
        s.fill((255, 255, 255, 28))
        surf.blit(s, (cx-1, i))
    for i in range(CANCHA_IZQ, CANCHA_DER, 20):
        s = pygame.Surface((10, 2), pygame.SRCALPHA)
        s.fill((255, 255, 255, 28))
        surf.blit(s, (i, cy-1))


def draw_hud_2j(surf, fuentes, datos, modo, tiempo=None):
    f_gr, f_med, f_peq = fuentes
    panel = pygame.Surface((VENTANA_HORI, PANEL_ALTO), pygame.SRCALPHA)
    panel.fill((8, 8, 18, 215))
    surf.blit(panel, (0, 0))
    pygame.draw.line(surf, (55, 55, 95), (0, PANEL_ALTO), (VENTANA_HORI, PANEL_ALTO), 2)

    cx      = VENTANA_HORI // 2
    color_m = PALETA_MODOS.get(modo, GRIS_MEDIO)
    t_m     = f_peq.render(NOMBRE_MODOS.get(modo, modo), True, color_m)
    surf.blit(t_m, (cx - t_m.get_width()//2, 5))

    pj, pia, golpes, vel, nj, nia = datos
    nivel = golpes // GOLPES_POR_NIVEL
    c_vel = (255, max(255-nivel*35, 80), 80) if nivel > 0 else GRIS_MEDIO
    t_vel = f_peq.render(f"vel x{vel:.1f}  {golpes} golpes", True, c_vel)
    surf.blit(t_vel, (8, 8))

    t_sep = f_gr.render(":", True, GRIS_MEDIO)
    t_j   = f_gr.render(str(pj),  True, CYAN)
    t_ia  = f_gr.render(str(pia), True, MAGENTA)
    sx    = cx - t_sep.get_width()//2
    surf.blit(t_sep, (sx, 20))
    surf.blit(t_j,   (sx - 14 - t_j.get_width(), 20))
    surf.blit(t_ia,  (sx + t_sep.get_width() + 14, 20))
    n_j  = f_peq.render(nj,  True, GRIS_MEDIO)
    n_ia = f_peq.render(nia, True, GRIS_MEDIO)
    surf.blit(n_j,  (sx - 14 - t_j.get_width()//2  - n_j.get_width()//2,  54))
    surf.blit(n_ia, (sx + t_sep.get_width() + 14 + t_ia.get_width()//2 - n_ia.get_width()//2, 54))

    pausa_hint = f_peq.render("ESC = pausa", True, (70, 70, 90))
    surf.blit(pausa_hint, (VENTANA_HORI - pausa_hint.get_width() - 8, 54))

    if tiempo is not None:
        ct  = ROJO if tiempo <= 10 else PALETA_MODOS.get(modo, BLANCO)
        t_t = f_med.render(f"{tiempo}s", True, ct)
        surf.blit(t_t, (VENTANA_HORI - t_t.get_width() - 10, 18))


def draw_hud_4j(surf, fuentes, puntos, vidas, modo):
    f_gr, f_med, f_peq = fuentes
    panel = pygame.Surface((VENTANA_HORI, PANEL_ALTO), pygame.SRCALPHA)
    panel.fill((8, 8, 18, 215))
    surf.blit(panel, (0, 0))
    pygame.draw.line(surf, (55, 55, 95), (0, PANEL_ALTO), (VENTANA_HORI, PANEL_ALTO), 2)

    cx      = VENTANA_HORI // 2
    color_m = PALETA_MODOS[modo]
    t_m     = f_peq.render(NOMBRE_MODOS[modo], True, color_m)
    surf.blit(t_m, (cx - t_m.get_width()//2, 5))

    nombres = ["J1", "J2", "J3", "J4"]
    colores  = [CYAN, MAGENTA, AMARILLO, VERDE]
    slot_w   = VENTANA_HORI // 4
    for i, (nm, color) in enumerate(zip(nombres, colores)):
        sx  = i * slot_w + slot_w // 2
        t_n = f_peq.render(nm, True, color)
        surf.blit(t_n, (sx - t_n.get_width()//2, 18))
        t_p = f_gr.render(str(puntos[i]), True, color)
        surf.blit(t_p, (sx - t_p.get_width()//2, 32))
        if modo == MODO_SUPERVIV:
            t_v = f_peq.render("■" * vidas[i] + "□" * (3 - vidas[i]), True, color)
            surf.blit(t_v, (sx - t_v.get_width()//2, 54))

    pausa_hint = f_peq.render("ESC = pausa", True, (70, 70, 90))
    surf.blit(pausa_hint, (cx - pausa_hint.get_width()//2, 54))

class Bola:
    def __init__(self, vel_factor=1.0):
        self.r        = BOLA_R
        self.golpes   = 0
        self.vel      = VEL_BOLA_INI * vel_factor
        self.vel_ini  = VEL_BOLA_INI * vel_factor
        self.vel_max  = VEL_BOLA_MAX * vel_factor
        self.trail    = []
        self.color    = BLANCO
        self.puntos   = [0, 0, 0, 0]
        self.reiniciar()

    def reiniciar(self, dir_hint=None):
        cx = VENTANA_HORI / 2
        cy = (CANCHA_ARR + CANCHA_ABA) / 2
        self.x      = cx
        self.y      = cy
        self.vel    = self.vel_ini
        self.golpes = 0
        self.trail  = []
        ang  = random.uniform(math.radians(30), math.radians(60))
        sx   = dir_hint if dir_hint in (-1, 1) else random.choice([-1, 1])
        sy   = random.choice([-1, 1])
        self.dx = sx * self.vel * math.cos(ang)
        self.dy = sy * self.vel * math.sin(ang)
        self.color = BLANCO

    def registrar_golpe(self):
        self.golpes += 1
        nv = min(self.vel_ini + (self.golpes // GOLPES_POR_NIVEL) * FACTOR_AUMENTO, self.vel_max)
        if nv != self.vel:
            f = nv / self.vel
            self.vel  = nv
            self.dx  *= f
            self.dy  *= f
        nivel = self.golpes // GOLPES_POR_NIVEL
        self.color = [BLANCO, CYAN, AMARILLO, NARANJA, ROJO, MAGENTA][min(nivel, 5)]

    def mover(self):
        self.trail.append((self.x, self.y))
        if len(self.trail) > 12:
            self.trail.pop(0)
        self.x += self.dx
        self.y += self.dy

    def rebotar_2j(self, particulas):
        scored = False
        if self.x - self.r <= CANCHA_IZQ:
            self.puntos[1] += 1
            particulas.emitir(CANCHA_IZQ + 20, self.y, MAGENTA, 28)
            self.reiniciar(dir_hint=1)
            scored = True
        elif self.x + self.r >= CANCHA_DER:
            self.puntos[0] += 1
            particulas.emitir(CANCHA_DER - 20, self.y, CYAN, 28)
            self.reiniciar(dir_hint=-1)
            scored = True
        if not scored:
            if self.y - self.r <= CANCHA_ARR:
                self.y  = CANCHA_ARR + self.r
                self.dy = abs(self.dy)
                particulas.emitir(self.x, CANCHA_ARR, GRIS_MEDIO, 8)
            if self.y + self.r >= CANCHA_ABA:
                self.y  = CANCHA_ABA - self.r
                self.dy = -abs(self.dy)
                particulas.emitir(self.x, CANCHA_ABA, GRIS_MEDIO, 8)

    def rebotar_4j(self, particulas, vidas, colores_j, puntos, raquetas):

        r_arr, r_der, r_aba, r_izq = raquetas

        if self.x - self.r <= CANCHA_IZQ and self.dx < 0:
            defensa_ok = r_izq.y <= self.y <= r_izq.y + r_izq.h
            if not defensa_ok:
                if vidas  is not None: vidas[3]  = max(0, vidas[3] - 1)
                if puntos is not None: puntos[1] += 1
            particulas.emitir(CANCHA_IZQ + 20, self.y, colores_j[3], 28)
            self.x  = CANCHA_IZQ + self.r + 1
            self.dx = abs(self.dx)

        if self.x + self.r >= CANCHA_DER and self.dx > 0:
            defensa_ok = r_der.y <= self.y <= r_der.y + r_der.h
            if not defensa_ok:
                if vidas  is not None: vidas[1]  = max(0, vidas[1] - 1)
                if puntos is not None: puntos[3] += 1
            particulas.emitir(CANCHA_DER - 20, self.y, colores_j[1], 28)
            self.x  = CANCHA_DER - self.r - 1
            self.dx = -abs(self.dx)

        if self.y - self.r <= CANCHA_ARR and self.dy < 0:
            defensa_ok = r_arr.x <= self.x <= r_arr.x + r_arr.w
            if not defensa_ok:
                if vidas  is not None: vidas[0]  = max(0, vidas[0] - 1)
                if puntos is not None: puntos[2] += 1
            particulas.emitir(self.x, CANCHA_ARR, colores_j[0], 28)
            self.y  = CANCHA_ARR + self.r + 1
            self.dy = abs(self.dy)

        if self.y + self.r >= CANCHA_ABA and self.dy > 0:
            defensa_ok = r_aba.x <= self.x <= r_aba.x + r_aba.w
            if not defensa_ok:
                if vidas  is not None: vidas[2]  = max(0, vidas[2] - 1)
                if puntos is not None: puntos[0] += 1
            particulas.emitir(self.x, CANCHA_ABA, colores_j[2], 28)
            self.y  = CANCHA_ABA - self.r - 1
            self.dy = -abs(self.dy)

class Raqueta:
    def __init__(self, x, y, largo, grosor, color, orientacion="V"):
        self.x       = float(x)
        self.y       = float(y)
        self.largo   = largo
        self.grosor  = grosor
        self.color   = color
        self.ori     = orientacion
        self.dir     = 0
        self.w = grosor if orientacion == "V" else largo
        self.h = largo  if orientacion == "V" else grosor

    def mover_j(self, neg, pos, vel=VEL_J):
        if neg:        self.dir = -1
        elif pos:      self.dir =  1
        else:          self.dir =  0
        if self.ori == "V":
            self.y = max(CANCHA_ARR, min(self.y + self.dir * vel, CANCHA_ABA - self.h))
        else:
            self.x = max(CANCHA_IZQ, min(self.x + self.dir * vel, CANCHA_DER - self.w))

    def mover_ia(self, bola, dif=1.0):
        vel = min(VEL_IA_BASE + (bola.golpes // IA_GOLPES_NIV) * IA_FACTOR, VEL_IA_MAX) * dif
        err = random.uniform(-10, 10) * (1 - dif * 0.5)
        if self.ori == "V":
            centro = self.y + self.h / 2
            target = bola.y + err
            if abs(target - centro) > 3:
                self.y += (1 if target > centro else -1) * vel
            self.y = max(CANCHA_ARR, min(self.y, CANCHA_ABA - self.h))
        else:
            centro = self.x + self.w / 2
            target = bola.x + err
            if abs(target - centro) > 3:
                self.x += (1 if target > centro else -1) * vel
            self.x = max(CANCHA_IZQ, min(self.x, CANCHA_DER - self.w))

    def colisionar(self, bola, particulas, pared):
        bx = bola.x - bola.r
        by = bola.y - bola.r
        bw = bh = bola.r * 2
        rx, ry, rw, rh = int(self.x), int(self.y), self.w, self.h
        if not (bx < rx+rw and bx+bw > rx and by < ry+rh and by+bh > ry):
            return False
        speed = math.hypot(bola.dx, bola.dy)
        if pared in ("L", "R"):
            rel    = (bola.y - (ry + rh/2)) / (rh/2)
            rel    = max(-1.0, min(1.0, rel))
            ang    = rel * math.radians(55)
            sx_s   = 1 if pared == "L" else -1
            bola.dx = sx_s * speed * math.cos(ang)
            bola.dy = speed * math.sin(ang)
            bola.x  = (rx + rw + bola.r) if pared == "L" else (rx - bola.r)
        else:
            rel    = (bola.x - (rx + rw/2)) / (rw/2)
            rel    = max(-1.0, min(1.0, rel))
            ang    = rel * math.radians(55)
            sy_s   = 1 if pared == "T" else -1
            bola.dy = sy_s * speed * math.cos(ang)
            bola.dx = speed * math.sin(ang)
            bola.y  = (ry + rh + bola.r) if pared == "T" else (ry - bola.r)
        bola.registrar_golpe()
        particulas.emitir(bola.x, bola.y, self.color, 14)
        return True

def crear_fuentes():
    return (
        pygame.font.SysFont("Consolas", 38, bold=True),
        pygame.font.SysFont("Consolas", 26, bold=True),
        pygame.font.SysFont("Consolas", 15),
        pygame.font.SysFont("Consolas", 54, bold=True),
        pygame.font.SysFont("Consolas", 34, bold=True),
        pygame.font.SysFont("Consolas", 17, bold=True),
        pygame.font.SysFont("Consolas", 13),
    )


class Boton:
    def __init__(self, x, y, w, h, texto, fuente, acento=CYAN):
        self.rect   = pygame.Rect(x, y, w, h)
        self.texto  = texto
        self.fuente = fuente
        self.acento = acento

    def draw(self, surf, mp):
        hover = self.rect.collidepoint(mp)
        pygame.draw.rect(surf, (40, 40, 60) if hover else (18, 18, 30),
                         self.rect, border_radius=8)
        pygame.draw.rect(surf, self.acento if hover else (55, 55, 80),
                         self.rect, 2, border_radius=8)
        c   = BLANCO if hover else GRIS_MEDIO
        txt = self.fuente.render(self.texto, True, c)
        surf.blit(txt, (self.rect.centerx - txt.get_width()//2,
                        self.rect.centery - txt.get_height()//2))

    def clicked(self, ev):
        return (ev.type == pygame.MOUSEBUTTONDOWN and ev.button == 1
                and self.rect.collidepoint(ev.pos))

def menu_pausa(ventana, captura, fuentes, modo, clock):

    f_gr, f_med, f_peq, f_tit, f_sub, f_btn, f_info = fuentes
    cx = VENTANA_HORI // 2

    color_modo = PALETA_MODOS.get(modo, CYAN)
    bw, bh     = 280, 52
    gap        = 16
    start_y    = 260

    btn_reanudar = Boton(cx - bw//2, start_y,          bw, bh, "REANUDAR",        f_btn, color_modo)
    btn_menu     = Boton(cx - bw//2, start_y + bh+gap, bw, bh, "MENU PRINCIPAL",  f_btn, AMARILLO)
    btn_salir    = Boton(cx - bw//2, start_y + (bh+gap)*2, bw, bh, "SALIR",       f_btn, ROJO)

    while True:
        mp = pygame.mouse.get_pos()
        for ev in pygame.event.get():
            if ev.type == QUIT:
                return "salir"
            if ev.type == pygame.KEYDOWN:
                if ev.key == pygame.K_ESCAPE:
                    return "reanudar"
                if ev.key == pygame.K_RETURN:
                    return "reanudar"
            if btn_reanudar.clicked(ev): return "reanudar"
            if btn_menu.clicked(ev):     return "menu"
            if btn_salir.clicked(ev):    return "salir"

        ventana.blit(captura, (0, 0))

        overlay = pygame.Surface((VENTANA_HORI, VENTANA_VERT), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 155))
        ventana.blit(overlay, (0, 0))

        panel_w, panel_h = 360, 300
        panel = pygame.Surface((panel_w, panel_h), pygame.SRCALPHA)
        panel.fill((12, 12, 28, 230))
        ventana.blit(panel, (cx - panel_w//2, start_y - 60))
        pygame.draw.rect(ventana, color_modo,
                         pygame.Rect(cx - panel_w//2, start_y - 60, panel_w, panel_h),
                         2, border_radius=10)

        t_pausa = f_tit.render("PAUSA", True, color_modo)
        ventana.blit(t_pausa, (cx - t_pausa.get_width()//2, start_y - 50))

        t_hint = f_peq.render("ESC o ENTER para reanudar", True, GRIS_MEDIO)
        ventana.blit(t_hint, (cx - t_hint.get_width()//2, start_y + 8))

        btn_reanudar.draw(ventana, mp)
        btn_menu.draw(ventana, mp)
        btn_salir.draw(ventana, mp)

        pygame.display.flip()
        clock.tick(FPS)

def pantalla_seleccion_rival(ventana, fondo, fuentes, modo, clock):

    f_gr, f_med, f_peq, f_tit, f_sub, f_btn, f_info = fuentes
    cx = VENTANA_HORI // 2

    color_modo  = PALETA_MODOS.get(modo, CYAN)
    nombre_modo = NOMBRE_MODOS.get(modo, modo)

    bw, bh = 300, 62
    gap    = 20
    btn_cpu = Boton(cx - bw//2, 310,        bw, bh, "VS  CPU",        f_btn, CYAN)
    btn_j2  = Boton(cx - bw//2, 310+bh+gap, bw, bh, "VS  JUGADOR  2", f_btn, AMARILLO)
    btn_back = Boton(cx - 90, 310 + (bh+gap)*2 + 10, 180, 40, "VOLVER", f_btn, ROJO)

    CONTROLES = {
        True:  "J1: W / S     CPU: automatico",
        False: "J1: W / S     J2: Flechas Arr/Aba",
    }

    hover_rival = None
    tick = 0

    while True:
        tick += 1
        mp = pygame.mouse.get_pos()

        for ev in pygame.event.get():
            if ev.type == QUIT:
                return None
            if ev.type == pygame.KEYDOWN and ev.key == pygame.K_ESCAPE:
                return None
            if btn_cpu.clicked(ev):  return True
            if btn_j2.clicked(ev):   return False
            if btn_back.clicked(ev): return None

        hover_rival = None
        if btn_cpu.rect.collidepoint(mp):  hover_rival = True
        if btn_j2.rect.collidepoint(mp):   hover_rival = False

        ventana.blit(fondo, (0, 0))
        ov = pygame.Surface((VENTANA_HORI, VENTANA_VERT), pygame.SRCALPHA)
        ov.fill((0, 0, 0, 105))
        ventana.blit(ov, (0, 0))

        pulso   = 0.5 + 0.5 * math.sin(tick * 0.05)
        c_modo  = tuple(min(255, int(c + 40 * pulso)) for c in color_modo)
        t_modo  = f_sub.render(nombre_modo, True, c_modo)
        ventana.blit(t_modo, (cx - t_modo.get_width()//2, 120))

        t_preg = f_med.render("¿Contra quien quieres jugar?", True, GRIS_MEDIO)
        ventana.blit(t_preg, (cx - t_preg.get_width()//2, 185))

        lw = 340
        pygame.draw.line(ventana, color_modo,
                         (cx - lw//2, 160), (cx + lw//2, 160), 2)

        icon_y = 230
        c_cpu = CYAN if hover_rival is True else (60, 60, 80)
        pygame.draw.circle(ventana, c_cpu, (cx - 80, icon_y), 22, 2)
        t_ic = f_peq.render("CPU", True, c_cpu)
        ventana.blit(t_ic, (cx - 80 - t_ic.get_width()//2, icon_y - 8))
        t_vs = f_med.render("VS", True, GRIS_MEDIO)
        ventana.blit(t_vs, (cx - t_vs.get_width()//2, icon_y - 13))
        c_hu = AMARILLO if hover_rival is False else (60, 60, 80)
        pygame.draw.circle(ventana, c_hu, (cx + 80, icon_y), 22, 2)
        t_ih = f_peq.render("J2", True, c_hu)
        ventana.blit(t_ih, (cx + 80 - t_ih.get_width()//2, icon_y - 8))

        btn_cpu.draw(ventana, mp)
        btn_j2.draw(ventana, mp)
        btn_back.draw(ventana, mp)

        if hover_rival is not None:
            tc = f_info.render(CONTROLES[hover_rival], True, color_modo)
            ventana.blit(tc, (cx - tc.get_width()//2, btn_back.rect.bottom + 14))

        t_esc = f_info.render("ESC para volver al menu", True, (55, 55, 75))
        ventana.blit(t_esc, (cx - t_esc.get_width()//2, VENTANA_VERT - 18))

        pygame.display.flip()
        clock.tick(FPS)

def pantalla_menu(ventana, fondo, fuentes, clock):
    f_gr, f_med, f_peq, f_tit, f_sub, f_btn, f_info = fuentes
    cx = VENTANA_HORI // 2

    MODOS_INFO = [
        (MODO_VS_CPU,   "VS CPU",        "1 jugador vs IA con dificultad progresiva",   CYAN,     "7 pts"),
        (MODO_1V1,      "1 vs 1",        "2 jugadores — W/S vs Flechas",               AMARILLO, "7 pts"),
        (MODO_RAPIDO,   "MODO RAPIDO",   "Primer en llegar a 3 puntos gana",            NARANJA,  "3 pts"),
        (MODO_CRONO,    "CONTRARRELOJ",  f"Mas puntos en {TIEMPO_CRONO} segundos",      MAGENTA,  f"{TIEMPO_CRONO}s"),
        (MODO_4J,       "4 JUGADORES",   "Los 4 lados son raquetas — primero en 5",     VERDE,    "5 pts"),
        (MODO_SUPERVIV, "SUPERVIVENCIA", "Cada pared sin defender = -1 vida",           ROJO,     "3 vidas"),
        (MODO_BOLAS2,   "DOBLE BOLA",    "2 bolas simultaneas — primero en 7",         VIOLETA,  "7 pts"),
        (MODO_TURBO,    "TURBO",         f"Bola ultra rapida — {TIEMPO_TURBO}s",        TURQUESA, f"{TIEMPO_TURBO}s"),
    ]

    bw, bh  = 310, 48
    gap_x   = 20
    gap_y   = 14
    total_w = 2 * bw + gap_x
    start_x = cx - total_w // 2
    start_y = 170

    botones = []
    for i, (modo, label, desc, color, meta) in enumerate(MODOS_INFO):
        col = i % 2
        row = i // 2
        bx  = start_x + col * (bw + gap_x)
        by  = start_y + row * (bh + gap_y)
        botones.append((Boton(bx, by, bw, bh, label, f_btn, color), modo, color, desc, meta))

    btn_salir = Boton(cx - 80, VENTANA_VERT - 52, 160, 38, "SALIR", f_btn, ROJO)

    tick = 0
    while True:
        tick += 1
        mp = pygame.mouse.get_pos()
        for ev in pygame.event.get():
            if ev.type == QUIT or (ev.type == pygame.KEYDOWN and ev.key == pygame.K_ESCAPE):
                return None
            if btn_salir.clicked(ev):
                return None
            for btn, modo, color, desc, meta in botones:
                if btn.clicked(ev):
                    return modo

        ventana.blit(fondo, (0, 0))
        ov = pygame.Surface((VENTANA_HORI, VENTANA_VERT), pygame.SRCALPHA)
        ov.fill((0, 0, 0, 95))
        ventana.blit(ov, (0, 0))

        pulso   = 0.5 + 0.5 * math.sin(tick * 0.04)
        ct      = (int(175+80*pulso), int(195+60*pulso), 255)
        t_tit   = f_tit.render("PyPong  Pro", True, ct)
        ventana.blit(t_tit, (cx - t_tit.get_width()//2, 36))

        t_sub = f_peq.render("Selecciona un modo de juego", True, GRIS_MEDIO)
        ventana.blit(t_sub, (cx - t_sub.get_width()//2, 124))

        hover_desc  = None
        hover_meta  = None
        hover_color = GRIS_MEDIO
        for btn, modo, color, desc, meta in botones:
            btn.draw(ventana, mp)
            if btn.rect.collidepoint(mp):
                hover_desc  = desc
                hover_meta  = meta
                hover_color = color

        if hover_desc:
            td = f_info.render(f"{hover_desc}  |  Meta: {hover_meta}", True, hover_color)
            ventana.blit(td, (cx - td.get_width()//2, start_y + 4*(bh+gap_y) + 10))

        btn_salir.draw(ventana, mp)
        t_esc = f_info.render("ESC para salir", True, (55, 55, 75))
        ventana.blit(t_esc, (cx - t_esc.get_width()//2, VENTANA_VERT - 18))

        pygame.display.flip()
        clock.tick(FPS)


def pantalla_fin_2j(ventana, fondo, fuentes, pj, pia, modo, clock, es_ia=True):
    f_gr, f_med, f_peq, f_tit, f_sub, f_btn, f_info = fuentes
    cx      = VENTANA_HORI // 2
    ganaste = pj > pia
    empate  = pj == pia

    if modo == MODO_1V1 or not es_ia:
        res_txt = "GANA J1!" if pj > pia else ("EMPATE!" if empate else "GANA J2!")
    else:
        res_txt = "GANASTE!" if ganaste else ("EMPATE!" if empate else "PERDISTE!")
    res_col = VERDE if (pj >= pia) else ROJO
    if empate: res_col = AMARILLO

    btn_nuevo = Boton(cx - 220, 350, 200, 48, "JUGAR DE NUEVO", f_btn, CYAN)
    btn_menu  = Boton(cx + 20,  350, 200, 48, "MENU PRINCIPAL", f_btn, AMARILLO)

    while True:
        mp = pygame.mouse.get_pos()
        for ev in pygame.event.get():
            if ev.type == QUIT:          return "salir"
            if btn_nuevo.clicked(ev):    return "nuevo"
            if btn_menu.clicked(ev):     return "menu"

        ventana.blit(fondo, (0, 0))
        ov = pygame.Surface((VENTANA_HORI, VENTANA_VERT), pygame.SRCALPHA)
        ov.fill((0, 0, 10, 175))
        ventana.blit(ov, (0, 0))

        t_r = f_tit.render(res_txt, True, res_col)
        ventana.blit(t_r, (cx - t_r.get_width()//2, 155))
        t_s = f_sub.render(f"{pj}  -  {pia}", True, BLANCO)
        ventana.blit(t_s, (cx - t_s.get_width()//2, 248))

        if modo == MODO_1V1:
            nj, nia = "J1", "J2"
        elif modo == MODO_VS_CPU:
            nj, nia = "TU", "CPU"
        else:
            nj  = "J1"
            nia = "CPU" if es_ia else "J2"
        t_l = f_peq.render(f"{nj}              {nia}", True, GRIS_MEDIO)
        ventana.blit(t_l, (cx - t_l.get_width()//2, 296))

        btn_nuevo.draw(ventana, mp)
        btn_menu.draw(ventana, mp)
        pygame.display.flip()
        clock.tick(FPS)


def pantalla_fin_4j(ventana, fondo, fuentes, puntos, vidas, modo, clock):
    f_gr, f_med, f_peq, f_tit, f_sub, f_btn, f_info = fuentes
    cx      = VENTANA_HORI // 2
    nombres = ["J1 (A/D)", "J2 (Arr/Aba)", "J3 (I/K)", "J4 (L/P)"]
    colores = [CYAN, MAGENTA, AMARILLO, VERDE]

    scores      = vidas[:] if modo == MODO_SUPERVIV else puntos[:]
    ganador_idx = scores.index(max(scores))

    btn_nuevo = Boton(cx - 220, 430, 200, 48, "JUGAR DE NUEVO", f_btn, CYAN)
    btn_menu  = Boton(cx + 20,  430, 200, 48, "MENU PRINCIPAL", f_btn, AMARILLO)

    while True:
        mp = pygame.mouse.get_pos()
        for ev in pygame.event.get():
            if ev.type == QUIT:       return "salir"
            if btn_nuevo.clicked(ev): return "nuevo"
            if btn_menu.clicked(ev):  return "menu"

        ventana.blit(fondo, (0, 0))
        ov = pygame.Surface((VENTANA_HORI, VENTANA_VERT), pygame.SRCALPHA)
        ov.fill((0, 0, 10, 175))
        ventana.blit(ov, (0, 0))

        t_g = f_tit.render(f"GANA  {nombres[ganador_idx]}!", True, colores[ganador_idx])
        ventana.blit(t_g, (cx - t_g.get_width()//2, 130))

        for i, (nm, color) in enumerate(zip(nombres, colores)):
            prefijo = "vidas" if modo == MODO_SUPERVIV else "pts"
            marker  = "  <--" if i == ganador_idx else ""
            t_p     = f_sub.render(f"{nm}: {scores[i]} {prefijo}{marker}", True, color)
            ventana.blit(t_p, (cx - t_p.get_width()//2, 240 + i * 46))

        btn_nuevo.draw(ventana, mp)
        btn_menu.draw(ventana, mp)
        pygame.display.flip()
        clock.tick(FPS)

def jugar_2j(ventana, fondo, fuentes, modo, clock, es_ia=None):
    f_gr, f_med, f_peq, f_tit, f_sub, f_btn, f_info = fuentes
    fuentes_hud = (f_gr, f_med, f_peq)

    vel_factor = 1.6 if modo == MODO_TURBO else 1.0
    bola       = Bola(vel_factor)
    bola2      = Bola(vel_factor) if modo == MODO_BOLAS2 else None
    if bola2:
        bola2.reiniciar(dir_hint=-1)

    partic = Particulas()
    meta   = META_RAPIDO if modo == MODO_RAPIDO else META_NORMAL

    if es_ia is None:
        es_ia = modo in (MODO_VS_CPU, MODO_RAPIDO, MODO_CRONO, MODO_BOLAS2, MODO_TURBO)

    dif_ia = 0.75 if modo == MODO_RAPIDO else 1.0

    r_izq = Raqueta(50,
                    (CANCHA_ARR + CANCHA_ABA)//2 - RAQUETA_LARGO//2,
                    RAQUETA_LARGO, RAQUETA_GROSOR, CYAN, "V")
    r_der = Raqueta(CANCHA_DER - 50 - RAQUETA_GROSOR,
                    (CANCHA_ARR + CANCHA_ABA)//2 - RAQUETA_LARGO//2,
                    RAQUETA_LARGO, RAQUETA_GROSOR, MAGENTA, "V")

    if modo == MODO_1V1:
        nj, nia = "J1", "J2"
    elif modo == MODO_VS_CPU:
        nj, nia = "TU", "CPU"
    else:
        nj  = "J1"
        nia = "CPU" if es_ia else "J2"

    teclas = set()
    t_ini  = pygame.time.get_ticks()
    tiempo_restante = TIEMPO_TURBO if modo == MODO_TURBO else TIEMPO_CRONO

    jugando = True
    while jugando:
        clock.tick(FPS)

        for ev in pygame.event.get():
            if ev.type == QUIT:
                return bola.puntos[0], bola.puntos[1], False
            if ev.type == pygame.KEYDOWN:
                teclas.add(ev.key)
                if ev.key == pygame.K_ESCAPE:
                    captura = ventana.copy()
                    res_pausa = menu_pausa(ventana, captura, fuentes, modo, clock)
                    if res_pausa == "menu":
                        return bola.puntos[0], bola.puntos[1], "menu"
                    if res_pausa == "salir":
                        return bola.puntos[0], bola.puntos[1], False
                    t_ini += pygame.time.get_ticks() - (t_ini + (pygame.time.get_ticks() - t_ini))
            if ev.type == pygame.KEYUP:
                teclas.discard(ev.key)

        r_izq.mover_j(pygame.K_w in teclas, pygame.K_s in teclas)
        if not es_ia:
            r_der.mover_j(pygame.K_UP in teclas, pygame.K_DOWN in teclas)
        else:
            r_der.mover_ia(bola, dif_ia)

        bola.mover()
        bola.rebotar_2j(partic)
        r_izq.colisionar(bola, partic, "L")
        r_der.colisionar(bola, partic, "R")

        if bola2:
            bola2.mover()
            bola2.rebotar_2j(partic)
            r_izq.colisionar(bola2, partic, "L")
            r_der.colisionar(bola2, partic, "R")

        if modo in (MODO_CRONO, MODO_TURBO):
            max_t = TIEMPO_TURBO if modo == MODO_TURBO else TIEMPO_CRONO
            elapsed = (pygame.time.get_ticks() - t_ini) // 1000
            tiempo_restante = max(0, max_t - elapsed)
            if tiempo_restante == 0:
                jugando = False
        else:
            if bola.puntos[0] >= meta or bola.puntos[1] >= meta:
                jugando = False
            if bola2 and (bola2.puntos[0] >= meta or bola2.puntos[1] >= meta):
                bola.puntos[0] += bola2.puntos[0]
                bola.puntos[1] += bola2.puntos[1]
                jugando = False

        ventana.blit(fondo, (0, 0))
        draw_campo_2j(ventana, modo)
        partic.update_draw(ventana)
        draw_raqueta(ventana, r_izq.x, r_izq.y, r_izq.w, r_izq.h, r_izq.color)
        draw_raqueta(ventana, r_der.x, r_der.y, r_der.w, r_der.h, r_der.color)
        draw_bola(ventana, bola.x, bola.y, bola.r, bola.color, bola.trail)
        if bola2:
            draw_bola(ventana, bola2.x, bola2.y, bola2.r, bola2.color, bola2.trail)

        tr_disp   = tiempo_restante if modo in (MODO_CRONO, MODO_TURBO) else None
        datos_hud = (bola.puntos[0], bola.puntos[1], bola.golpes, bola.vel, nj, nia)
        draw_hud_2j(ventana, fuentes_hud, datos_hud, modo, tr_disp)

        pygame.display.flip()

    return bola.puntos[0], bola.puntos[1], True


def jugar_4j(ventana, fondo, fuentes, modo, clock):
    f_gr, f_med, f_peq, f_tit, f_sub, f_btn, f_info = fuentes
    fuentes_hud = (f_gr, f_med, f_peq)

    bola      = Bola()
    partic    = Particulas()
    colores_j = [CYAN, MAGENTA, AMARILLO, VERDE]
    vidas     = [3, 3, 3, 3]
    puntos    = [0, 0, 0, 0]

    cx = CANCHA_IZQ + (CANCHA_DER - CANCHA_IZQ) // 2
    cy = CANCHA_ARR + (CANCHA_ABA - CANCHA_ARR) // 2

    r_j1 = Raqueta(cx - RAQUETA_LARGO_H//2, CANCHA_ARR,
                   RAQUETA_LARGO_H, RAQUETA_GROSOR, CYAN,    "H")
    r_j2 = Raqueta(CANCHA_DER - RAQUETA_GROSOR, cy - RAQUETA_LARGO//2,
                   RAQUETA_LARGO, RAQUETA_GROSOR, MAGENTA,  "V")
    r_j3 = Raqueta(cx - RAQUETA_LARGO_H//2, CANCHA_ABA - RAQUETA_GROSOR,
                   RAQUETA_LARGO_H, RAQUETA_GROSOR, AMARILLO, "H")
    r_j4 = Raqueta(CANCHA_IZQ, cy - RAQUETA_LARGO//2,
                   RAQUETA_LARGO, RAQUETA_GROSOR, VERDE,   "V")

    teclas  = set()
    jugando = True

    while jugando:
        clock.tick(FPS)

        for ev in pygame.event.get():
            if ev.type == QUIT:
                return puntos, vidas, False
            if ev.type == pygame.KEYDOWN:
                teclas.add(ev.key)
                if ev.key == pygame.K_ESCAPE:
                    captura   = ventana.copy()
                    res_pausa = menu_pausa(ventana, captura, fuentes, modo, clock)
                    if res_pausa == "menu":
                        return puntos, vidas, "menu"
                    if res_pausa == "salir":
                        return puntos, vidas, False
            if ev.type == pygame.KEYUP:
                teclas.discard(ev.key)

        r_j1.mover_j(pygame.K_a     in teclas, pygame.K_d    in teclas)
        r_j2.mover_j(pygame.K_UP    in teclas, pygame.K_DOWN in teclas)
        r_j3.mover_j(pygame.K_i     in teclas, pygame.K_k    in teclas)
        r_j4.mover_j(pygame.K_l     in teclas, pygame.K_p    in teclas)

        bola.mover()
        bola.rebotar_4j(partic,
                        vidas  if modo == MODO_SUPERVIV else None,
                        colores_j,
                        puntos if modo == MODO_4J       else None,
                        [r_j1, r_j2, r_j3, r_j4])

        r_j1.colisionar(bola, partic, "T")
        r_j2.colisionar(bola, partic, "R")
        r_j3.colisionar(bola, partic, "B")
        r_j4.colisionar(bola, partic, "L")

        if modo == MODO_4J:
            if any(p >= META_4J for p in puntos):
                jugando = False

        elif modo == MODO_SUPERVIV:
            if any(v <= 0 for v in vidas):
                jugando = False

        ventana.blit(fondo, (0, 0))
        draw_campo_4j(ventana)
        partic.update_draw(ventana)

        draw_raqueta(ventana, r_j1.x, r_j1.y, r_j1.w, r_j1.h, r_j1.color, horizontal=True)
        draw_raqueta(ventana, r_j2.x, r_j2.y, r_j2.w, r_j2.h, r_j2.color)
        draw_raqueta(ventana, r_j3.x, r_j3.y, r_j3.w, r_j3.h, r_j3.color, horizontal=True)
        draw_raqueta(ventana, r_j4.x, r_j4.y, r_j4.w, r_j4.h, r_j4.color)
        draw_bola(ventana, bola.x, bola.y, bola.r, bola.color, bola.trail)

        draw_hud_4j(ventana, fuentes_hud, puntos, vidas, modo)

        ctrl_display = [
            ("J1: A / D",   CYAN,     12,               CANCHA_ARR + 8),
            ("J2: Arr/Aba", MAGENTA,  CANCHA_DER - 105, CANCHA_ARR + 8),
            ("J3: I / K",   AMARILLO, 12,               CANCHA_ABA - 22),
            ("J4: L / P",   VERDE,    CANCHA_DER - 80,  CANCHA_ABA - 22),
        ]
        for txt, col, tx, ty in ctrl_display:
            tc = f_info.render(txt, True, col)
            ventana.blit(tc, (tx, ty))

        pygame.display.flip()

    return puntos, vidas, True

def main():
    ventana = pygame.display.set_mode((VENTANA_HORI, VENTANA_VERT))
    pygame.display.set_caption("PyPong Pro")
    fondo   = fondo_gradiente()
    fuentes = crear_fuentes()
    clock   = pygame.time.Clock()

    MODOS_4J            = (MODO_4J, MODO_SUPERVIV)
    MODOS_CON_SELECCION = (MODO_RAPIDO, MODO_CRONO, MODO_BOLAS2, MODO_TURBO)

    modo    = None
    es_ia   = None   
    running = True

    while running:
        if modo is None:
            modo  = pantalla_menu(ventana, fondo, fuentes, clock)
            es_ia = None
            if modo is None:
                break

            if modo == MODO_VS_CPU:
                es_ia = True
            elif modo == MODO_1V1:
                es_ia = False
            elif modo in MODOS_CON_SELECCION:
                es_ia = pantalla_seleccion_rival(ventana, fondo, fuentes, modo, clock)
                if es_ia is None:      
                    modo = None
                    continue

        if modo in MODOS_4J:
            puntos, vidas, normal = jugar_4j(ventana, fondo, fuentes, modo, clock)
            if normal == "menu":
                modo = None
                continue
            if not normal:
                break
            res = pantalla_fin_4j(ventana, fondo, fuentes, puntos, vidas, modo, clock)
        else:
            pj, pia, normal = jugar_2j(ventana, fondo, fuentes, modo, clock, es_ia)
            if normal == "menu":
                modo = None
                continue
            if not normal:
                break
            res = pantalla_fin_2j(ventana, fondo, fuentes, pj, pia, modo, clock, es_ia)

        if res == "nuevo":
            pass          
        elif res == "menu":
            modo = None
        else:
            break

    pygame.quit()


if __name__ == "__main__":
    main()