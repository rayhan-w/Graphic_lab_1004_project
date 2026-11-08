"""
PROJECT 1: Dhaka Traffic - Day & Night (2D Animated Real-Life Scene)
=====================================================================
Real-life idea: Dhaka'r rastay rickshaw, car ar bus chole, traffic
light er signal mene thame/chole, din-raat bodlay, brishtio namano jay.

Lab er jekhan theke neya:
  Lab 1 -> GL_QUADS / GL_TRIANGLES diye shape (building, gari, rasta)
  Lab 2 -> GL_TRIANGLE_FAN diye circle (chaka, surjo, chaad, signal light)
           GL_LINES diye road er dashed line + brishtir fota
  Lab 3 -> glTranslatef / glRotatef / glScalef + glPushMatrix/glPopMatrix
           (chaka ghora, megh vosha, ekই function diye onek building/gari)
  Lab 4 -> glutTimerFunc diye animation (Lissajous er motoi update loop)
  Lab 5 -> Keyboard (special + normal) ar Mouse event handling
           (square move er bodle ekhane rickshaw move hoy)

Controls:
  LEFT / RIGHT Arrow  -> Nijer rickshaw ta shamne-pichone chalao
  D                   -> Din (Day)
  N                   -> Raat (Night)
  R                   -> Brishti on/off (Rain)
  P                   -> Animation pause / play
  Mouse Click         -> Din / Raat bodlabe
  ESC                 -> Bondho
"""

from OpenGL.GLUT import *
from OpenGL.GLU import *
from OpenGL.GL import *
import math

W, H = 1000, 600


rickshaw_x = 180
wheel_angle = 0
car_x = 650
bus_x = 350
cloud_x = 0
sun_t = 0.0
rain_offset = 0
frame = 0
is_day = True
rain_on = False
paused = False


STARS = [(60 + (i * 137) % 900, 470 + (i * 53) % 110) for i in range(35)]



def drawCircle(x, y, r):
    """GL_TRIANGLE_FAN diye vora circle - Lab 2 (two-6) er technique."""
    glBegin(GL_TRIANGLE_FAN)
    glVertex2f(x, y)
    for i in range(361):
        a = math.radians(i)
        glVertex2f(x + r * math.cos(a), y + r * math.sin(a))
    glEnd()


def drawRect(x, y, w, h):
    """GL_QUADS diye rectangle - Lab 1 er technique."""
    glBegin(GL_QUADS)
    glVertex2f(x, y)
    glVertex2f(x + w, y)
    glVertex2f(x + w, y + h)
    glVertex2f(x, y + h)
    glEnd()


def drawTriangle(x1, y1, x2, y2, x3, y3):
    glBegin(GL_TRIANGLES)
    glVertex2f(x1, y1)
    glVertex2f(x2, y2)
    glVertex2f(x3, y3)
    glEnd()


def drawText(x, y, text):
    glRasterPos2f(x, y)
    for ch in text:
        glutBitmapCharacter(GLUT_BITMAP_HELVETICA_18, ord(ch))


def drawWheel(x, y, r):
    """Ghurnayman chaka: translate + rotate diye spoke ghore (Lab 3)."""
    glColor3f(0.1, 0.1, 0.1)
    drawCircle(x, y, r)
    glPushMatrix()
    glTranslatef(x, y, 0)
    glRotatef(wheel_angle, 0, 0, 1)
    glColor3f(0.85, 0.85, 0.85)
    glBegin(GL_LINES)
    glVertex2f(-r, 0); glVertex2f(r, 0)
    glVertex2f(0, -r); glVertex2f(0, r)
    glEnd()
    glPopMatrix()
    glColor3f(0.9, 0.9, 0.9)
    drawCircle(x, y, r * 0.3)



def drawSkyBody():
    """Din e surjo, raat e chaad - ektai jaygay ghore (Lab 4 er curve er moto param)."""
    sx = 120 + (sun_t * 60) % 760
    sy = 500 + 25 * math.sin(sun_t * 0.7)
    if is_day:
        glColor3f(1.0, 0.8, 0.0)
        drawCircle(sx, sy, 34)
    else:
        glColor3f(0.95, 0.95, 0.85)
        drawCircle(sx, sy, 28)
        glColor3f(0.07, 0.09, 0.25)
        drawCircle(sx + 12, sy + 8, 24)
        glColor3f(1, 1, 1)
        glBegin(GL_POINTS)
        for (x, y) in STARS:
            glVertex2f(x, y)
        glEnd()


def drawCloud(cx, cy, s):
    """Megh = koyekta circle eksathe, glScalef diye chhoto-boro (Lab 3)."""
    glPushMatrix()
    glTranslatef(cx, cy, 0)
    glScalef(s, s, 1)
    if is_day:
        glColor3f(1, 1, 1)
    else:
        glColor3f(0.45, 0.48, 0.6)
    drawCircle(0, 0, 22)
    drawCircle(24, 4, 28)
    drawCircle(52, 0, 22)
    drawCircle(26, -8, 24)
    glPopMatrix()


def drawBuilding(x, h, r, g, b):
    """Ekই function, alada alada translate/scale diye onek building (Lab 3-lab er house er moto)."""
    glColor3f(r, g, b)
    drawRect(x, 230, 110, h)

    for row in range(int(h // 42)):
        for col in range(3):
            if is_day:
                glColor3f(0.75, 0.88, 0.95)
            else:
                glColor3f(1.0, 0.85, 0.35)
            drawRect(x + 12 + col * 32, 245 + row * 42, 18, 24)


def drawRoad():
    glColor3f(0.22, 0.22, 0.24)
    drawRect(0, 0, W, 230)
    glColor3f(0.35, 0.35, 0.35)
    drawRect(0, 218, W, 12)

    glColor3f(1, 1, 1)
    glBegin(GL_LINES)
    for x in range(0, W, 70):
        glVertex2f(x + 10, 148)
        glVertex2f(x + 45, 148)
        glVertex2f(x + 10, 72)
        glVertex2f(x + 45, 72)
    glEnd()


def traffic_state():
    """frame counter theke signal: GREEN -> YELLOW -> RED -> abar GREEN."""
    cycle = frame % 540
    if cycle < 300:
        return "GREEN"
    elif cycle < 360:
        return "YELLOW"
    else:
        return "RED"


def drawTrafficLight():
    state = traffic_state()
    glColor3f(0.15, 0.15, 0.15)
    drawRect(880, 230, 10, 150)
    drawRect(858, 368, 54, 118)
    lights = [("RED", 455, (1, 0.15, 0.15)),
              ("YELLOW", 418, (1, 0.8, 0)),
              ("GREEN", 381, (0.15, 0.9, 0.3))]
    for name, cy, (r, g, b) in lights:
        if name == state:
            glColor3f(r, g, b)
            drawCircle(885, cy, 15)
        else:
            glColor3f(r * 0.3, g * 0.3, b * 0.3)
            drawCircle(885, cy, 15)


def drawCar(x, y):
    glColor3f(0.85, 0.2, 0.2)
    drawRect(x, y, 130, 30)
    drawTriangle(x + 128, y, x + 148, y, x + 128, y + 22)
    glColor3f(0.7, 0.1, 0.1)
    drawRect(x + 28, y + 30, 68, 26)
    glColor3f(0.7, 0.9, 1.0)
    drawRect(x + 34, y + 34, 24, 18)
    drawRect(x + 64, y + 34, 24, 18)
    if not is_day:
        glColor3f(1, 0.95, 0.6)
        drawTriangle(x + 148, y + 8, x + 195, y - 2, x + 195, y + 22)
    drawWheel(x + 28, y, 15)
    drawWheel(x + 105, y, 15)


def drawBus(x, y):
    glColor3f(0.1, 0.55, 0.3)
    drawRect(x, y, 210, 58)
    glColor3f(0.85, 0.95, 1.0)
    for i in range(5):
        drawRect(x + 14 + i * 38, y + 30, 28, 20)
    glColor3f(1, 0.8, 0)
    drawRect(x, y + 12, 210, 8)
    drawWheel(x + 40, y, 16)
    drawWheel(x + 170, y, 16)


def drawRickshaw(x, y):
    """User er hero vehicle - Arrow key diye chole."""

    glColor3f(0.1, 0.6, 0.75)
    glBegin(GL_TRIANGLE_FAN)
    glVertex2f(x + 42, y + 62)
    for i in range(181):
        a = math.radians(i)
        glVertex2f(x + 42 + 46 * math.cos(a), y + 62 + 34 * math.sin(a))
    glEnd()
    glColor3f(0.95, 0.55, 0.1)
    drawRect(x + 8, y + 30, 78, 32)
    glColor3f(0.2, 0.2, 0.7)
    drawRect(x + 88, y + 28, 30, 10)

    glColor3f(0.98, 0.8, 0.6)
    drawCircle(x + 103, y + 58, 10)
    glColor3f(0.15, 0.5, 0.2)
    glBegin(GL_LINES)
    glVertex2f(x + 103, y + 48); glVertex2f(x + 103, y + 30)
    glVertex2f(x + 103, y + 42); glVertex2f(x + 122, y + 34)
    glVertex2f(x + 103, y + 30); glVertex2f(x + 118, y + 14)
    glEnd()
    glColor3f(0.3, 0.3, 0.3)
    glBegin(GL_LINES)
    glVertex2f(x + 20, y + 30); glVertex2f(x + 20, y + 14)
    glVertex2f(x + 78, y + 30); glVertex2f(x + 78, y + 14)
    glVertex2f(x + 103, y + 28); glVertex2f(x + 124, y + 14)
    glEnd()
    drawWheel(x + 20, y + 14, 14)
    drawWheel(x + 78, y + 14, 14)
    drawWheel(x + 124, y + 14, 14)


def drawRain():
    """GL_LINES diye helano brishtir fota - offset diye niche name (Lab 4 animation)."""
    glColor3f(0.65, 0.8, 1.0)
    glBegin(GL_LINES)
    for i in range(90):
        x = (i * 47) % W
        y = (i * 89 - rain_offset) % H
        glVertex2f(x, y)
        glVertex2f(x - 5, y - 18)
    glEnd()



def main():
    drawSkyBody()
    drawCloud((cloud_x) % 1150 - 120, 520, 1.0)
    drawCloud((cloud_x * 0.6 + 420) % 1150 - 120, 555, 0.7)
    drawCloud((cloud_x * 0.8 + 760) % 1150 - 120, 495, 0.55)

    drawBuilding(30, 190, 0.75, 0.55, 0.45)
    drawBuilding(165, 250, 0.5, 0.6, 0.75)
    drawBuilding(300, 165, 0.7, 0.65, 0.5)
    drawBuilding(435, 225, 0.55, 0.7, 0.6)
    drawBuilding(565, 180, 0.72, 0.5, 0.6)
    drawBuilding(695, 255, 0.5, 0.55, 0.7)

    drawRoad()
    drawTrafficLight()
    drawBus(bus_x, 168)
    drawCar(car_x, 92)
    drawRickshaw(rickshaw_x, 18)

    if rain_on:
        drawRain()


    glColor3f(1, 1, 1) if not is_day else glColor3f(0.1, 0.1, 0.3)
    drawText(18, 568, "DHAKA TRAFFIC  |  D=Day  N=Night  R=Rain  P=Pause  Arrows=Rickshaw  Signal: " + traffic_state())


def showScreen():
    if is_day:
        glClearColor(0.55, 0.82, 1.0, 1)
    else:
        glClearColor(0.07, 0.09, 0.25, 1)
    glClear(GL_COLOR_BUFFER_BIT)
    glMatrixMode(GL_PROJECTION)
    glLoadIdentity()
    glOrtho(0, W, 0, H, 0, 1)
    glMatrixMode(GL_MODELVIEW)
    glLoadIdentity()
    glEnable(GL_BLEND)
    glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)
    glPointSize(3)
    main()
    glutSwapBuffers()



def update(value):
    global car_x, bus_x, cloud_x, sun_t, rain_offset, frame, wheel_angle
    if not paused:
        frame += 1
        sun_t += 0.02
        cloud_x += 0.7
        rain_offset += 14
        state = traffic_state()
        if state != "RED":
            speed = 4 if state == "GREEN" else 2
            car_x += speed
            bus_x -= speed * 0.8
            wheel_angle -= speed * 3
            if car_x > W + 160:
                car_x = -170
            if bus_x < -230:
                bus_x = W + 20
    glutPostRedisplay()
    glutTimerFunc(30, update, 0)



def specialKeys(key, x, y):
    global rickshaw_x, wheel_angle
    if key == GLUT_KEY_RIGHT:
        rickshaw_x = min(rickshaw_x + 12, W - 150)
        wheel_angle -= 25
    elif key == GLUT_KEY_LEFT:
        rickshaw_x = max(rickshaw_x - 12, 0)
        wheel_angle += 25
    glutPostRedisplay()


def normalKeys(key, x, y):
    global is_day, rain_on, paused
    if key == b'd' or key == b'D':
        is_day = True
    elif key == b'n' or key == b'N':
        is_day = False
    elif key == b'r' or key == b'R':
        rain_on = not rain_on
    elif key == b'p' or key == b'P':
        paused = not paused
    elif key == b'\x1b':
        sysExit()
    glutPostRedisplay()


def mouseClick(button, state, x, y):
    global is_day
    if button == GLUT_LEFT_BUTTON and state == GLUT_DOWN:
        is_day = not is_day
    glutPostRedisplay()


def sysExit():
    import sys
    sys.exit(0)


glutInit()
glutInitDisplayMode(GLUT_RGBA | GLUT_DOUBLE)
glutInitWindowSize(W, H)
glutInitWindowPosition(100, 100)
glutCreateWindow(b"Project 1 - Dhaka Traffic Day & Night")
glutDisplayFunc(showScreen)
glutSpecialFunc(specialKeys)
glutKeyboardFunc(normalKeys)
glutMouseFunc(mouseClick)
glutTimerFunc(30, update, 0)
glutMainLoop()
