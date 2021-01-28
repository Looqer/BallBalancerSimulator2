import pygame
import sys
import time
import matplotlib.pyplot as plt

from math import *

pygame.init()
width = 800
height = 800
outerHeight = 800
margin = 20
display = pygame.display.set_mode((width, height))
end_time = time.time() + 5

#game_surf = pygame.Surface((width, height))
trace = pygame.Surface(display.get_size())

pygame.display.set_caption("Ball simulator")
clock = pygame.time.Clock()

surface1 = pygame.Surface((50,50))
surface1.fill((255,0,0))
surface2 = pygame.Surface((50,50))
surface2.fill((0,255,0))

background = (50, 50, 50)
white = (236, 240, 241)
gray = (123, 125, 125)
black = (23, 32, 42)
red = (255, 0, 0)
green = (0, 255, 0)
stickColor = (249, 231, 159)
gravityColor = (100, 0 ,100)

colors = [black]

balls = []
noBalls = 1
radius = 10
friction = 0.1
bounce = 0.9
Pvalue = 0
Ivalue = 0
Dvalue = 0
Kp = 0.001
Ki = 0
Kd = 0.04

FUZZYX = 1
Fclosex = 0
Fmediumx = 0
Ffarx = 0

FUZZYY = 1
Fclosey = 0
Fmediumy = 0
Ffary = 0



class Ball:
    def __init__(self, x, y, oldy, oldx, xv, yv, xa, ya, xF, yF, mass, grav, speed, color, angle, ballNum, errorx, errory, errorpx, errorpy, errxsum, errysum):
        self.x = x
        self.y = y
        self.oldy = oldy
        self.oldx = oldx
        self.xv = xv
        self.yv = yv
        self.xa = xa
        self.ya = ya
        self.xF = xF
        self.yF = yF
        self.mass = 1
        self.grav = 9.81
        self.color = color
        self.angle = angle
        self.speed = speed
        self.ballNum = ballNum
        self.font = pygame.font.SysFont("Agency FB", 10)
        self.errorx = 0.0
        self.errory = 0.0
        self.errorpx = 0.0
        self.errorpy = 0.0
        self.slidex = 0.0
        self.slidey = 0.0
        self.errxsum = 0.0
        self.errysum = 0.0
        self.destX = 0
        self.destY = 0


    # Draws Balls on Display Window
    def draw(self, x, y):
        pygame.draw.ellipse(display, self.color, (x - radius, y - radius, radius*2, radius*2))


    # Moves the Ball around the Screen
    def move(self):

        #friction
        self.speed -= (self.speed)/30

        #stop if movement is slow
        if self.speed <= .1:
            self.speed = 0

        #save last step position values
        self.oldx = self.x
        self.oldy = self.y

        #change position with velocity
        self.x = self.x + self.xv
        self.y = self.y + self.yv

        #bouncing
        if not (self.x < width - radius - margin):
            self.xv = -self.xv * bounce
        if not(radius + margin < self.x):
            self.xv = -self.xv * bounce
        if not (self.y < height - radius - margin):
            self.yv = -self.yv * bounce
        if not(radius + margin < self.y):
            self.yv = -self.yv * bounce



    #wheel trace
    def destinationWheel(self):

        #target position
        self.destX = (cos(time.time()*4)+3.14) *100
        self.destY = (sin(time.time()*4)+3.14) *100

        #target position limit
        if self.destX >= 800:
            self.destX = 800
        if self.destX <= 0:
            self.destX = 0
        if self.destY >= 800:
            self.destY = 800
        if self.destY <= 0:
            self.destY = 0



class CueStick:

    def __init__(self, x, y, length, color):
        self.x = x
        self.y = y
        self.length = length
        self.color = color
        self.tangent = 0

    #Applying force to ball
    def applyForce(self, cueBall, force):
        cueBall.xv += (cueBall.x - self.x)/10
        cueBall.yv += (cueBall.y - self.y)/10

    #Draws CueStick
    def draw(self, cuex, cuey):
        self.x, self.y = pygame.mouse.get_pos()
        self.tangent = (degrees(atan2((cuey - self.y), (cuex - self.x))))
        pygame.draw.line(display, white, (cuex + self.length*cos(radians(self.tangent)), cuey + self.length*sin(radians(self.tangent))), (cuex, cuey), 1)
        pygame.draw.line(display, self.color, (self.x, self.y), (cuex, cuey), 3)

    #Applying gravity force to ball
    def applyGrav(self, cueBall, levelBallX, levelBallY, destBall, forceOfGrav, cuex, cuey):

        #Error calculation and saving previous values
        cueBall.errorpx = cueBall.errorx
        cueBall.errorpy = cueBall.errory
        cueBall.errorx = self.x - cueBall.destX
        cueBall.errory = self.y - cueBall.destY

        #Fuzzyfication x
        if(50>abs(cueBall.errorx)>0):
            Fclosex = -abs(cueBall.errorx)*2+100
        else:
            Fclosex = 0

        if (100 > abs(cueBall.errorx) > 50):
            Fmediumx = abs(cueBall.errorx) * 2 - 100
        elif (150 > abs(cueBall.errorx) > 100):
            Fmediumx = -abs(cueBall.errorx) * 2 + 300
        else:
            Fmediumx = 0

        if (200 > abs(cueBall.errorx) > 150):
            Ffarx = abs(cueBall.errorx) * 2 - 300
        elif (abs(cueBall.errorx) > 200):
            Ffarx = 1
        else:
            Ffarx = 0

        #Defuzzification x
        FUZZYX = 0.5*Fclosex + Fmediumx +2 * Ffarx

        #PID x
        slidex = FUZZYX*(Kp*(cueBall.errorx) + Kd*(cueBall.errorx - cueBall.errorpx) + Ki*(cueBall.errxsum))

        #Control limits x
        if slidex > 0.5:
            slidex = 0.5
        if slidex < -0.5:
            slidex = -0.5

        #Fuzzyfication y
        if (50 > abs(cueBall.errory) > 0):
            Fclosey = -abs(cueBall.errory) * 2 + 100
        else:
            Fclosey = 0

        if (100 > abs(cueBall.errory) > 50):
            Fmediumy = abs(cueBall.errory) * 2 - 100
        elif (150 > abs(cueBall.errory) > 100):
            Fmediumy = -abs(cueBall.errory) * 2 + 300
        else:
            Fmediumy = 0

        if (200 > abs(cueBall.errory) > 150):
            Ffary = abs(cueBall.errory) * 2 - 300
        elif (abs(cueBall.errory) > 200):
            Ffary = 1
        else:
            Ffary = 0

        #Defuzzification y
        FUZZYY = 0.5 * Fclosey + Fmediumy + 2 * Ffary

        #PID y
        slidey = FUZZYY*(Kp*(cueBall.errory) + Kd*(cueBall.errory - cueBall.errorpy) + Ki*(cueBall.errysum))

        #Control limits y
        if slidey > 0.5:
            slidey = 0.5
        if slidey < -0.5:
            slidey = -0.5

        #Sum of errors
        cueBall.errxsum += cueBall.errorx
        cueBall.errysum += cueBall.errory

        # Acceleration calculation
        cueBall.xF = cueBall.mass * cueBall.grav * sin(slidex)
        cueBall.yF = cueBall.mass * cueBall.grav * sin(slidey)

        #Acceleration calculation
        cueBall.xa = cueBall.xF/cueBall.mass
        cueBall.ya = cueBall.yF/cueBall.mass

        #Velocity calculation
        cueBall.xv -= cueBall.xa
        cueBall.yv -= cueBall.ya

        #Destination point calculating
        levelBallX.x = -slidex*(400/0.5)+400
        levelBallY.y = -slidey*(400/0.5)+400


    # Draws Force Stick on Pygame Window
    def drawForce(self, cuex, cuey):
        self.x = cuex
        self.y = cuey
        self.tangent = (degrees(atan2((cuex - 400), (cuey - 400))))
        pygame.draw.line(display, self.color, (400,400), (cuex, cuey), 3)



def border():
    pygame.draw.rect(display, (0, 100, 255), (0, 0, 800, 800), 3)

def close():
    pygame.quit()
    sys.exit()


# Main Function
def poolTable():
    counter = 0
    tablicapolozenie = []
    tablicaerror = []
    tablicacel = []
    tcounter = []
    loop = True


    cueBall = Ball(700, 700, 0, 0, -15, 0, 0, 0, 0, 0, 0, 0.05, 9.81, white, 0, "cue", 0, 0, 0, 0, 0, 0)
    cueStick = CueStick(0, 0, 100, stickColor)

    levelBallX = Ball(400, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0.05, 9.81,  red, 0, "cue", 0, 0, 0, 0, 0, 0)
    levelBallY = Ball(0, 400, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0.05, 9.81,  red, 0, "cue", 0, 0, 0, 0, 0, 0)

    destBall = Ball(400, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0.05, 9.81,  green, 0, "cue", 0, 0, 0, 0, 0, 0)

    while loop:

        cueBall.destinationWheel()





        forceLength = ((cueBall.x - 400) ** 2 + (cueBall.y - 400) ** 2) ** 0.5
        gravityStick = CueStick(0, 20, forceLength, gravityColor)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                close()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_q:
                    close()

                if event.key == pygame.K_r:
                    poolTable()

            if event.type == pygame.MOUSEBUTTONDOWN:
                start = [cueBall.x, cueBall.y]
                x, y = pygame.mouse.get_pos()
                end = [x ,y]
                dist = ((start[0] - end[0])**2 + (start[1] - end[1])**2)**0.5
                force = dist/10.0
                if force > 50:
                    force = 50

                cueStick.applyForce(cueBall, force)

        display.fill(background)

        oldcueballx = cueBall.x
        oldcuebally = cueBall.y
        pygame.draw.line(trace, white, (oldcueballx, oldcuebally), (cueBall.x, cueBall.y))
        display.blit(trace, (0, 0))

        cueBall.draw(cueBall.x, cueBall.y)
        destBall.draw(cueBall.destX, cueBall.destY)
        levelBallX.draw(levelBallX.x, levelBallX.y)
        levelBallY.draw(levelBallY.x, levelBallY.y)

        cueBall.move()



        if not (cueBall.speed < 0):
            cueStick.draw(cueBall.x, cueBall.y)

        gravityStick.drawForce(cueBall.x, cueBall.y)

        #print(gravityStick.length)

        gravityStick.applyGrav(cueBall, levelBallX, levelBallY, destBall, gravityStick.length, cueBall.x, cueBall.y)

        for i in range(len(balls)):
            balls[i].draw(balls[i].x, balls[i].y)

        for i in range(len(balls)):
           balls[i].move()

        border()  #obramowanie (na razie zostawic)


        counter += 1
        tcounter.append(counter)
        tablicapolozenie.append(cueBall.x)
        tablicaerror.append(cueBall.errorx)
        tablicacel.append(cueBall.destX)


        if counter > 500:

            plt.plot(tablicapolozenie)
            plt.plot(tablicaerror)
            plt.plot(tablicacel)

            plt.show()
            close()

        pygame.display.update()
        clock.tick(60)

poolTable()