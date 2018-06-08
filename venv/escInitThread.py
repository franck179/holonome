import threading, time
class escInitThread (threading.Thread):
        def __init__(self,robot,slot,lock):
            threading.Thread.__init__(self)
            self.slot = slot
            self.robot = robot
            self.lock = lock
        def run (self):
            if self.slot > 1 : self.slot = self.slot +12
            else : self.slot=self.slot
            self.lock.acquire(1)
            print("initialisation ESC slot n° ", self.slot)
            self.robot.shield.set_pwm(self.slot,0,307) #307 est le signal neutre sous 50 Hz (1.5 / 20 x 4096 = 307)
            time.sleep(0.5)
            self.lock.release()
            time.sleep(0.5)