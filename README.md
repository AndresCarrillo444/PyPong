# 🏓 PyPong Pro

**PyPong Pro** es una versión modernizada y vibrante del clásico *Pong*, desarrollada íntegramente en **Python** con la librería **Pygame**. Este proyecto transforma la mecánica minimalista de los años 70 en una experiencia arcade contemporánea con efectos de partículas, múltiples modos de juego y soporte para hasta 4 jugadores simultáneos.

---

##  Características Principales

###  Modos de Juego Variados
El proyecto incluye **8 modos distintos**, cada uno con reglas y metas específicas:
* **VS CPU / 1 vs 1:** El duelo tradicional con dificultad progresiva.
* **Modo Rápido:** Partidas cortas al primero en anotar 3 puntos.
* **Contrarreloj:** Máxima puntuación en un límite de 60 segundos.
* **4 Jugadores:** Acción en los cuatro bordes de la pantalla (Arriba, Abajo, Izquierda, Derecha).
* **Supervivencia:** Cada fallo resta una de tus 3 vidas.
* **Doble Bola:** Dos bolas en juego simultáneamente para duplicar el caos.
* **Turbo:** Velocidad de bola ultra rápida con límite de tiempo de 45 segundos.

###  Inteligencia Artificial y Físicas
* **IA Adaptativa:** La velocidad y precisión del rival virtual aumentan dinámicamente según el nivel de golpes de la partida.
* **Física de Rebote:** El ángulo de la bola varía según el punto de impacto en la raqueta, permitiendo tiros estratégicos.
* **Velocidad Progresiva:** La bola acelera tras un número determinado de golpes, incrementando la intensidad del juego.

###  Estética Visual
* **Sistema de Partículas:** Explosiones visuales al anotar puntos o colisionar con las raquetas.
* **Efecto de Estela:** Las bolas dejan un rastro dinámico que cambia de color según la velocidad.
* **Interfaz Neon:** Menús estilizados con efectos de pulso y botones interactivos.

---

##  Controles

| Acción | Jugador 1 | Jugador 2 | Jugador 3 | Jugador 4 |
| :--- | :--- | :--- | :--- | :--- |
| **Moverse (V)** | `W` / `S` | `Arriba` / `Abajo` | `I` / `K` | `L` / `P` |
| **Moverse (H)** | `A` / `D` | --- | `I` / `K` | --- |
| **Pausar** | `ESC` | --- | --- | --- |

---

## Instalación y Ejecución

1. **Requisitos Previos**
   Asegúrate de tener instalado Python y la librería Pygame:
   ```bash
   pip install pygame
   pip install numpy
   
2. **Instala las dependencias**
   ```bash
   python PyPong.py

## Detalles Técnicos
Lenguaje: Python 3.x

Motor: Pygame

Resolución: 900x660 píxeles

Arquitectura: Orientada a objetos (Clases para Bola, Raqueta, Particula, Boton).

## Licencia
Este proyecto es de código abierto. ¡Siéntete libre de modificarlo, añadir nuevos modos o mejorar la IA!

Desarrollado con ❤️ por **Andres Carrillo/AndresCarrillo444**
