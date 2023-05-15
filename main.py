import pygame
pygame.init()
from pygame.locals import *
import sys
import random
import math
import numpy as np 


#setup
clock = pygame.time.Clock()
FPS = 120
pygame.display.set_caption("Physics")
#icon = pygame.image.load("icon.png")
#pygame.display.set_icon(icon)
width, height = 960, 540
screen = pygame.display.set_mode((width, height), pygame.RESIZABLE)
font = pygame.font.Font('freesansbold.ttf', 20)
running = True
gravity = True#bool(int(input('gravity? (1 or 0)')))
gConst = 1
follow = 1
followX, followY = width/2, height/2
following = 0
offsetX, offsetY = 0, 0
offsetSpeed = 10
scale = 0.001
scaleFactor = 1.02
paused = False
speed = 1
speedFactor = 1.02
showVelocity = False
numberState = 0 #0 = normal, 1 = shorthand, 2 = scientific

#Calculates the distance in pixels between two points
def distance(x1, y1, x2, y2):
    return ((x2 - x1) ** 2 + (y2 - y1) ** 2) ** (1 / 2)


#Calculates the angle of a vector given its origin and x,y
def calculate_angle(x1, y1, x2, y2):
    if x1 == x2:
        if y1 == y2:
            return 0
        if y2 > y1:
            return 90
        else:
            return -90
    elif x1 > x2:
        return math.degrees(math.atan((y2 - y1) / (x2 - x1))) + 180
    elif x2 > x1 and y1 > y2:
        return math.degrees(math.atan((y2 - y1) / (x2 - x1))) + 360
    else:
        return math.degrees(math.atan((y2 - y1) / (x2 - x1)))
    
#Faster image function, returns an image
def image(img):
    return pygame.image.load(str(img) + '.png').convert_alpha()

#Prunes inactive objects
def pruned(l):
    newlist = []
    for i in l:
        if not i.done:
            newlist.append(i)
    return newlist

#Rounds to the nearest 1/place
def roundPlace(n, place = 1):
    return math.ceil(n * place) / place

#Adds suffixes to large numbers
def shortNumber(n):
    if n < 0:
        sign = -1
    else:
        sign = 1

    num = abs(n)
    
    if num >= 1000 and num < 1000000:
        return str(sign * roundPlace(num/1000, 10)) + 'K'
    elif num >= 1000000 and num < 1000000000:
        return str(sign * roundPlace(num/1000000, 10)) + 'M'
    elif num >= 1000000000 and num < 1000000000000:
        return str(sign * roundPlace(num/1000000000, 10)) + 'B'
    elif num >= 1000000000000 and num < 1000000000000000:
        return str(sign * roundPlace(num/1000000000000, 10)) + 'T'
    elif num > 1000000000000000:
        return str(sign * roundPlace(num/1000000000000000, 10)) + 'Q'
    
#Generates a random boolean
def randbool(weight = 50):
    if random.randint(0, 100) > weight:
        return True
    else:
        return False

def randsign(weight = 50):
    if random.randint(0, 100) > weight:
        return 1
    else:
        return -1

#Rotates a list
def rotateList(l, n):
    return l[n:] + l[:n]

#Imports files based on path, returns single file or a list of files
def import_file(obj, amount = 1, path='assets/', filetype = 'png'):
    storage = []
    if filetype == 'png':
        if amount > 1:
            for i in range(amount):
                storage.append(image(path + obj + '_' + str(i)))
            return storage
        else:
            return image(path + obj)
    else:
        if amount > 1:
            for i in range(amount):
                storage.append(path + obj + '_' + str(i) + '.'+filetype)
            return storage
        else:
            return path + obj + '.' + filetype

class Object():
    objects = []
    codeIterator = 0
    def __init__(self, x, y, r, m, v = [0, 0], defaultColor = (255, 255, 255)):
        self.x = x
        self.y = y
        self.r = r #radius
        self.m = m #mass
        self.v = np.array(v)
        self.a = np.array([0, 0])
        self.defaultColor = defaultColor
        self.color = (255, 255, 255)
        self.code = Object.codeIterator
        Object.codeIterator += 1
    def update(self):
        self.v += self.a * speed
        self.x += self.v[0] * speed
        self.y += self.v[1] * speed
    def render(self):
        if self.code == following and follow:
            self.color = (180, 180, 255)
        elif self.code == closestIndex and not follow:
            self.color = (180, 180, 255)
        else:
            self.color = self.defaultColor
        pygame.draw.circle(screen, self.color, ((self.x - followX + offsetX) * scale + width/2, (self.y - followY + offsetY) * scale + height/2), self.r * scale + 1)
    def renderVelocity(self):
        x, y = (self.x - followX + offsetX) * scale + width/2, (self.y - followY + offsetY) * scale + height/2
        pygame.draw.line(screen, (255, 255, 255), (x, y), (x + self.v[0] * scale * 100 , y + self.v[1] * scale * 100))

class Text():
    texts = []
    def __init__(self, x, y, message, life = -1):
        self.message = message
        self.text = font.render(message, True, (255, 255, 255))
        self.rect = self.text.get_rect()
        self.center = (x, y)
        self.rect.center = self.center
        self.life = life
        self.hidden = False
    def update(self):
        if self.life != -1:
            self.life -=1
        self.rect = self.text.get_rect()
        self.rect.center = self.center
    def render(self):
        if not self.hidden:
            self.text = font.render(self.message, True, (255, 255, 255))
            screen.blit(self.text, self.rect)
#Main rendering function
def draw():
    global followX
    global followY
    global following
    global offsetX
    global offsetY
    global follow
    global scale
    global paused
    global speed
    global speedFactor
    global offsetSpeed
    global numberState
    global closestIndex
    global showVelocity

    if pState == 1:
        paused = not paused
        print(paused)

    if oState == 1:
        numberState += 1
        print(numberState)
        if numberState == 3:
            numberState = 0

    if vState == 1:
        showVelocity = not showVelocity

    if lshift_key:
        offsetSpeed = 2
    else:
        offsetSpeed = 10

    if w_key and s_key:
        follow = 0
    elif w_key:
        offsetY += offsetSpeed / scale
        follow = 0
    elif s_key:
        offsetY -= offsetSpeed / scale
        follow = 0

    if a_key and d_key:
        follow = 0
    elif a_key:
        offsetX += offsetSpeed / scale
        follow = 0
    elif d_key:
        offsetX -= offsetSpeed / scale
        follow = 0

    if q_key and e_key:
        pass
    elif q_key:
        scale /= scaleFactor
    elif e_key:
        scale *= scaleFactor

    if n_key and m_key:
        pass
    elif n_key:
        speed /= speedFactor
    elif m_key:
        speed *= speedFactor

    if b_key:
        speed = 1

    if speed > 10:
        speed = 10

    Text.texts[0].message = 'x' + str(math.ceil(speed * 1000)/1000)

    mousePos = pygame.mouse.get_pos()
    relativeMousePos = (roundPlace((mousePos[0] - width/2) / scale - offsetX + followX, 1000), roundPlace((mousePos[1] - height/2) / scale - offsetY + followY, 1000))

    if numberState == 0:
        formattedMousePos = relativeMousePos
    if numberState == 1:
        formattedMousePos = (shortNumber(relativeMousePos[0]), shortNumber(relativeMousePos[1]))
    elif numberState == 2:
        formattedMousePos = (np.format_float_scientific(relativeMousePos[0], unique=False, precision=3), np.format_float_scientific(relativeMousePos[1], unique=False, precision=3))

    #print(relativeMousePos)
    Text.texts[1].message = str(formattedMousePos[0]) + ', ' + str(formattedMousePos[1])
    Text.texts[1].center = (mousePos[0], mousePos[1] + 20)


    closest = distance(Object.objects[0].x, Object.objects[0].y, relativeMousePos[0], relativeMousePos[1])
    closestIndex = 0
    for i in range(1, len(Object.objects)):
        distanceFromMouse = distance(Object.objects[i].x, Object.objects[i].y, relativeMousePos[0], relativeMousePos[1])
        if distanceFromMouse < closest:
            closest = distanceFromMouse
            closestIndex = i

    if mousetick:
        following = closestIndex
        follow = 1
        offsetX, offsetY = 0, 0
            
        #following += 1
        #offsetX, offsetY = 0, 0
        #follow = 1
        #if following >= len(Object.objects):
        #    following = 0
    
    if follow:
        followX = Object.objects[following].x
        followY = Object.objects[following].y

    if not paused:
        for root in range(len(Object.objects) - 1):
            for iterator in range(root + 1, len(Object.objects)):
                r = Object.objects[root]
                i = Object.objects[iterator]
                
                dx = r.x - i.x
                dy = r.y - i.y
                angle = -math.atan2(dy,dx)

                firstRotationMatrix = np.array([
                    [math.cos(angle), math.sin(angle)],
                    [-math.sin(angle), math.cos(angle)]
                    ])

                secondRotationMatrix = np.array([
                    [math.cos(angle), -math.sin(angle)],
                    [math.sin(angle), math.cos(angle)]
                    ])
                d = distance(r.x, r.y, i.x, i.y)
                
                if gravity:
                    #gravity
                    force = gConst * speed * r.m * i.m / (d)**2

                    rVRotated = np.matmul(r.v, firstRotationMatrix)
                    iVRotated = np.matmul(i.v, firstRotationMatrix)

                    rVRotated[0] -= force/r.m
                    iVRotated[0] += force/i.m

                    rVFinal = np.matmul(rVRotated, secondRotationMatrix)
                    iVFinal = np.matmul(iVRotated, secondRotationMatrix)

                    Object.objects[root].v = rVFinal
                    Object.objects[iterator].v = iVFinal
                    
                if d <= r.r + i.r:
                    #collision
                    rVRotated = np.matmul(r.v, firstRotationMatrix)
                    iVRotated = np.matmul(i.v, firstRotationMatrix)

                    rVX = ((r.m - i.m) * rVRotated[0] + 2 * i.m * iVRotated[0]) / (r.m + i.m)
                    iVX = ((i.m - r.m) * iVRotated[0] + 2 * r.m * rVRotated[0]) / (r.m + i.m)

                    rVRotatedFinal = np.array([rVX, rVRotated[1]])
                    iVRotatedFinal = np.array([iVX, iVRotated[1]])

                    rVFinal = np.matmul(rVRotatedFinal, secondRotationMatrix)
                    iVFinal = np.matmul(iVRotatedFinal, secondRotationMatrix)

                    Object.objects[root].v = rVFinal
                    Object.objects[iterator].v = iVFinal
    
    screen.fill((0, 0, 0))    
    for obj in Object.objects:
        if not paused:
            obj.update()
        obj.render()
        if showVelocity:
            obj.renderVelocity()
    
    keepIndex = []
    for text in Text.texts:
        if not text.life == 0:
            keepIndex.append(text)
            text.update()
            text.render()
    Text.texts = keepIndex.copy()

    pygame.draw.line(screen, (255, 255, 255),
        ((Object.objects[closestIndex].x - followX + offsetX) * scale + width/2, (Object.objects[closestIndex].y - followY + offsetY) * scale + height/2),
        mousePos, 1)
    
mousetick=0
pState = 0 #0: off, 1: on, 2: lifted
oState = 0
vState = 0

#Object.objects.append(Object(100, 100, 30, 100, v = [4.8, 1]))
#Object.objects.append(Object(200, 100, 10, 100, v = [0.5, 0.1]))
#Object.objects.append(Object(250, 100, 10, 100, v = [0.5, -0.1]))

#Object.objects.append(Object(100, 300, 5, 20, v = [0, -1.2]))
#Object.objects.append(Object(200, 100, 5, 20, v = [0.0, 0.0]))
#Object.objects.append(Object(500, 300, 5, 20, v = [0, -2.2]))
#Object.objects.append(Object(1900, 100, 1000, 15000, v = [0.0, 0.0]))

#Object.objects.append(Object(700, 100, 5, 1, v = [0, -3]))
#Object.objects.append(Object(400, 30, 10, 2000, v = [0.5, -4.8]))
#Object.objects.append(Object(700, 50, 5, 1, v = [0, -3]))
#Object.objects.append(Object(2800, 100, 2000, 50000, v = [2.0, -10]))
#Object.objects.append(Object(20000, 100, 5000, 2000000, v = [0.0, 0]))

#Stars
for i in range(random.randint(10, 20)):
    x, y = random.randint(-1000000, 1000000), random.randint(-1000000, 1000000)
    starSize = random.randint(4000, 20000)
    Object.objects.append(Object(
        x,
        y,
        starSize, starSize ** 2,
        v = [random.randint(-10, 10), random.randint(-10, 10)],
        defaultColor = (245, random.randint(66, 200), 66)))

    #Planets
    for i in range(random.randint(0, 3)):
        planetSize = random.randint(400, 2000)
        Object.objects.append(Object(
            x + random.randint(2 * starSize, 5 * starSize) * randsign(),
            y + random.randint(2 * starSize, 5 * starSize) * randsign(),
            planetSize, planetSize ** 2,
            v = [random.randint(-200, 200), random.randint(-200, 200)],
            defaultColor = (random.randint(80, 150), random.randint(50, 120), random.randint(50, 120))
            ))

Text.texts.append(Text(10, 20, '')) #speed
Text.texts.append(Text(100, 100, '')) #mouse coords

#main loop
while running:

    #main events + mouse detection
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
            pygame.quit()
            sys.exit()
        elif event.type == VIDEORESIZE:
            screen = pygame.display.set_mode((event.w,event.h),pygame.RESIZABLE)
            width=screen.get_width()
            height=screen.get_height()
        elif event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 1:
                mousetick=1
            elif event.button == 2:
                mousetick=2
            elif event.button == 3:
                mousetick=3

    keys = pygame.key.get_pressed()
    if keys[pygame.K_d]:
        d_key=True
    else:
        d_key=False
    if keys[pygame.K_a]:
        a_key=True
    else:
        a_key=False
    if keys[pygame.K_s]:
        s_key=True
    else:
        s_key=False
    if keys[pygame.K_w]:
        w_key=True
    else:
        w_key=False
    if keys[pygame.K_q]:
        q_key=True
    else:
        q_key=False
    if keys[pygame.K_e]:
        e_key=True
    else:
        e_key=False
    if keys[pygame.K_p]:
        p_key=True
    else:
        p_key=False
    if keys[pygame.K_n]:
        n_key=True
    else:
        n_key=False
    if keys[pygame.K_m]:
        m_key=True
    else:
        m_key=False
    if keys[pygame.K_b]:
        b_key=True
    else:
        b_key=False
    if keys[pygame.K_LSHIFT]:
        lshift_key=True
    else:
        lshift_key=False
    if keys[pygame.K_o]:
        o_key=True
    else:
        o_key=False
    if keys[pygame.K_v]:
        v_key=True
    else:
        v_key=False

    if v_key:
        if vState == 0:
            vState = 1
    else:
        if vState == 2:
            vState = 0

    if o_key:
        if oState == 0:
            oState = 1
    else:
        if oState == 2:
            oState = 0
    
    if p_key:
        if pState == 0:
            pState = 1
    else:
        if pState == 2:
            pState = 0
            

    #print(pState)
    
    #updates
    draw()
    if vState == 1:
        vState = 2 #showVelocity key reset
    if pState == 1:
        pState = 2 #pause key reset
    if oState == 1:
        oState = 2 #shorthand key reset
    mousetick = 0 #mousetick reset    
    pygame.display.update()
    clock.tick(FPS)
