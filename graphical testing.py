import pygame
import sys
from pygame.locals import QUIT
import math


def get_point_from_angle(center, distance, degrees):
    # Convert degrees to radians
    radians = math.radians(degrees)

    # Calculate the coordinates of the point
    x = center[0] + distance * math.cos(radians)
    y = center[1] - distance * math.sin(radians)  # Subtract instead of adding

    return x, y


base_pos = [0, 0]
target_pos = [100, 50]

arm_1_len = 60
arm_2_len = 60

pygame.init()
DISPLAYSURF = pygame.display.set_mode((400, 300))
pygame.display.set_caption('Robotic Arm Sim')

base_pos[0] = (DISPLAYSURF.get_width() / 2) + base_pos[0]
base_pos[1] = (DISPLAYSURF.get_height() / 2) - base_pos[1]

target_pos[0] = (DISPLAYSURF.get_width() / 2) + target_pos[0]
target_pos[1] = (DISPLAYSURF.get_height() / 2) - target_pos[1]

while True:
    try:
        for event in pygame.event.get():
            if event.type == QUIT:
                pygame.quit()
                sys.exit()
        DISPLAYSURF.fill("#676569")
        target_pos = pygame.mouse.get_pos()

        pygame.draw.circle(DISPLAYSURF, "#5226ff", base_pos, 5)
        pygame.draw.circle(DISPLAYSURF, "#ff2931", target_pos, 5)

        pygame.draw.line(DISPLAYSURF, "#e300ff", base_pos, target_pos, 3)

        distance = math.sqrt((base_pos[0] - target_pos[0]) ** 2 + (base_pos[1] - target_pos[1]) ** 2)

        # Calculate the angle using atan2
        s1 = math.acos((arm_2_len ** 2 + distance ** 2 - arm_1_len ** 2) / (2 * arm_2_len * distance))
        # print(math.degrees(s))
        s = s1 + abs(math.atan((abs(target_pos[1]) - abs(base_pos[1])) / (abs(target_pos[0]) - abs(base_pos[0]))))

        if target_pos[0] < base_pos[0] and target_pos[1] <= base_pos[1]:
            s = math.pi - s
        elif target_pos[0] < base_pos[0] and target_pos[1] > base_pos[1]:
            s = (math.pi + s) - (2 * s1)
        elif target_pos[0] >= base_pos[0] and target_pos[1] > base_pos[1]:
            s = ((2 * math.pi) - s) + (2 * s1)

        # print(f"Sholder angle: {math.degrees(s)}")
        font = pygame.font.Font('freesansbold.ttf', 12)
        text = font.render(f"Sholder angle: {round(math.degrees(s), 2)}", True, "#74c23d")
        textRect = text.get_rect()
        textRect.topleft = (10, 10)
        DISPLAYSURF.blit(text, textRect)

        e = math.acos((arm_1_len ** 2 + arm_2_len ** 2 - distance ** 2) / (2 * arm_1_len * arm_2_len))

        # print(f"Elbow angle: {math.degrees(e)}")
        font = pygame.font.Font('freesansbold.ttf', 12)
        text = font.render(f"Elbow angle: {round(math.degrees(e), 2)}", True, "#74c23d")
        textRect = text.get_rect()
        textRect.topleft = (10, 40)
        DISPLAYSURF.blit(text, textRect)

        point = get_point_from_angle(base_pos, arm_1_len, math.degrees(s))

        pygame.draw.line(DISPLAYSURF, "#6dff00", base_pos, point, 2)
        pygame.draw.line(DISPLAYSURF, "#6dff00", point, target_pos, 2)
        pygame.draw.circle(DISPLAYSURF, "#ff00ce", point, 4)

        pygame.display.update()
    except:
        # print("out of range")
        i = 1
