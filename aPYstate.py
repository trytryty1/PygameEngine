import pygame, math, os
from pygame import *
import math
ASSET_PATH = "assets/"

print("Engine 1.0")
print("Using asset path: " + ASSET_PATH)

running = False
world = None
pgclock = None
pgwindow = None
pgwindowSize = (500,500)
pgguiSurface = None
pgguiSurfaceHighlight = None

# Start pygame
def init(screenWidth, screenHeight):
    print("Initializing pygame and engine")
    global running, world, pgclock, pgwindow, pgwindowSize, pgguiSurface, pgguiSurfaceHighlight
    pgwindowSize = [screenWidth, screenHeight]
    
    # Set up the drawing window
    pgwindow = pygame.display.set_mode(pgwindowSize)
    pgclock = pygame.time.Clock()
    world = World()

    pgguiSurface = pygame.Surface([screenWidth,screenHeight], pygame.SRCALPHA, 32)

    pgguiSurfaceHighlight = pygame.Surface([screenWidth,screenHeight], pygame.SRCALPHA, 32)

def run():
    global running, world, pgclock, pgwindow
    running = True
    world.start()
    print("Starting game loop")
    
    while running:
        # Checks pygame events
        for event in pygame.event.get():
            # Was close button pressed?
            if event.type == pygame.QUIT:
                running = False
            if event.type == pygame.KEYDOWN:
                Input.keyPressed(event.key)
            if event.type == pygame.KEYUP:
                Input.keyReleased(event.key)
            if event.type == pygame.MOUSEMOTION:
                x,y = event.pos
                Input.mouseMoved(x, y)
            if event.type == pygame.MOUSEBUTTONDOWN:
                Input.mouseDown[event.button-1] = True
            if event.type == pygame.MOUSEBUTTONUP:
                Input.mouseDown[event.button-1] = False

        # Update world
        world.update()

        # Draw everything
        Renderer.draw()
        
        # Constant update speed
        pgclock.tick(60)

    # End pygame
    print("Closing pygame...")
    pygame.quit()

class Entity:
    def __init__(self):
        self.position = [0,0]
        self.children = []
        self.parent = None
        self.components = []
        self.tags = []
        self.toDestroy = False
    def destroy(self):
        for c in self.children:
            c.destroy()
        for c in self.components:
            c.destroy()
        del self.components
        self.parent = None
        World.destroy(self)
        del self
        
    def addTag(self, tag):
        self.tags.append(tag)
    def addComponent(self, c):
        self.components.append(c)
        c.parent = self
    def removeComponent(self, c):
        self.components.remove(c)
    def addChild(self, e):
        self.children.append(e)
        e.parent = self
    def update(self):
        for c in self.components:
            if c.active:
                c.update()
    def start(self):
        for c in self.components:
            c.start()
    def translate(self, x, y):
        self.position[0] += x
        self.position[1] += y
    def x(self):
        return self.position[0]
    def y(self):
        return self.position[1]
    def setPos(self, x, y):
        self.position[0] = x
        self.position[1] = y

class Component:
    active = True
    parent = None
    def start(self):
        pass
    def update(self):
        pass
    def destroy(self):
        pass

class Renderer:
    sprites = []
    background = (55,155,255)
    camera = (0,0)
    drawGrid = True
    gridSize = 32
    gridColor = (44,44,44)

    @staticmethod
    def convertToCamera(pos):
        global pgwindowSize
        pos[0] -= Renderer.camera[0] - pgwindowSize[0]/2
        pos[1] -= Renderer.camera[1] - pgwindowSize[1]/2
        return pos

    def sortZLayerKey(e):
        return e.zLevel
    
    @staticmethod
    def addSprite(spriteRenderer):
        Renderer.sprites.append(spriteRenderer)
        Renderer.sprites.sort(reverse=True, key=Renderer.sortZLayerKey)

    @staticmethod
    def draw():
        global pgwindow, pgwindowSize
        pgwindow.fill(Renderer.background)
        r,g,b = Renderer.background
        Renderer.gridColor = (r - (r/6), g - (g/6), b - (b/6))

        if Renderer.drawGrid:
            remainderx = (pgwindowSize[0]%Renderer.gridSize)/2
            remaindery = (pgwindowSize[1]%Renderer.gridSize)/2
            for i in range(math.floor(pgwindowSize[0]/Renderer.gridSize) + 1):
                pygame.draw.line(pgwindow,Renderer.gridColor,
                                 (0,Renderer.gridSize*i - remaindery),
                                 (pgwindowSize[0],Renderer.gridSize*i - remaindery))
            for i in range(math.floor(pgwindowSize[1]/Renderer.gridSize) + 1):
                pygame.draw.line(pgwindow,Renderer.gridColor,
                                 (Renderer.gridSize*i - remainderx,0),
                                 (Renderer.gridSize*i - remainderx,pgwindowSize[0]))
        
        for s in Renderer.sprites:
            x, y = Renderer.convertToCamera(s.center())
            
            img = pygame.transform.rotate(s.sprite,s.rotation)
            img = pygame.transform.scale(img, (s.width, s.height))
            pgwindow.blit(img, (x, y))

        GUI.drawGUI()
        
        # Flip the display
        pygame.display.flip()

class SpriteRenderer(Component):
    sprite = None
    width = 0
    height = 0
    rotation = 0
    zLevel = 0
    draw = True
    offset = [0,0]
    alpha = 0
    def start(self):
        print("here")
        Renderer.addSprite(self)
    def center(self):
        return [
            self.parent.x() + self.offset[0] - self.width/2,
            self.parent.y() + self.offset[1] - self.height/2]

class World:
    entities = []

    @staticmethod
    def findAllWithTag(tag):
        taglist = []
        for e in World.entites:
            if tag in e.tags:
                taglist.append(e)
        return taglist

    @staticmethod
    def start():
        for e in World.entities:
            e.start()
        World.hasStarted = True

    @staticmethod
    def destroy(e):
        World.entities.remove(e)
        
    @staticmethod
    def __init__():
        World.entities = []
        World.hasStarted = False

    @staticmethod
    def update():
        for e in World.entities:
            e.update()

    @staticmethod
    def addEntity(e):
        World.entities.append(e)
        if World.hasStarted:
            e.start()

def getImage(name):
    global ASSET_PATH
    transColor = pygame.Color(255, 255, 255)
    image = pygame.image.load(ASSET_PATH + "sprites/" + name + ".png").convert()
    image.set_colorkey(transColor)
    return image

class GUI:
    elements = []
    
    class GUIContainer:
        def __init__(self, width, height):
            self.width = width
            self.height = height
            self.x = 0
            self.y = 0
            self.mouseDown = False
            self.mouseHover = False
            self.containers = []
        def mouseEntered(self):
            self.mouseHover = True
        def mouseLeft(self):
            self.mouseHover = False
        def mouseDown(self):
            self.mouseDown = True
        def mouseUp(self):
            self.mouseDown = False
        def add(self, container):
            self.containers.append(container)
        def mouseMoved(self):
            x = Input.getMouseX()
            y = Input.getMouseY()
            self.mouseHover = x > self.x and x < self.x + self.width and y > self.y and y < self.y + self.height
            for c in self.containers:
                c.mouseMoved()
        def draw(self):
            for c in self.containers:
                c.draw()

    class GUIExactLayout(GUIContainer):
        def __init__(self):
            super().__init__(500, 500)

        def draw(self):
            for c in self.containers:
                c.draw()

        def add(self, container, x, y, width, height):
            self.containers.append(container)
            container.x = x
            container.y = y
            container.width = width
            container.height = height

    class GUIPanelLayout(GUIContainer):
        def __init__(self, rows, columns, vertical):
            super().__init__(500, 500)
            self.vertical = vertical
            self.rows = rows
            self.columns = columns

        def add(self, container, x):
            self.containers.append(container)
            container.x = self.x + len(self.containers) * (self.width/self.rows)
            container.y = self.y
            container.width = (self.width/self.rows)
            container.height = self.height
            
    class GUIButton(GUIContainer):
        DEFAULT_GUI_BUTTON_SIZE = (50,50)
        def __init__(self, title):
            width, height = GUI.GUIButton.DEFAULT_GUI_BUTTON_SIZE
            super().__init__(width, height)
            self.title = title
            self.color = (100,100,100)
            self.sprite = None

        def setSprite(self, sprite):
            self.sprite = pygame.transform.scale(sprite, (self.width, self.height))
            
        def draw(self):
            global pgguiSurface, pgguiSurfaceHighlight
            if self.sprite is None:
                pygame.draw.rect(pgguiSurface, self.color, (self.x, self.y, self.width, self.height))
            else:
                pgguiSurface.blit(self.sprite, (self.x, self.y))
            alpha = 50
            if self.mouseHover:
                if Input.mouseLeftPressed():
                    alpha = 100
                pygame.draw.rect(pgguiSurfaceHighlight, (0,0,0,alpha), (self.x, self.y, self.width, self.height))

    def drawGUI():
        for e in GUI.elements:
            e.draw()
        global pgguiSurface, pgguiSurfaceHighlight, pgwindow
        pgguiSurface.blit(pgguiSurfaceHighlight, (0,0))
        pgwindow.blit(pgguiSurface, (0,0))
        pgguiSurfaceHighlight.fill((0,0,0,0))
        

    @staticmethod
    def addGUIElement(e):
        GUI.elements.append(e)

    def mouseMoved():
        for e in GUI.elements:
            e.mouseMoved()

class Input:
    mouseX = 0
    mouseY = 0
    mouseDown = [0,0,0]
    keysDown = []
    
    @staticmethod
    def getMouseX():
        return Input.mouseX

    def getWorldMouseX():
        global pgwindowSize
        return Input.mouseX - Renderer.camera[0] - pgwindowSize[0]/2

    def getWorldMouseY():
        global pgwindowSize
        return Input.mouseY - Renderer.camera[1] - pgwindowSize[1]/2
    
    @staticmethod
    def getMouseY():
        return Input.mouseY
    
    @staticmethod
    def mouseLeftPressed():
        return Input.mouseDown[0]
    
    @staticmethod
    def mouseScrollPressed():
        return Input.mouseDown[1]
    
    @staticmethod
    def mouseRightPressed():
        return Input.mouseDown[2]

    @staticmethod
    def isKeyDown(key):
        return Input.keysDown[key]

    @staticmethod
    def keyPressed(pyKey):
        Input.keysDown[pyKey] = True

    @staticmethod
    def keyReleased(pyKey):
        Input.keysDown[pyKey] = False

    @staticmethod
    def mouseMoved(x, y):
        Input.mouseX = x
        Input.mouseY = y
        GUI.mouseMoved()
