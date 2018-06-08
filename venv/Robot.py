import Adafruit_PCA9685, time, pygame,math, gestionVitesse
import numpy as np
from escInitThread import *
import threading
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
    seuil_y_std = 0.30
    seuil_y_slide = 0.30





    def __init__(self,slotsServos = []):
        self.shield = Adafruit_PCA9685.PCA9685()
        self.nbServos = len(slotsServos)
        self.slotsServos = slotsServos #utilité à vérifier !
        self.joysticks = []
        self.esc = []
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

    def minimax(self,a,mini,maxi):
        if a <= mini : return mini
        elif a >= maxi : return maxi
        else : return a



    #def set_moteurs(self):
            #for i in range(self.nbServos) :
                #self.initialiser_esc(i)
                #print("ESC n°{0}/{1} initialisé".format(i,self.nbServos))

    def set_joysticks(self):
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
            else:
                print("Aucun joystick connecté")

    def _signe(self,num):
        if num >= 0 : return 1
        else : return -1

    def set_vitesses_moteurs(self,tableau):
        for i in range(2):
            for j in range(2):
                self.shield.set_pwm(14*i+j,0,tableau[i,j])


    def deplacement_std(self):
        x = self.joysticks[0].get_axis(2)
        y = -self.joysticks[0].get_axis(3)
        print("x={0} et y={1}".format(x,y))
        if x == 0 : alpha = math.pi/2
        else : alpha=math.atan(y/x)
        unscaledV = math.sqrt(x**2*math.cos(alpha)**2+y**2*math.sin(alpha)**2)
        print("unscaledV :",unscaledV)
        #v = gestionVitesse.esc(unscaledV)
        #print("v =",v)

        if (y > - self.seuil_y_std) and (y < self.seuil_y_std) : #rotation sans avancer
            #self.set_vitesses_moteurs(self._signe(x)*v*self.rD)
            tabV = unscaledV*self._signe(x)*self.rD
            tabV = [list(map(gestionVitesse.esc,tabV[0])),list(map(gestionVitesse.esc,tabV[1]))]
            tabV = np.array(tabV)
            self.set_vitesses_moteurs(tabV)
            print("tab =",tabV)
        else : # rotation en avançant ou reculant
            #vg = gestionVitesse.esc((unscaledV+x/2)*self._signe(y))
            #vd = gestionVitesse.esc((unscaledV-x/2)*self._signe(y))
            vg = gestionVitesse.esc(self.minimax((unscaledV+x/2),0,1)*self._signe(y))
            vd = gestionVitesse.esc(self.minimax((unscaledV-x/2),0,1)*self._signe(y))
            # vg = gestionVitesse.esc(max(1,1.5*x)*self._signe(y))
            # vd = gestionVitesse.esc(max(-1,x/2)*self._signe(y))
            print("vg = {0} et vd={1}".format(vg,vd))
            self.set_vitesses_moteurs(np.array([[vg,vd],[vg,vd]]))

    def deplacement_slide(self) :
        x = self.joysticks[0].get_axis(0)
        y = -self.joysticks[0].get_axis(1)
        if x == 0:
            alpha = math.pi / 2
        else:
            alpha = math.atan(y / x)
        unscaledV = math.sqrt(x ** 2 * math.cos(alpha) ** 2 + y ** 2 * math.sin(alpha) ** 2)
        #unscaledV = math.sqrt(x**2+y**2)
        #v = gestionVitesse.esc(unscaledV)

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
        tabV = unscaledV*tab
        tabV = [list(map(gestionVitesse.esc,tabV[0])),list(map(gestionVitesse.esc,tabV[1]))]
        tabV = np.array(tabV)
        print("tabV=",tabV)
        self.set_vitesses_moteurs(tabV)



