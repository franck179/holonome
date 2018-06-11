# -*- coding: utf-8 -*-
from Robot import *

typeManette = "PS4"

continu = True
wr = Robot(4)
wr.initialiser_esc()
wr.set_joysticks(typeManette)

while continu:
    repos = (wr.manette.get_axis(wr.gachetteGauche) == -1 or wr.manette.get_axis(wr.gachetteGauche) == 0) \
    and wr.manette.get_axis(wr.stickGauche[0]) == 0 and wr.manette.get_axis(wr.stickGauche[1]) == 0 \
            and wr.manette.get_axis(wr.stickDroit[0]) == 0 and wr.manette.get_axis(wr.stickDroit[1]) == 0
    for event in pygame.event.get():
        repos = (wr.manette.get_axis(wr.gachetteGauche) == -1 or wr.manette.get_axis(wr.gachetteGauche) == 0) \
                and wr.manette.get_axis(wr.stickGauche[0]) == 0 and wr.manette.get_axis(wr.stickGauche[1]) == 0 \
                and wr.manette.get_axis(wr.stickDroit[0]) == 0 and wr.manette.get_axis(wr.stickDroit[1]) == 0
        if event.type == pygame.JOYBUTTONDOWN and event.button == wr.manette.select: #bouton select
            continu = False
            wr.fin_esc()
            break #sortie du programme
        if event.type == pygame.JOYAXISMOTION :
            if repos :
                wr.arret()
            else :
                if event.axis == wr.manette.gachetteGauche: #gachette gauche
                    wr.setAcc()
                elif event.axis in wr.manette.stickDroit : #stick droit
                    wr.deplacement_std()
                elif event.axis in wr.manette.stickGauche : #stick gauche
                    wr.deplacement_slide()
        // pygame.event.clear() #vide la queue - annule plusieurs appuis sur joystick