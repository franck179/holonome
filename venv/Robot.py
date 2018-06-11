import Adafruit_PCA9685, time, pygame,math
import numpy as np
from escInitThread import *
import threading
def scale(x, in_min, in_max, out_min, out_max):
    """
    Equivalent de la fonction map() en arduino
    :param x: valeur à mapper
    :param in_min: borne inférieure d'entrée
    :param in_max: borne supérieure d'entrée
    :param out_min: borne inférieure de sortie
    :param out_max: borne supérieure de sortie
    :return:
    """
    return (x-in_min) * (out_max-out_min) / (in_max-in_min) + out_min

class Robot:
    """
        Classe permettant de controler un robot basé sur une carte
        raspberry munie d'un shield servo-moteurs d'Adafruit PCA9685
        sur lequel sont connectés plusieurs esc reliés à des moteurs DC
        Le robot peut être controlé à l'aide d'une (ou plusieurs) manettes
        USB branchées sur la raspberry.
        Les moteurs de roues sont réputés être branchés comme suit :

        AVG = slot 0
        AVD = slot 1
        ARG = slot 14
        ARD = slot 15


    """
    #~ sD = np.array([[1, -1],[-1, 1]])
    #~ sARD = np.array([[0, -1],[-1, 0]])
    #~ sARG = np.array([[-1, 0],[0, -1]])
    #~ sG = np.array([[-1, 1],[1, -1]])
    #~ sAVG = np.array([[0, 1],[1, 0]])
    #~ sAVD = np.array([[1, 0],[0, 1]])
    sG = np.array([[1, -1],[-1, 1]])
    sARG = np.array([[0, -1],[-1, 0]])
    sARD = np.array([[-1, 0],[0, -1]])
    sD = np.array([[-1, 1],[1, -1]])
    sAVD = np.array([[0, 1],[1, 0]])
    sAVG = np.array([[1, 0],[0, 1]])
    rG = np.array([[1, -1],[1, -1]])
    rD = np.array([[1, -1],[1, -1]])
    seuil_y_std = 0.20
    seuil_y_slide = 0.20
    vitesseMin = 25





    def __init__(self,slotsServos = []):
        self.shield = Adafruit_PCA9685.PCA9685()
        self.nbServos = len(slotsServos)
        self.slotsServos = slotsServos #utilité à vérifier !
        self.joysticks = []
        self.esc = []
        self.acc = vitesseMin
        baton = threading.Lock()
        for s in self.slotsServos:
            th = escInitThread(self,s,baton)
            self.esc.append(th)

    def initialiser_esc(self):
        self.shield.set_pwm_freq(50)
        for i in range(self.nbServos):
            self.esc[i].start()
        for i in range(self.nbServos):
            self.esc[i].join()
        print("Initialisation terminée")

    def fin_esc(self):
        for s in self.slotsServos:
            self.shield.set_pwm(s,0,4096)
            print("esc sur port {} éteint".format(s))

    def calculVitesse(self, v):
        return int(scale(v,-100,100,205,410))

    def minimax(self,a,mini,maxi):
        if a <= mini : return mini
        elif a >= maxi : return maxi
        else : return a
    
    def config_Joystick(self,nom):
        if nom == "REV":
            self.stickGauche = (0,1)
            self.stickDroit = (2,3)
            self.gachetteGauche = 5
            self.gachetteDroite =
            self.croixDir =
            self.boutonGauche =
            self.boutonDroit =
            self.select =10
            return 0
        if nom == "PS4":
            self.stickGauche = (0,1)
            self.stickDroit = (2,5)
            self.gachetteGauche = 3
            self.gachetteDroite = 4
            self.croixDir = 0
            self.boutonGauche = 4
            self.boutonDroit = 6
            self.select = 12 # à tester
            return 1
    
    def set_joysticks(self,nom):
        #initialiser tous les modules de pygame
            pygame.init()
            #on peut les initialiser séparémént
            #pygame.joystick.init()

            #On compte les joysticks
            nb_joysticks = pygame.joystick.get_count()

            #Et on en crée un s'il y a en au moins un
            if nb_joysticks > 0:
                for i in range(nb_joysticks):
                    self.joysticks.append(pygame.joystick.Joystick(i))
                    self.joysticks[i].init()
                    print("Le joystick n°{0} est connecté".format(i+1))
                self.manette = self.joystick(self.config_Joystick(nom))
            else:
                print("Aucun joystick connecté")

    def _signe(self,num):
        if num >= 0 : return 1
        else : return -1

    def set_vitesses_moteurs(self,tableau):
        for i in range(2):
            for j in range(2):
                self.shield.set_pwm(14*i+j,0,tableau[i,j])

    def setAcc(self):
        #val = self.joysticks[0].get_axis(5)
        val = self.manette.get_axis(self.gachetteGauche)
        if val == -1 :
            self.acc = vitesseMin
        else :
            self.acc = 100*val

    def deplacement_std(self):
        # x = self.joysticks[0].get_axis(2)
        # y = -self.joysticks[0].get_axis(3)
        x = self.manette.get_axis(self.stickDroit[0])
        y = -self.manette.get_axis(self.stickDroit[1])
        print("x={0} et y={1}".format(x,y))
        if x == 0 : alpha = math.pi/2
        elif x < 0 :  alpha=math.atan(y/x) + math.pi
        else : alpha=math.atan(y/x)
        unscaledV = math.sqrt(x**2*math.cos(alpha)**2+y**2*math.sin(alpha)**2)
        print("unscaledV :",unscaledV)

        if (y > - self.seuil_y_std) and (y < self.seuil_y_std) : #rotation sans avancer
            tabV = self.acc*self._signe(x)*self.rD
            tabV = [list(map(self.calculVitesse,tabV[0])),list(map(self.calculVitesse,tabV[1]))]
            tabV = np.array(tabV)
            self.set_vitesses_moteurs(tabV)
            print("tab =",tabV)
        else : # rotation en avançant ou reculant
            vg = self.calculVitesse(self.acc * math.cos(alpha))
            vd = self.calculVitesse(self.acc * math.sin(alpha))
            print("vg = {0} et vd={1}".format(vg,vd))
            self.set_vitesses_moteurs(np.array([[vg,vd],[vg,vd]]))

    def deplacement_slide(self) :
        # x = self.joysticks[0].get_axis(0)
        # y = -self.joysticks[0].get_axis(1)
        x = self.manette.get_axis(self.stickGauche[0])
        y = -self.manette.get_axis(self.stickGauche[1])
        if x == 0:
            alpha = math.pi / 2
        else:
            alpha = math.atan(y / x)

        if (y > -self.seuil_y_slide) and (y < self.seuil_y_slide) : #glissement sans avancer
            if x > 0 :
                tab = self.sD
            else :
                tab = self.sG
        elif y >= self.seuil_y_slide :
            if x > 0 :
                tab = self.sAVD
            else :
                tab = self.sAVG
        else :
            if x > 0 :
                tab = self.sARD
            else :
                tab = self.sARG

        print("tab=",tab)
        tabV = self.acc*tab
        tabV = [list(map(self.calculVitesse,tabV[0])),list(map(self.calculVitesse,tabV[1]))]
        tabV = np.array(tabV)
        print("tabV=",tabV)
        self.set_vitesses_moteurs(tabV)
        
    def arret(self):
        self.set_vitesses_moteurs([[307,307],[307,307]])



