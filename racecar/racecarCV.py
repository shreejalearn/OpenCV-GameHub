import random
import pygame as py
from pygame.locals import *
import subprocess
import cv2
from cvzone.HandTrackingModule import HandDetector

import numpy as np
import pyautogui as pt

cap = cv2.VideoCapture(0)
cam_w, cam_h = 680, 480
cap.set(3, cam_w)
cap.set(4, cam_h)
frameR = 100

detector = HandDetector(maxHands=1, detectionCon=0.65)

clock = py.time.Clock()

sh = 700
sw = 550
run = False

path = (100, 0, 300, sh)  # road

win = (sw, sh)

py.init()
py.display.set_caption('Zoom Zoom')
display = py.display.set_mode(win)

othercars = [py.image.load(f'images/{f}') for f in ['car2.png', 'car3.png', 'car4.png', 'car5.png']]
death = py.image.load('images/dead.png')

coin_image = py.image.load('images/coin.png')

scroll_lane = 0  # scrolling bg
sprite_init = py.sprite.Sprite

class Setup(sprite_init):
    def __init__(self, image, x, y):
        self.image = py.transform.smoothscale(image, (70, 70))
        self.rect = self.image.get_rect(center=(x, y))
        super().__init__()

class Coin(Setup):
    def __init__(self, x, y):
        super().__init__(coin_image, x, y)

score = 0
money = 0
starty = 650
startx = 250

class PlayerVehicle(Setup):
    def __init__(self, x, y):
        pic = py.image.load('images/car1.png')
        super().__init__(pic, x, y)

player = PlayerVehicle(startx, starty)
players = py.sprite.Group()
players.add(player)

lane_coordinates = [150, 250, 350]

dividerh = 40  # white lines of lane
dividerw = 9  # white lines of lane

edge_r = (395, 0, dividerh, sh)  # right edge
edge_l = (95, 0, dividerw, sh)  # left edge

speed = 10

running = True
enemy = py.sprite.Group()
coins = py.sprite.Group()
global pause
pause = False
showdeath = death.get_rect()

def paused():
    global pause, run
    while pause:
        for event in py.event.get():
            if event.type == py.QUIT:
                py.quit()
                quit()
            elif event.type == py.KEYDOWN:
                if event.key == py.K_p:
                    pause = False
                    return  # Exit the paused function
                if event.key == py.K_q:
                    save_money_and_quit()
                if event.key == py.K_r:
                    save_money_and_quit()

        display.fill(("#AA4A44"))  # grass

        # edges
        py.draw.rect(display, ("#ffa500"), edge_r)
        py.draw.rect(display, ("#ffa500"), edge_l)

        py.draw.rect(display, (100, 100, 100), path)  # road
        for y in range(-dividerh * 2, sh, dividerh * 2):
            for x in (lane_coordinates[0] + 45, lane_coordinates[1] + 45):
                py.draw.rect(display, (255, 255, 255), (x, y + scroll_lane, dividerw, dividerh))
        players.draw(display)
        enemy.draw(display)
        coins.draw(display)
        display.blit(show, div)
        display.blit(show3, div3)
        display.blit(show_coins, (10, 150))
        py.display.update()
        clock.tick(15)

def save_money_and_quit():
    with open("money.txt") as f:
        contents = f.readlines()
    m = ""
    for thing in contents:
        m += thing
    m = int(m)
    m += money

    with open('money.txt', 'w') as h:
        h.write(str(m))
    py.quit()
    quit()

while running:
    ret, frame = cap.read()
    frame = cv2.flip(frame, 1)
    hands, frame = detector.findHands(frame)

    cv2.rectangle(frame, (frameR, frameR), (cam_w - frameR, cam_h - frameR), (255, 0, 255), 2)

    if hands:
        hand1 = hands[0]
        fingers = detector.fingersUp(hand1)
        if fingers[4] == 1:  # If thumb is closed (gesture for left hand)
            # Move the player's vehicle to the left
            if player.rect.center[0] > lane_coordinates[0]:
                player.rect.x -= 100
        elif fingers[4] == 0:  # If thumb is open (gesture for right hand)
            # Move the player's vehicle to the right
            if player.rect.center[0] < lane_coordinates[2]:
                player.rect.x += 100
        elif sum(fingers[1:]) == 0:  # If all fingers except thumb are closed (gesture for middle lane)
            # Move the player's vehicle to the middle lane
            player.rect.center = (lane_coordinates[1], player.rect.centery)

    cv2.imshow('frame', frame)
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

    # Update Pygame display
    py.display.update()

    if not pause:
        display.fill(("#AA4A44"))  # grass

        # edges
        py.draw.rect(display, ("#ffa500"), edge_r)
        py.draw.rect(display, ("#ffa500"), edge_l)

        py.draw.rect(display, (100, 100, 100), path)  # road

        clock.tick(120)

        for i in py.event.get():
            if i.type == KEYDOWN:

                if i.key == K_RIGHT:
                    if player.rect.center[0] < lane_coordinates[2]:
                        player.rect.x += 100

                if i.key == K_LEFT:
                    if player.rect.center[0] > lane_coordinates[0]:
                        player.rect.x -= 100
                if i.key == py.K_p:
                    pause = True
                    paused()
                if i.key == py.K_q:
                    save_money_and_quit()
                if i.key == py.K_r:
                    save_money_and_quit()

                for car in enemy:  # collision after lane switch
                    if py.sprite.collide_rect(player, car):
                        run = True

                        if i.key == K_RIGHT:
                            player.rect.right = car.rect.left
                            showdeath.center = [
                                player.rect.right,
                                (player.rect.center[1] + car.rect.center[1]) / 2
                            ]

                        if i.key == K_LEFT:
                            player.rect.left = car.rect.right
                            showdeath.center = [
                                player.rect.left,
                                (player.rect.center[1] + car.rect.center[1]) / 2
                            ]
                    for coin in coins:
                        if py.sprite.collide_rect(car, coin):
                            coin.kill()

            if i.type == QUIT:
                running = False

        if scroll_lane >= dividerh * 2:
            scroll_lane = 0

        for y in range(-dividerh * 2, sh, dividerh * 2):
            for x in (lane_coordinates[0] + 45, lane_coordinates[1] + 45):
                py.draw.rect(display, (255, 255, 255), (x, y + scroll_lane, dividerw, dividerh))
        for coin in coins:
            if py.sprite.collide_rect(player, coin):
                money += random.randint(1, 3)
                coin.kill()
        scroll_lane = scroll_lane + speed * 2

        f1 = py.font.Font("images/Neucha-Regular.ttf", 24)
        show = f1.render('Score: ' + str(score), True, (255, 255, 255))
        show3 = f1.render(('q=quit'), True, (255, 255, 255))
        show_coins = f1.render('Money: ' + str(money), True, (255, 255, 255))

        if len(enemy) < 3:

            new = True  # enough gap between vehicles
            for z in enemy:
                if z.rect.top < z.rect.height * 1.5:
                    new = False

            if new:
                pic = random.choice(othercars)
                l = random.choice(lane_coordinates)
                car = Setup(pic, l, sh / -2)
                enemy.add(car)

        if len(coins) < 1:
            new = True  # enough gap between coins
            for z in coins:
                if z.rect.top < z.rect.height * 2.5:
                    new = False
            if new:
                l = random.choice(lane_coordinates)
                coin = Coin(l, sh / -2)
                coins.add(coin)

        players.draw(display)
        enemy.draw(display)
        coins.draw(display)

        for t in enemy:
            t.rect.y = t.rect.y + speed

            if t.rect.top >= sh:
                t.kill()

                score += 1

                if score % 8 == 0:
                    speed += 0.5
        for coin in coins:
            coin.rect.y = coin.rect.y + speed
            if coin.rect.top >= sh:
                coin.kill()

        div = show.get_rect()
        div.center = (44, 100)
        div3 = show3.get_rect()
        div3.center = (44,200)

        if py.sprite.spritecollide(player, enemy, True):
            run = True
            showdeath.center = [player.rect.centerx, player.rect.top]

        if run:
            with open("highscores.txt") as z:
                c = z.readlines()
            for g in c:
                x = c.index(g)
                c[x] = g.strip()
            x = (c[7])
            if int(x) < score:
                c[7] = str(score)
            with open('highscores.txt', 'w') as y:
                for t in c:
                    y.write(str(t) + "\n")
            save_money_and_quit()

        for car in enemy:  # collision after lane switch
            if py.sprite.collide_rect(player, car):
                run = True

                if i.key == K_RIGHT:
                    player.rect.right = car.rect.left
                    showdeath.center = [
                        player.rect.right,
                        (player.rect.center[1] + car.rect.center[1]) / 2
                    ]

                if i.key == K_LEFT:
                    player.rect.left = car.rect.right
                    showdeath.center = [
                        player.rect.left,
                        (player.rect.center[1] + car.rect.center[1]) / 2
                    ]
            for coin in coins:
                if py.sprite.collide_rect(car, coin):
                    coin.kill()

        display.blit(show, div)
        display.blit(show3, div3)
        display.blit(show_coins, (10, 150))

        py.display.update()

with open("money.txt") as f:
    contents = f.readlines()
m = ""
for thing in contents:
    m += thing
m = int(m)
m += money

with open('money.txt', 'w') as h:
    h.write(str(m))
py.quit()
