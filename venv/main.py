# -*- coding: utf-8 -*-
from Robot import *

continu = True
wr = Robot(4)
#wr.set_moteurs()
wr.initialiser_esc()
wr.set_joysticks()

while continu:
    for event in pygame.event.get():
        if event.type == pygame.JOYBUTTONDOWN and event.button == 10: #bouton select
            continu = False
            wr.fin_esc()
            break #sortie du programme
        if event.type == pygame.JOYAXISMOTION :
            if event.axis == 5: #gachette gauche
                wr.setAcc()
            if event.axis == 2 or event.axis == 3 : #joystick droit
                wr.deplacement_std()
            else : #joystick gauche
                wr.deplacement_slide()
        pygame.event.clear() #vide la queue - annule plusieurs appuis sur joystick