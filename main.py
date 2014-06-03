#The basic idea is from Fogleman's Minecraft clone
#(https://github.com/fogleman/Minecraft)
# The OpenGl configuration comes from his project
# But I think they should be liks this
import socket
from thread import *
from pyglet.gl import * 
from pyglet.window import key 
import math
import random
import time
import copy
import sys

DISTANCE=3
TOWERINFO={}

def thirdVersion(position,rotation = (0, 0)):#100%me
    x,y,z=position
    Rx,Ry=rotation
    x3v=x+DISTANCE*math.sin(math.radians(Rx))
    z3v=z-DISTANCE*math.cos(math.radians(Rx))
    y3v=y+DISTANCE*math.sin(math.radians(Ry))
    return (x3v,y3v,z3v)

def rotateBird(coordinates,rotation,position,elevation):#100%me
    result=[]
    if elevation>0:coordinates=elevateBird(coordinates,position,elevation)
    Rx,Ry=rotation
    Rx=-math.radians(Rx)
    x,y,z=position
    for i in xrange(len(coordinates)):
        if i%3==0:
            tempX,tempZ=coordinates[i]-x,coordinates[i+2]-z
            result.append(tempX*math.cos(Rx)+tempZ*math.sin(Rx)+x)
        elif i%3==1:
            tempX,tempY,tempZ=coordinates[i-1]-x,coordinates[i]-y,\
            coordinates[i+1]-z            
            result.append(coordinates[i])
        else:
            tempX,tempZ=coordinates[i-2]-x,coordinates[i]-z
            result.append((-tempX)*math.sin(Rx)+tempZ*math.cos(Rx)+z)
    return result

def elevateBird(coordinates,position,elevation):
    x,y,z=position
    if elevation>0:
        Ry=math.radians(30)
        result=[]
        for i in xrange(len(coordinates)):
            if i%3==0:
                tempX,tempY,tempZ=coordinates[i]-x,coordinates[i+1]-y,\
                coordinates[i+2]-z     
                result.append(tempX+x)
            elif i%3==1:
                tempX,tempY,tempZ=coordinates[i-1]-x,coordinates[i]-y,\
                coordinates[i+1]-z            
                result.append(tempY*math.cos(Ry)+tempZ*(-math.sin(Ry))+y)
            else:
                tempX,tempY,tempZ=coordinates[i-2]-x,coordinates[i-1]-y,\
                coordinates[i]-z            
                result.append(tempY*math.sin(Ry)+tempZ*math.cos(Ry)+z)
    return result
# The upper 3 functions is to use matrix to convert 1st person version to
# 3rd person version

def cube_vertices(x, y, z, n):
    return [
        x-n,y+n,z+n, x+n,y+n,z+n, x+n,y+n,z-n, x-n,y+n,z-n,  # top
        x-n,y-n,z-n, x+n,y-n,z-n, x+n,y-n,z+n, x-n,y-n,z+n,  # bottom
        x-n,y-n,z-n, x-n,y-n,z+n, x-n,y+n,z+n, x-n,y+n,z-n, # left
        x+n,y-n,z+n, x+n,y-n,z-n, x+n,y+n,z-n, x+n,y+n,z+n, # right
        x-n,y-n,z+n, x+n,y-n,z+n, x+n,y+n,z+n, x-n,y+n,z+n, # front
        x+n,y-n,z-n, x-n,y-n,z-n, x-n,y+n,z-n, x+n,y+n,z-n, # back
    ]
# Fogleman's method to make a block, i just modify the top one

class TextureGroup(pyglet.graphics.Group): 
    def __init__(self, path):
        super(TextureGroup, self).__init__()
        self.texture = pyglet.image.load(path).get_texture()
    def set_state(self):
        glEnable(self.texture.target)
        glBindTexture(self.texture.target, self.texture.id)
    def unset_state(self):
        glDisable(self.texture.target)
# Fogleman's method to store image in menory

class environment(object):
    def __init__(self):#80%me
        self.batch = pyglet.graphics.Batch()
        self.grass = TextureGroup('resource\\grass.jpg') 
        self.birdData=[]
        self.box=TextureGroup('resource\\box.jpg')
        self.towerGroup={}
        self.soil=TextureGroup('resource\\soil.jpg')
        self.initialize() 
#to establish rhe environment, including the ground and towers

    def initialize(self,detail=None):
        n = 100 #size of the total map
        for x in xrange(-n, n + 1):
            for z in xrange(-n, n + 1):
                position=(x,0,z)
                self.makeGroud(position)
        if detail==None:
            for row in xrange(7):
                for col in xrange(7):
                    centerX,centerZ,heightY=-35+row*9+8,-35+col*9+8,\
                    random.randint(5,20)
                    self.towerGroup[(centerX,centerZ)]=heightY
                    number,data=self.makeTowers((centerX,heightY,centerZ))
                    self.batch.add(number, GL_QUADS, self.box,('v3f/static', \
                    data),('t2f/static', [0,0,0,1,1,1,1,0]*(number/4)))
            global TOWERINFO
            TOWERINFO=self.towerGroup
        else:
            for tower in detail:
                centerX,centerZ=tower
                heightY=detail[tower]
                number,data=self.makeTowers((centerX,heightY,centerZ))
                self.batch.add(number, GL_QUADS, self.box,('v3f/static',data),\
                               ('t2f/static', [0,0,0,1,1,1,1,0]*(number/4)))

    def makeTowers(self,position):#100%me
        x,y,z=position
        dataNumber=48*y+36
        data=[]
        for floor in xrange(y):
            basicData=[x-1.5,floor-0.5,z-1.5, x-1.5,floor+0.5,z-1.5, \
                       x-0.5,floor+0.5,z-1.5, x-0.5,floor-0.5,z-1.5,
                   x-0.5,floor-0.5,z-1.5, x-0.5,floor+0.5,z-1.5,\
                   x+0.5,floor+0.5,z-1.5, x+0.5,floor-0.5,z-1.5,
                   x+0.5,floor-0.5,z-1.5, x+0.5,floor+0.5,z-1.5, \
                   x+1.5,floor+0.5,z-1.5, x+1.5,floor-0.5,z-1.5]
            otherData=self.rotateTower(basicData,position,108)
            #use Recursion and 2D matrix to calculate the other coordinates
            data=data+basicData+otherData
        for row in xrange(3):
            for col in xrange(3):
                data=data+self.makeTowerUp((x+1-row,y,z+1-col))
        return (dataNumber,data)
    
    def rotateTower(self,basicData,keyPoint,goal,result=[]):
        #find cooridinates of texture out of  the tower 
        x,y,z=keyPoint
        transformer=[]
        for i in xrange(len(basicData)):
            if i%3==0:
                transformer.append(-basicData[i+2]+x+z)
            elif i%3==1:
                transformer.append(basicData[i])
            else:
                transformer.append(basicData[i-2]-x+z)
        result=result+transformer
        if len(result)==goal:
            return result
        else:
            return self.rotateTower(transformer,keyPoint,goal,result)
        
    def makeTowerUp(self,position):
        x,y,z=position
        return [x+0.5,y-0.5,z+0.5, x+0.5,y-0.5,z-0.5,\
                x-0.5,y-0.5,z-0.5, x-0.5,y-0.5,z+0.5]
    
    def makeGroud(self,position):
        x,y,z=position
        texture=random.choice([self.grass,self.soil])
        data=[x-0.5,y-0.5,z-0.5, x-0.5,y-0.5,z+0.5,
              x+0.5,y-0.5,z+0.5, x+0.5,y-0.5,z-0.5]
        self.batch.add(4,GL_QUADS,texture,('v3f/static', data),(
            't2f/static', [0,1,1,1,1,0,0,0]))
            
class Window(pyglet.window.Window):
    def __init__(self, *args, **kwargs):
        super(Window, self).__init__(*args, **kwargs)
        self.isStart=False
        self.environment = environment()
        self.body=TextureGroup('resource\\ownBird.jpg')
        self.clientBody=TextureGroup('resource\\anotherBird.jpg')
        self.coinImage=TextureGroup('resource\\doge.png')
        self.onlineInfo=TextureGroup('resource\\3d.png')
        self.intr=TextureGroup('resource\\intr.png')
        self.tutotial=TextureGroup('resource\\tutorial.png')
        self.deathSound=pyglet.media.load('resource\\death.wav',
                                          streaming=False)
        self.coinGet=pyglet.media.load('resource\\coinGetNew.wav',
                                       streaming=False)
        self.winning=pyglet.media.load('resource\\winning.wav',
                                       streaming=False)
        self.flyfly=pyglet.media.load('resource\\flyfly.wav', streaming=False)
        self.toHigh=pyglet.media.load('resource\\toHigh.wav', streaming=False)
        self.boundSound=pyglet.media.load('resource\\bound.wav',
                                          streaming=False)
        self.pressSound=pyglet.media.load('resource\\press.wav',
                                          streaming=False)
        self.beep=pyglet.media.load("resource\\beep.wav",streaming=False)
        self.specialColor=(0, 255, 255, 255)
        self.defaultColor=(255, 255, 0, 255)
        self.ownAddr=socket.gethostbyname(socket.gethostname())
        self.lastColor=-1 # used to make the button sound beep only once
        self.isOffline=False
        self.coinShown = {}
        self.resistence=8 # when collide with map bundary
        self.beServer=self.beClient=False
        self.placeCoin()
        self.initCoinShown=copy.deepcopy(self.coinShown)
        pyglet.clock.schedule_interval(self.update, 1.0 / 70)
        self.waitingCounts=0
        self.isWaiting=False
        self.textBatch=pyglet.graphics.Batch()
        self.isInput=False
        self.askToInit=False
        self.isTutorial=False
        self.name=socket.gethostname()
        self.anotherName="TEMP"
        self.serverAddr="***.***.***.***"
        self.init()
        
    def init(self):
        self.jumpSpeed=0
        self.jumpStep=0.1
        #the 2 upper attributes are for coins, make it junm up and down
        self.set_exclusive_mouse(True)
        self.flying = True
        self.strafe = [0, 0] 
        self.position = self.anotherBirdPosition=(0, 24, 3)
        self.birdPosition=thirdVersion(self.position)
        self.pause=False
        self.isLose=self.isWin=False
        self.mouseX=self.mouseY=0
        self.rotation = (0, 0)
        self.isControl=True
        self.batch = pyglet.graphics.Batch()
        self.clock=30
        self.coinCollection=self.clientCoinCollection=0
        self.benchmark=time.clock()
        self.timeNow=self.timeUsage=0
        self.clockBegin=0
        self.needDel=None
        self.coinBatch=pyglet.graphics.Batch()
        self.dy=self.dx=self.dz= 0
        self.coinShown=copy.deepcopy(self.initCoinShown)
        
    def set_exclusive_mouse(self, exclusive):
        super(Window, self).set_exclusive_mouse(exclusive)
        self.exclusive = exclusive
        
    def get_sight_vector(self):#method of Fogleman
        x, y = self.rotation
        m = math.cos(math.radians(y)) 
        dy = math.sin(math.radians(y)) 
        dx = math.cos(math.radians(x - 90)) * m 
        dz = math.sin(math.radians(x - 90)) * m 
        return (dx, dy, dz)
    
    def get_motion_vector(self):#method of Fogleman
        if any(self.strafe) and self.isLose==False:
            if self.isStart==False:return 
            x, y = self.rotation
            strafe = math.degrees(math.atan2(*self.strafe)) 
            if self.flying==True:
                m = math.cos(math.radians(y)) 
                dy = math.sin(math.radians(y))
                if self.strafe[1]: 
                    dy = 0.0
                    m = 1
                if self.strafe[0] > 0: 
                    dy *= -1
                dx = math.cos(math.radians(x + strafe)) * m
                dz = math.sin(math.radians(x + strafe)) * m
            else:
                dy = 0.0
                dx = math.cos(math.radians(x + strafe))
                dz = math.sin(math.radians(x + strafe))
        else:
            dy = 0.0
            dx = 0.0
            dz = 0.0
        return (dx, dy, dz)
    
    def sendServer(self):
        try:
            data=str(((self.birdPosition,self.rotation,self.dy),self.isLose))
            self.connection.sendto(data,(self.serverAddr,9009))
            buf=eval(self.connection.recv(512))
            if len(buf)>0:
                self.timeNow=buf[6]
                if buf[5]==True:
                    self.init()
                else:
                    anotherBird=buf[0]
                    self.needDel=buf[1]
                    if buf[3]>self.clientCoinCollection:self.coinGet.play()
                    self.clientCoinCollection=buf[3]
                    self.coinCollection=buf[2]
                    if self.isWin==False and buf[4]==True:
                        self.isWin=True
                        self.winning.play()
                        self.set_exclusive_mouse(False)
                self.anotherBirdBody(anotherBird)
            else:
                self.connection.close()
                self.beClient=False
                self.isOffline=True
                self.init()
                self.isStart=False
                self.set_exclusive_mouse(False)
        except: pass
        
    def receiveClient(self):
        try:
            buf=eval(self.connection.recv(512))
            if len(buf)>0:
                anotherBird=buf[0]
                if self.timeNow>0.5:
                    if self.isWin==False and buf[1]==True:
                        self.isWin=True
                        self.winning.play()
                        self.set_exclusive_mouse(False)
                self.anotherBirdBody(anotherBird)
                data=str(((self.birdPosition,self.rotation,self.dy),
                    self.needDel,self.coinCollection,
                    self.clientCoinCollection, self.isLose, self.askToInit,
                    self.timeNow))
                self.connection.send(data)
                if self.askToInit:
                    self.askToInit=False
            else:
                self.connection.close()
                self.beServer=False
                self.isOffline=True
                self.init()
                self.isStart=False
                self.set_exclusive_mouse(False)
        except: pass
        
    def update(self,dt):
        if self.beClient:self.sendServer()
        elif self.beServer:self.receiveClient()        
        if self.pause==False and self.isWin==False and self.isLose==False:
            self.birdPosition=thirdVersion(self.position,self.rotation)
            self.birdBody()    
        if self.pause or self.isWin or self.isLose or self.isStart==False:
            return
        else:
            self.coinJump()
            d = 0.12
            dx, dy, dz = self.get_motion_vector()
            dx, dy, dz = dx * d, dy * d, dz * d
            self.dx-=self.resistence*dt
            self.dx=max(0,self.dx)
            self.dz-=self.resistence*dt
            self.dz=max(0,self.dz)
            if dz>0:dz-=self.dz
            elif dz<0:dz+=self.dz
            if dx>0:dx-=self.dx
            elif dz<0:dx+=self.dx  
            if not self.flying and self.pause==False:
                self.dy -= dt * 0.5 # g force
                dy += self.dy
            bx, by, bz = self.birdPosition
            tempPosition=[bx + dx, by + dy, bz + dz]
            x,y,z=self.position
            if self.collide(self.birdPosition,dx,dy,dz):
                self.position = (x+dx, max(y+dy,0), z+dz)
            
    def findToConnect(self):
        self.clientPort=random.randrange(8000,8999)
        self.connection=socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.serverPort=9009
        self.connection.bind((self.ownAddr, self.clientPort))
        self.initInfo={"map":False,"name":self.name}
        self.connection.connect((self.serverAddr,9009))
        print "connected!"
        self.connection.sendto(str(self.initInfo),(self.serverAddr,9009))
        data=eval(self.connection.recv(32768))
        self.coinShown=data[1]
        self.initCoinShown=data[1]
        self.initInfo["map"]=data[0]
        self.anotherName=data[2]
        self.isInput=False
        self.beClient=True
        self.clientCoinCollection=0
        global TOWERINFO
        TOWERINFO=self.initInfo["map"]
        self.environment.batch = pyglet.graphics.Batch()
        self.environment.initialize(TOWERINFO)
        self.environment.towerGroup=TOWERINFO
        self.isStart=True
        self.set_exclusive_mouse(True)
        
    def waitForConnect(self):
        self.needDel=None
        self.clientCoinCollection=0
        self.listener = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.serverAddr=self.ownAddr
        self.listener.bind((self.serverAddr, 9009))
        self.listener.listen(5)
        self.connection,self.address = self.listener.accept()
        self.isWaiting=False
        self.beServer=True
        buf=eval(self.connection.recv(1024))
        self.connection.send(str((TOWERINFO,self.coinShown,self.name)))
        self.isStart=True
        self.anotherName=buf["name"]
        self.timeNow=self.timeUsage=0
        self.benchmark=time.clock()
        self.set_exclusive_mouse(True)
            
    def placeCoin(self):
        for tower in TOWERINFO:
            centerX,centerZ=tower
            heightY=TOWERINFO[tower]
            coinData = cube_vertices(centerX, heightY+0.5, centerZ, 0.5)
            self.coinShown[(centerX,heightY,centerZ)]=coinData
            
    def coinJump(self):
        self.jumpSpeed+=self.jumpStep
        if self.jumpSpeed>1:self.jumpStep=-0.05
        elif self.jumpSpeed<-1:self.jumpStep=0.05
        newCoinShown={}
        for coin in self.coinShown:
            centerX,heightY,centerZ=coin
            newCoinShown[coin]=cube_vertices(centerX,
            heightY+0.5+self.jumpSpeed, centerZ, 0.5)
        self.coinShown=newCoinShown
            
    def bound(self,limit):
        if time.time()-self.clockBegin<limit:#lose control for 1.5s in too high
            self.isControl=False
        else:
            self.isControl=True
            
    def directDirection(self,one, another):
        x1,y1,z1=one
        x2,y2,z2=another
        return ((x1-x2)**2+(y1-y2)**2+(z1-z2)**2)**0.5
    
    def checkCoin(self,position,camp="server"):
        xPosition,yPosition,zPosition=position
        if self.beServer:
            needDel=None
            for key in self.coinShown:
                if self.directDirection(key,position)<=2.5:
                    if camp=="server":
                        self.coinGet.play()
                        self.coinCollection+=1
                    else:
                        self.clientCoinCollection+=1
                    needDel=key
                    break
            if needDel!=None:
                self.needDel=needDel
                del self.coinShown[needDel]
            if self.clientCoinCollection-self.coinCollection>\
            len(self.coinShown):
                self.isLose=True
                self.set_exclusive_mouse(False)
        else:
            if self.beServer==False and self.beClient==False:
                self.needDel=None
            if self.beClient==False:
                for key in self.coinShown:
                    if self.directDirection(key,position)<=2:
                        self.coinGet.play()
                        self.coinCollection+=1
                        self.needDel=key
                        break
            if self.needDel!=None and self.needDel in self.coinShown:
                del self.coinShown[self.needDel]
            if self.beClient:
                if self.coinCollection-self.clientCoinCollection>\
                len(self.coinShown):
                    self.isLose=True
                    self.set_exclusive_mouse(False)
        if self.beServer==False and self.beClient==False:
            if (self.coinCollection)==49:
                self.isWin=True
                self.set_exclusive_mouse(False)
        
    def collide(self, position,dx,dy,dz):
        xPosition,yPosition,zPosition=position
        self.checkCoin(position)
        for tower in self.environment.towerGroup:
            y=self.environment.towerGroup[tower]
            if y>yPosition:
                x,z=tower
                if self.directDirection((x,0,z),(xPosition,0,zPosition))<=2:
                    self.isLose=True
                    self.deathSound.play()
                    self.set_exclusive_mouse(False)
        if max(xPosition,zPosition)>45 or min(xPosition,zPosition)<-45:
            self.boundSound.play()
            if abs(xPosition)>45:self.dx=1.5
            if abs(zPosition)>45:self.dz=1.5
            return True
        elif yPosition>25 or self.isControl==False:
            if self.isControl==True:
                self.toHigh.play()
                self.clockBegin=time.time()
            self.bound(1)
        yGroup=self.birdData[1::3]
        if min(yGroup)<=-0.5:
            self.isLose=True
            self.deathSound.play()
            self.set_exclusive_mouse(False)
        return True
    
    def on_mouse_scroll(self, x, y, scroll_x, scroll_y):
        #adjust the distance between camera and the bird
        global DISTANCE
        verisonLimit=1.6
        if self.isStart and self.flying==False:
            DISTANCE+=scroll_y*0.1
            if DISTANCE==0.1:DISTANCE=verisonLimit
            elif  DISTANCE<verisonLimit:
                DISTANCE=0
            DISTANCE=min(DISTANCE,4)
    
    def birdBody(self):
        birdX,birdY,birdZ=self.birdPosition
        self.birdData = rotateBird(cube_vertices(birdX,birdY,birdZ, 0.5),
                                   self.rotation,self.birdPosition,self.dy)
        self.batch = pyglet.graphics.Batch()
        if self.beClient:image=self.clientBody
        else:image=self.body
        self.batch.add(24, GL_QUADS, image,('v3f/stream', self.birdData),\
                       ('t2f/stream', [1,0,0,0,0,1,1,1]*6))
        
    def anotherBirdBody(self,rawData):
        birdPosition,rotation,dy=rawData
        birdX,birdY,birdZ=birdPosition
        self.anotherBirdData=rotateBird(cube_vertices(birdX,birdY,birdZ, 0.5),
                                        rotation,birdPosition,dy)
        self.anotherBatch = pyglet.graphics.Batch()
        if self.beClient:image=self.body
        else:image=self.clientBody
        self.anotherBatch.add(24, GL_QUADS, image,('v3f/stream',
        self.anotherBirdData),('t2f/stream', [1,0,0,0,0,1,1,1]*6))
        if self.beServer:
            self.checkCoin(birdPosition,"client")
        elif self.beClient:pass
        else:self.checkCoin(birdPosition)

        
    def on_mouse_press(self, x, y, button, modifiers):
        centerX,centerY=self.width/2,self.height/2
        if self.isWin or self.isLose or self.pause:
            self.mousePauseMenu(x,y,centerX,centerY)
        elif self.isInput:
            if centerX-110<self.mouseX<centerX+110 \
            and centerY-120<self.mouseY<centerY-70:
                self.on_key_press(key.ENTER,16)
            elif centerX-120<self.mouseX<centerX+120 \
            and centerY-170<self.mouseY<centerY-120:
                self.on_key_press(key.M,16)
        elif self.isTutorial:
            if centerX-120<self.mouseX<centerX+120 \
            and centerY-170<self.mouseY<centerY-120:
                self.on_key_press(key.M,16)            
        elif self.isWaiting:
            self.mouseWaitingForClient(x, y,centerX,centerY)
        elif self.isOffline:
            if centerX-110<self.mouseX<centerX+110 \
            and centerY-120<self.mouseY<centerY-70:
                self.on_key_press(key.M,16)
            elif centerX-120<self.mouseX<centerX+120 \
            and centerY-170<self.mouseY<centerY-120:
                self.on_key_press(key.ESCAPE,16)       
        else: self.mouseMainmenu(x, y,centerX,centerY)

            
    def mouseWaitingForClient(self,x, y,centerX,centerY):
        if centerX-100<x<centerX+100 and centerY-160<y<centerY-120:
            self.on_key_press(key.ESCAPE,16)

    def mouseMainmenu(self,x, y,centerX,centerY):
        if centerX-50<x<centerX+50 and centerY-80<y<centerY-40:
            self.on_key_press(key.ENTER,16)
        elif centerX-140<self.mouseX<centerX and \
        centerY-130<self.mouseY<centerY-100:
            self.on_key_press(key.L,16)
        elif centerX<self.mouseX<centerX+140 and \
        centerY-130<self.mouseY<centerY-100:
            self.on_key_press(key.B,16)
        elif centerX-140<self.mouseX<centerX+140 and \
        centerY-170<self.mouseY<centerY-140:
            self.on_key_press(key.T,16)
        elif centerX-140<self.mouseX<centerX+140 and \
        centerY-210<self.mouseY<centerY-180:
            sys.exit()
            
    def mousePauseMenu(self,x, y,centerX,centerY):
        if centerX-100<x<centerX+100 and centerY-130<y<centerY-90 \
        and self.beClient==False:
            self.on_key_press(key.R,16)
        elif centerX-150<x<centerX+150 and centerY-180<y<centerY-140:
            self.on_key_press(key.M,16)
        elif centerX-100<x<centerX+100 and centerY-230<y<centerY-190:
            self.on_key_press(key.ESCAPE,16)
        elif centerX-100<x<centerX+100 and centerY-80<y<centerY-40:
            self.on_key_press(key.P,16)
    
                        
    def on_mouse_motion(self, x, y, dx, dy):
        if self.exclusive and self.isLose==False and self.isWin==False \
            and self.flying==False and self.isControl:
            m = 0.05
            #sensitivity ot the mouse
            x, y = self.rotation
            x, y = x + dx * m, y + dy * m
            y = max(-30, min(30, y))
            rotation = (x, y)
            if self.collide(self.position,dx,0,dy):       
                self.rotation = (x, y)
        else:
            self.mouseX,self.mouseY=x,y
            
    def on_key_press(self, symbol, modifiers):
        if self.isInput:
            self.inputServerAddress(symbol)
        elif self.isWaiting:
            if symbol==key.ESCAPE:
                sys.exit()
        elif self.isTutorial:
            if symbol==key.M:
                self.pressSound.play()
                self.isTutorial=False
        elif self.isOffline:
            if symbol==key.ESCAPE:
                sys.exit()
            elif symbol==key.M:
                self.pressSound.play()
                self.isOffline=False
        elif self.isStart==False:
            self.keyMainmenu(symbol)
        else:
            if self.isLose or self.pause or self.isWin:
                self.checkMenuForWL(symbol)
                self.benchmark=time.clock()
            else:
                if symbol==key.P:
                    if self.beClient or self.beServer:pass
                    else:
                        self.pause=True
                        self.timeUsage=self.timeNow
                        self.set_exclusive_mouse(False)
                if symbol == key.W and self.flying:
                    self.strafe[0]-=1
                    self.flying=False
                elif symbol == key.SPACE and self.isControl \
                             and self.flying==False:
                    self.flyfly.play()
                    self.dy = 0.12
                    # self.dy is to t ocontrol how to fly 

    def keyMainmenu(self,symbol):
        if symbol==key.B:
            self.isInput=True
            self.pressSound.play()
        if symbol==key.ENTER:
            self.isStart=True
            self.set_exclusive_mouse(True)
            self.benchmark=time.clock()
            self.pressSound.play()
        elif symbol==key.L:
            self.isWaiting=True
            self.pressSound.play()
            start_new_thread(self.waitForConnect,())
        elif symbol==key.T:
            self.isTutorial=True
            self.pressSound.play()
        elif symbol==key.ESCAPE:
            sys.exit()

    def inputServerAddress(self,symbol):
        if 46<symbol<58:
        #number key from 0 t to 9
            for i in xrange(15):
                if self.serverAddr[i]=="*":
                    self.serverAddr=self.serverAddr[0:i]+str(symbol-48)+\
                    self.serverAddr[i+1::]
                    break
        elif symbol==key.BACKSPACE:
            for i in xrange(15):
                if self.serverAddr[14-i]!="*" and self.serverAddr[14-i]!=".":
                    self.serverAddr=self.serverAddr[0:(14-i)]+"*"+\
                    self.serverAddr[15-i::]
                    break
        elif symbol==key.M:
            self.isInput=False
            self.pressSound.play()
        if self.serverAddr[-1]!="*" and symbol==65293:
            try:
                self.findToConnect()
                self.isStart=True
                self.set_exclusive_mouse(True)
            except:
                self.isInput=False
                self.isOffline=True
                self.connection.close()
                self.set_exclusive_mouse(False)
    
    def checkMenuForWL(self,symbol):
        if symbol ==key.P and self.isWin==False and self.isLose==False:
            self.pause=False
            self.set_exclusive_mouse(True)
            self.pressSound.play()
        elif symbol==key.R:
            self.pressSound.play()
            if self.beServer:
                self.askToInit=True
                self.init()
            elif self.beClient: pass
            else: self.init()
        elif symbol==key.ESCAPE:
            if self.beClient or self.beServer:
                self.connection.sendall(str([]))
                self.connection.close()
            sys.exit()
        elif symbol==key.M:
            self.pressSound.play()
            if self.beClient or self.beServer:
                self.connection.sendall(str([]))
                self.connection.close()
                self.beClient=self.beServer=False
            self.init()
            self.isStart=False
            self.set_exclusive_mouse(False)

    def set_2d(self):
        #OpenGL configuration 1
        width, height = self.get_size()
        glDisable(GL_DEPTH_TEST)
        glViewport(0, 0, width, height)
        glMatrixMode(GL_PROJECTION)
        glLoadIdentity()
        glOrtho(0, width, 0, height, -1, 1)
        glEnable(GL_BLEND)
        glMatrixMode(GL_MODELVIEW)
        glLoadIdentity()

    def set_3d(self):
        #OpenGL configuration 2
        width, height = self.get_size()
        glDisable(GL_BLEND)
        glEnable(GL_DEPTH_TEST)
        glViewport(0, 0, width, height)
        glMatrixMode(GL_PROJECTION)
        glLoadIdentity()
        gluPerspective(65.0, width / float(height), 0.1, 60.0)
        glMatrixMode(GL_MODELVIEW)
        glLoadIdentity()
        x, y = self.rotation
        glRotatef(x, 0, 1, 0)
        glRotatef(-y, math.cos(math.radians(x)), 0, math.sin(math.radians(x)))
        x, y, z = self.position
        glTranslatef(-x, -y, -z)
        
    def on_draw(self):
        self.clear()
        try:
            self.set_3d()
            glColor3d(1, 1, 1)
            self.environment.batch.draw()
            self.drawCoin()
            self.batch.draw()
            if self.beServer or self.beClient: self.anotherBatch.draw()
            self.set_2d()
        except:pass
        centerX,centerY=self.width/2,self.height/2
        if self.isStart==False:
            if self.isWaiting:self.drawWaitConncect(centerX,centerY)
            elif self.isInput: self.drawInput(centerX,centerY)
            elif self.isOffline: self.drawOffline(centerX,centerY)
            elif self.isTutorial:self.drawTutorial(centerX,centerY)
            else: self.drawMainMenu(centerX,centerY)
        if self.isStart:
            self.drawLocationInfo()
            self.drawClock(centerX)
            if self.flying and self.pause==False and self.isWin==False:
                self.drawIntruc(centerX,centerY)
            elif self.isLose: self.drawLose(centerX,centerY)
            elif self.isWin: self.drawWin(centerX,centerY)
            elif self.pause: self.drawPause(centerX,centerY)
        if self.beClient or self.beServer:
            self.drawCoinCollections()
            if self.isWin==False and self.isLose==False:self.drawPauseOnline()
        self.textBatch.draw()
        self.textBatch=pyglet.graphics.Batch()
    
    def drawClock(self,centerX):
        info=pyglet.text.Label('', font_name='Arial', font_size=30,x=centerX,
                            y=self.height, anchor_x='center', anchor_y='top',
        color=(0, 0, 0, 255),batch=self.textBatch)
        if self.isStart:
            if self.pause or self.isWin or self.isLose or self.beClient:pass
            else: self.timeNow=self.timeUsage+(time.clock()-self.benchmark)
        info.text="%02d:%02d"%(self.timeNow/60,self.timeNow%60)

    def drawCoin(self):
        self.coinBatch=pyglet.graphics.Batch()
        for key in self.coinShown:
            self.coinBatch.add(24, GL_QUADS, self.coinImage,('v3f/static',
                self.coinShown[key]),('t2f/static', [1,0,0,0,0,1,1,1]*6))                
        self.coinBatch.draw()
        del self.coinBatch
        
    def drawLocationInfo(self): 
        x, y, z = self.birdPosition
        xzInfo=pyglet.text.Label(" ", font_name='Arial', font_size=20,x=0,
        y=self.height, anchor_x='left', anchor_y='top',
        color=(0,0,0,255),batch=self.textBatch)
        xzInfo.text='(%.2f, %.2f) %d / %d' % ( x, z, len(self.coinShown),49)
        if y<=20:color=(0,0,0,255)
        else:
            color=(min(255,int(255*(y-20)/5)),0,0,255)
        heightInfo=pyglet.text.Label("",font_name='Arial',font_size=25,x=0,
        y=self.height-30, anchor_x='left', anchor_y='top',
        color=color,batch=self.textBatch)
        heightInfo.text="HEIGHT: %.2f"%(y)
        if self.isControl==False:
            alertInfo=pyglet.text.Label("DANGER !", font_name='Arial',
            font_size=30,x=0, y=self.height-60, anchor_x='left',
            anchor_y='top', color=(255,0,0,255),batch=self.textBatch)
        
    def drawWaitConncect(self,centerX,centerY):
        background=self.textBatch.add(4, pyglet.gl.GL_QUADS,None,('v2i',
            (centerX-350, centerY-250,centerX+350, centerY-250,centerX+350,
             centerY+250,centerX-350, centerY+250)),('c4B',
            (0,0,0,255, 0,0,0,255, 0,0,0,255, 0,0,0,255)))
        color=(255, 255, 255, 255)
        showServerIP=pyglet.text.Label(" ", font_name='Arial', bold=True,
            font_size=23,x=centerX, y=centerY+130, anchor_x='center',
            anchor_y='top', color=color,batch=self.textBatch)
        showServerIP.text="SERVER ADDRESS: "+ self.serverAddr
        showWelcome=pyglet.text.Label("WAITING FOR CONNECTION... ",
            font_name='Arial', bold=True,font_size=23,x=centerX, y=centerY+50,
            anchor_x='center', anchor_y='top', color=color,batch=self.textBatch)
        if centerX-100<self.mouseX<centerX+100 and \
            centerY-160<self.mouseY<centerY-120: color=(0, 255, 255, 255)
        else:color=(255, 255, 0, 255)
        infoBack=pyglet.text.Label('Exit (Esc)', font_name='Arial', bold=True,
            font_size=25,x=centerX, y=centerY-125, anchor_x='center',
            anchor_y='top', color=color,batch=self.textBatch)

        
    def drawInput(self,centerX,centerY):
        area=[[centerX-120,centerX+120,centerY-170,centerY-120,
               self.defaultColor],
            [centerX-110,centerX+110, centerY-120,centerY-70,
             self.defaultColor]]
        background=self.textBatch.add(4, pyglet.gl.GL_QUADS, None,('v2i',
            (centerX-350, centerY-250,centerX+350, centerY-250,centerX+350,
             centerY+250,centerX-350, centerY+250)),('c4B', (0,0,0,255,
            0,0,0,255, 0,0,0,255, 0,0,0,255)))
        color=(255, 255, 255, 255)
        showOwnIP=pyglet.text.Label(" ", font_name='Arial', bold=True,
            font_size=25,x=centerX, y=centerY+150, anchor_x='center',
            anchor_y='top', color=color,batch=self.textBatch)
        showOwnIP.text="YOUR ADDRESS: "+self.ownAddr
        showInput=pyglet.text.Label("", font_name='Arial', bold=True,
            font_size=25,x=centerX, y=centerY+100, anchor_x='center',
            anchor_y='top', color=color,batch=self.textBatch)
        showInput.text="SERVER ADDRESS: "+self.serverAddr
        for i in xrange(2):
            if area[i][0]<self.mouseX<area[i][1] and \
                area[i][2]<self.mouseY<area[i][3]:
                area[i][4]=self.specialColor
                if i+9!=self.lastColor:
                    self.lastColor=i+9
                    if self.serverAddr[-1]=="*" and i==1:pass
                    else:self.beep.play()
                break
            else:area[i][4]=self.defaultColor   
        infoBack=pyglet.text.Label('Main Menu(M)', font_name='Arial',
            bold=True,font_size=25,x=centerX, y=centerY-125, anchor_x='center',
            anchor_y='top', color=area[0][4],batch=self.textBatch)
        if self.serverAddr[-1]!="*":
            info2=pyglet.text.Label('Go!(Enter)', font_name='Arial', bold=True,
                font_size=25,x=centerX, y=centerY-75, anchor_x='center',
                anchor_y='top', color=area[1][4],batch=self.textBatch)    
        
    def drawMainMenu(self,centerX,centerY):#100%me
        area=[[centerX-140,centerX+140,centerY-90,centerY-60,
               self.defaultColor],#pressStart
            [centerX-140,centerX+140, centerY-170,centerY-140,
             self.defaultColor],#turtoial
            [centerX-140, centerX+140, centerY-210, centerY-180,
             self.defaultColor]]#exit
        background=self.textBatch.add(4, pyglet.gl.GL_QUADS,None,('v2i',
            (centerX-350, centerY-250,centerX+350, centerY-250,centerX+350,
             centerY+250,centerX-350, centerY+250)),('c4B', (70,130,180,200,
            70,130,180,200, 70,130,180,200, 70,130,180,200)))
        info=pyglet.text.Label('FLAPPY BIRD', font_name='Rosewood Std Regular',
            font_size=70,x=centerX, y=centerY+200, anchor_x='center',
            anchor_y='top', color=(255, 255, 0, 255),batch=self.textBatch)
        self.textBatch.add(4, GL_QUADS, self.onlineInfo,('v2i', (centerX,
            centerY-50,centerX+400,centerY-50,centerX+400,centerY+350,centerX,
            centerY+350,)),('t2i', [0,0,1,0,1,1,0,1]))
        for i in xrange(len(area)):
            if area[i][0]<self.mouseX<area[i][1] and \
            area[i][2]<self.mouseY<area[i][3]:
                area[i][4]=self.specialColor
                if i!=self.lastColor:
                    self.lastColor=i
                    self.beep.play()
                break
            else:area[i][4]=self.defaultColor
        pressStart=pyglet.text.Label("Single Mode (Enter)", font_name='Arial',
            bold=True,font_size=23,x=centerX, y=centerY-50, anchor_x='center',
            anchor_y='top', color=area[0][4],batch=self.textBatch)
        pressTutorial=pyglet.text.Label("Tutorial (T)", font_name='Arial',
            bold=True,font_size=23,x=centerX, y=centerY-130, anchor_x='center',
            anchor_y='top', color=area[1][4],batch=self.textBatch)
        pressExit=pyglet.text.Label("Back to Desktop (Esc)", font_name='Arial',
            bold=True,font_size=23,x=centerX, y=centerY-170, anchor_x='center',
            anchor_y='top', color=area[2][4],batch=self.textBatch)
        if centerX-200<self.mouseX<centerX+200 and \
            centerY-130<self.mouseY<centerY-100:
            self.drawChooseServerClient(self.width/2,self.height/2)
        else:
            color=(255, 255, 0, 255)
            pressLan=pyglet.text.Label("I'm not single!", font_name='Arial',
            bold=True,font_size=25,x=centerX, y=centerY-90, anchor_x='center',
            anchor_y='top', color=color,batch=self.textBatch)

    def drawChooseServerClient(self,centerX,centerY):
        area=[[centerX-200,centerX,centerY-130,centerY-100,self.defaultColor],
            #Be Server (L)
            [centerX,centerX+200, centerY-130,centerY-100,self.defaultColor]]
            #Be Client (B)
        for i in xrange(2):
            if area[i][0]<self.mouseX<area[i][1] and \
            area[i][2]<self.mouseY<area[i][3]:
                area[i][4]=self.specialColor
                if (i+3)!=self.lastColor:
                    self.lastColor=(i+3)
                    self.beep.play()
                break
            else:area[i][4]=self.defaultColor
        pressServer=pyglet.text.Label("Be Server (L)", font_name='Arial',
            bold=True,font_size=23,x=centerX-100, y=centerY-90,
            anchor_x='center', anchor_y='top',
            color=area[0][4],batch=self.textBatch)
        pressClient=pyglet.text.Label("Be Client (B)", font_name='Arial',
            bold=True,font_size=23,x=centerX+100, y=centerY-90,
            anchor_x='center', anchor_y='top',
            color=area[1][4],batch=self.textBatch)

    def drawCoinCollections(self):
        if self.beClient: ownCoinInfo,antherCoinInfo=\
            self.clientCoinCollection,self.coinCollection
        elif self.beServer: ownCoinInfo,antherCoinInfo=\
            self.coinCollection,self.clientCoinCollection
        ownCoins=pyglet.text.Label('', font_name='Arial', font_size=20,
            x=self.width, y=self.height, anchor_x='right', anchor_y='top',
        color=(0, 0, 0, 255),batch=self.textBatch)
        ownCoins.text=self.name+":   "+str(ownCoinInfo)+"   "
        anotherCoins=pyglet.text.Label('', font_name='Arial', font_size=20,
            x=self.width, y=self.height-30, anchor_x='right', anchor_y='top',
        color=(0, 0, 0, 255),batch=self.textBatch)
        anotherCoins.text=self.anotherName+":   "+str(antherCoinInfo)+"   "        

    def drawPause(self,centerX,centerY):
        background=self.textBatch.add(4, pyglet.gl.GL_QUADS,None,('v2i',
            (centerX-300, centerY-250,centerX+300, centerY-250,centerX+300,
            centerY+250,centerX-300, centerY+250)),('c4B',
            (70,130,180,150, 70,130,180,150, 70,130,180,150, 70,130,180,150)))
        info=pyglet.text.Label('PAUSE', font_name='Rosewood Std Regular',
            font_size=70, x=centerX, y=centerY+200, anchor_x='center',
            anchor_y='top', color=(255, 255, 0, 255),batch=self.textBatch)
        self.drawInfoForWL(centerX,centerY)    
        
    def drawPauseOnline(self):
        info=pyglet.text.Label('NO PAUSE ONLINE', font_name='Arial',
            font_size=20, x=self.width, y=self.height-60, anchor_x='right',
            anchor_y='top', color=(255, 255, 0, 255),batch=self.textBatch)
        info1=pyglet.text.Label('BE RESPECTFUL!', font_name='Arial',
            font_size=20, x=self.width, y=self.height-90, anchor_x='right',
            anchor_y='top', color=(255, 255, 0, 255),batch=self.textBatch)
        info1=pyglet.text.Label('SUICIDE MAKES RETRY', font_name='Arial',
            font_size=20, x=self.width, y=self.height-120, anchor_x='right',
            anchor_y='top', color=(255, 255, 0, 255),batch=self.textBatch)

    def drawLose(self,centerX,centerY):#100%me
        background=self.textBatch.add(4, pyglet.gl.GL_QUADS,None,('v2i',
            (centerX-300, centerY-250,centerX+300, centerY-250,centerX+300,
            centerY+250,centerX-300, centerY+250)),('c4B',
            (70,130,180,150, 70,130,180,150, 70,130,180,150, 70,130,180,150)))
        info=pyglet.text.Label('Game Over', font_name='Rosewood Std Regular',
            font_size=70,x=centerX, y=centerY+200, anchor_x='center',
            anchor_y='top', color=(255, 255, 0, 255),batch=self.textBatch)
        self.drawInfoForWL(centerX,centerY)

    def drawWin(self,centerX,centerY):#100%me
        background=self.textBatch.add(4, pyglet.gl.GL_QUADS,None,('v2i',
            (centerX-300, centerY-250,centerX+300, centerY-250,centerX+300,
            centerY+250,centerX-300, centerY+250)),('c4B',
            (70,130,180,150, 70,130,180,150, 70,130,180,150, 70,130,180,150)))
        info=pyglet.text.Label("", font_name='Rosewood Std Regular',
            font_size=70,x=centerX, y=centerY+200, anchor_x='center',
            anchor_y='top', color=(255, 255, 0, 255),batch=self.textBatch)
        if self.beClient or self.beServer: info.text="YOUR SCORE:"+"%d"%(
            abs(self.coinCollection-self.clientCoinCollection)/
            (math.atan(self.timeNow)*(2/math.pi))*100)
        else: info.text="YOUR SCORE:"+"%d"%(49/(math.atan(self.timeNow)
            *(2/math.pi))*100)
        self.drawInfoForWL(centerX,centerY)

    def drawInfoForWL(self,centerX,centerY):
        area=[[centerX-100,centerX+100,centerY-80,centerY-40,
               self.defaultColor],#Resume(P)
            [centerX-100, centerX+100, centerY-130, centerY-90,
             self.defaultColor],#Server Only:Retry(R)
            [centerX-150, centerX+150, centerY-180, centerY-140,
             self.defaultColor],#Main Menu(M)
            [centerX-100, centerX+100, centerY-230, centerY-190,
             self.defaultColor]]#Exit(Esc)        
        for i in xrange(len(area)):
            if area[i][0]<self.mouseX<area[i][1] and \
            area[i][2]<self.mouseY<area[i][3]:
                area[i][4]=self.specialColor
                if (i+5)!=self.lastColor:
                    self.lastColor=(i+5)
                    self.beep.play()
                break
            else:area[i][4]=self.defaultColor
        if self.pause:
            infoPause=pyglet.text.Label('Resume(P)', font_name='Arial',
                    bold=True,font_size=30,x=centerX, y=centerY-25,
                    anchor_x='center', anchor_y='top', color=area[0][4],
                    batch=self.textBatch)
        if self.beServer or self.beClient:
            info1=pyglet.text.Label('Server Only:Retry(R)', font_name='Arial',
                bold=True,font_size=30,x=centerX, y=centerY-75,
                anchor_x='center', anchor_y='top', color=area[1][4],
                batch=self.textBatch)
        else:
            info1=pyglet.text.Label('Retry(R)', font_name='Arial', bold=True,
                font_size=30,x=centerX, y=centerY-75, anchor_x='center',
                anchor_y='top',color=area[1][4],batch=self.textBatch)            
        info2=pyglet.text.Label('Main Menu(M)', font_name='Arial', bold=True,
            font_size=30,x=centerX, y=centerY-125, anchor_x='center',
            anchor_y='top', color=area[2][4],batch=self.textBatch)
        info3=pyglet.text.Label('Exit(Esc)', font_name='Arial', bold=True,
            font_size=30,x=centerX, y=centerY-175, anchor_x='center',
            anchor_y='top', color=area[3][4],batch=self.textBatch)
        
    def drawOffline(self,centerX,centerY):    
        area=[[centerX-120,centerX+120,centerY-170,centerY-120,
               self.defaultColor],
            [centerX-110,centerX+110, centerY-120,centerY-70,
             self.defaultColor]]
        for i in xrange(2):
            if area[i][0]<self.mouseX<area[i][1] and \
                area[i][2]<self.mouseY<area[i][3]:
                area[i][4]=self.specialColor
                if i+9!=self.lastColor:
                    self.lastColor=i+9
                    if self.serverAddr[-1]=="*" and i==1:pass
                    else:self.beep.play()
                break
            else:area[i][4]=self.defaultColor   
        background=self.textBatch.add(4, pyglet.gl.GL_QUADS, None,('v2i',
            (centerX-350, centerY-250,centerX+350, centerY-250,centerX+350,
             centerY+250,centerX-350, centerY+250)),('c4B', (0,0,0,255,
            0,0,0,255, 0,0,0,255, 0,0,0,255)))
        line1=pyglet.text.Label('Server not Prepared', font_name='Arial',
            bold=True, font_size=25, x=centerX, y=centerY+200,
            anchor_x='center', anchor_y='top',
            color=(255, 255, 255, 255),batch=self.textBatch)
        line2=pyglet.text.Label('or Wrong Input', font_name='Arial', bold=True,
            font_size=25, x=centerX, y=centerY+150, anchor_x='center',
            anchor_y='top', color=(255, 255, 255, 255),batch=self.textBatch)
        line3=pyglet.text.Label('or Opponent Escaped!', font_name='Arial',
            bold=True, font_size=25, x=centerX, y=centerY+100,
            anchor_x='center', anchor_y='top',
            color=(255, 255, 255, 255),batch=self.textBatch)
        line4=pyglet.text.Label('Technically to Say: OFFLINE!',
            font_name='Arial',bold=True, font_size=25, x=centerX, y=centerY+50,
            anchor_x='center', anchor_y='top', color=(255, 255, 255, 255),
            batch=self.textBatch)
        infoExit=pyglet.text.Label('Exit(Esc)', font_name='Arial', bold=True,
            font_size=25,x=centerX, y=centerY-125, anchor_x='center',
            anchor_y='top', color=area[0][4],batch=self.textBatch)
        infoBack=pyglet.text.Label('Main Menu(M)', font_name='Arial',
            bold=True,font_size=25,x=centerX, y=centerY-75, anchor_x='center',
            anchor_y='top', color=area[1][4],batch=self.textBatch)    

    def drawIntruc(self,centerX,centerY):
        background=self.textBatch.add(4, pyglet.gl.GL_QUADS,None,('v2i',
            (centerX-100, centerY+75,centerX+100, centerY+75,centerX+150,
             centerY+240,centerX-150, centerY+240)),('c4B',
            (70,130,180,150, 70,130,180,150, 70,130,180,150, 70,130,180,150)))
        self.textBatch.add(4, GL_QUADS, self.intr,('v2i', (centerX-125,
            centerY+50,centerX+125, centerY+50,centerX+125, centerY+250,
            centerX-125, centerY+250)),('t2i', [0,0,1,0,1,1,0,1]))

    def drawTutorial(self,centerX,centerY):
        area=[[centerX-120,centerX+120,centerY-170,centerY-120,
               self.defaultColor],
            [centerX-110,centerX+110, centerY-120,centerY-70,
             self.defaultColor]]
        background=self.textBatch.add(4, pyglet.gl.GL_QUADS, None,('v2i',
            (centerX-350, centerY-250,centerX+350, centerY-250,centerX+350,
            centerY+250,centerX-350, centerY+250)),('c4B', (70,130,180,200,
            70,130,180,200, 70,130,180,200, 70,130,180,200)))
        if centerX-120<self.mouseX<centerX+120 and centerY-170<self.mouseY\
            <centerY-120:color=self.specialColor
        else:color=self.defaultColor
        infoBack=pyglet.text.Label('Main Menu(M)', font_name='Arial',
            bold=True,font_size=25,x=centerX, y=centerY-125, anchor_x='center',
            anchor_y='top', color=color,batch=self.textBatch)
        self.textBatch.add(4, GL_QUADS, self.tutotial,('v2i', (centerX-350,
            centerY-250,centerX+350, centerY-250,centerX+350, centerY+250,
            centerX-350, centerY+250)),('t2i', [0,0,1,0,1,1,0,1]))

def setup_fog():
    #OPenGL configuration 3
    glEnable(GL_FOG)
    glFogfv(GL_FOG_COLOR, (GLfloat * 4)(0.5, 0.69, 1.0, 1))
    glHint(GL_FOG_HINT, GL_DONT_CARE)
    glFogi(GL_FOG_MODE, GL_LINEAR)
    glFogf(GL_FOG_START, 10.0)
    glFogf(GL_FOG_END, 50.0)

def setup():
    #OPenGL configuration 3
    glClearColor(0.5, 0.69, 1.0, 1)
    glEnable(GL_CULL_FACE)
    glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_NEAREST)
    glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_NEAREST)
    setup_fog()

window = Window(width=800, height=600, caption='FLAPPY BIRD--ONLINE & 3D!',
                resizable=True)
window.set_exclusive_mouse(False)
icon1 = pyglet.image.load('resource\\16X16.png')
icon2 = pyglet.image.load('resource\\32X32.png')
window.set_icon(icon1, icon2)
setup()
pyglet.app.run()