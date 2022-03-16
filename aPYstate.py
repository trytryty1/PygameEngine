

__version__ = '0.1'
__author__ = 'David Wing'

import os
import math

try:
    import pygame
    print("pygame module sucesfully installed")
except ModuleNotFoundError:
    print("module 'pygame' is not installed you tard")
from pygame import *


ASSET_PATH = "assets/"

print("You are using aPYstate! Good luck...")
print("Using asset path: " + ASSET_PATH)

# ================
# Engine variables
# ================
_running = False
_pgclock = None
_pgwindow = None
_pgwindowSize = (500,500)
_pgguiSurface = None
_pgguiSurfaceHighlight = None

# ============
# Start pygame
# ============
def init(screenWidth, screenHeight):
    print("Initializing pygame and engine")
    global _running, _world, _pgclock, _pgwindow, _pgwindowSize, _pgguiSurface, _pgguiSurfaceHighlight
    _pgwindowSize = [screenWidth, screenHeight]
    # Set up the drawing window
    _pgwindow = pygame.display.set_mode(_pgwindowSize)
    _pgclock = pygame.time.Clock()
    _pgguiSurface = pygame.Surface([screenWidth,screenHeight], pygame.SRCALPHA, 32)
    _pgguiSurfaceHighlight = pygame.Surface([screenWidth,screenHeight], pygame.SRCALPHA, 32)
    _pgguiSurfaceHighlight.set_colorkey((255,255,255))

    
# Math stuff
class Vector:
    def __init__(self, x, y):
        self.x = x
        self.y = y

    def __str__(self):
        return "x: " + str(self.x) + " ||| y: " + str(self.y)
        
    def add(self, vector):
        return Vector(self.x + vector.x, self.y + vector.y)

    def magnitude(self):
        return math.hypot(self.x, self.y)

    def unit(self):
        magnitude = self.magnitude()
        # Stop division by 0
        if magnitude == 0:
            return Vector(0,0)
        return Vector(self.x/magnitude, self.y/magnitude)

    def subtract(self, vector):
        return Vector(self.x - vector.x, self.y - vector.y)

    def distance(self, vector):
        return Vector(math.hypot(vector.x - self.x, vector.y - self.y))

    def angle(self, vector):
        return math.atan2(self.x - vector.x, self.y - vector.y)

    def angleUnit(self, vector):
        angle = self.angle(vector)
        angleVector = Vector(math.cos(angle), math.sin(angle))
        return angleVector.unit()

    def scale(self, scale):
        return Vector(self.x*scale, self.y*scale)

    def set(self, x, y):
        self.x = x
        self.y = y

# =========
# Game loop
# =========
def run():
    global _running, _world, _pgclock, _pgwindow
    _running = True
    print("Starting game loop")

    World.start()
    
    while _running:
        # Checks pygame events
        for event in pygame.event.get():
            # Was close button pressed?
            if event.type == pygame.QUIT:
                _running = False
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

        # Update _world
        World.update()

        Physics.updatePhysics()

        # Draw everything
        Renderer.draw()
        
        # Constant update speed
        _pgclock.tick(60)

    # End pygame
    print("Closing pygame...")
    pygame.quit()

# ============
# Entity Class
# ============
class Transform:
    def __init__(self, x, y, rotation = 0):
        self.location = Vector(x, y)
        self.rotation = rotation

    def translate(self, x, y):
        self.location = self.location.add(Vector(x, y))

    def rotate(self, rotation):
        self.rotation += rotation

    def getX(self):
        return self.location.x

    def getY(self):
        return self.location.y

    def getRotation(self):
        return self.rotation

class Rectangle(Transform):
    def __init__(self, x = 0, y = 0, width = 32, height = 32, rotation = 0):
        self.location = Vector(x, y)
        self.rotation = rotation
        self.size = Vector(width, height)

    def getWidth(self):
        return self.size.x

    def getHeight(self):
        return self.size.y

    def center(self):
        return Vector(self.getX() - self.getWidth()*0.5, self.getY() - self.getHeight()*0.5)

    def isCollided(self, rect2):
        rect1 = self
        if (
                rect1.getX() < rect2.getX() + rect2.getWidth() and
                rect1.getX() + rect1.getWidth() > rect2.getX() and
                rect1.getY() < rect2.getY() + rect2.getHeight() and
                rect1.getY() + rect1.getHeight() > rect2.getY()
        ):
            return True
        else:
            return False

    def contains(self, point):
        if (
                point.getX() > self.getWidth() and point.getX() < self.getX() + self.getWidth() and
                point.getY() > self.getHeight() and point.getY() < self.getY() + self.getHeight()
            ):
            return True
        else:
            return False
            

class Entity:
    def __init__(self, x=0, y=0):
        self.transform = Transform(x,y)
        self.children = []
        self.parent = None
        self.components = {}
        self.tags = []
        self.toDestroy = False
        
    def destroy(self):
        for c in self.children:
            c.destroy()
        for c in self.components.values():
            c.destroy()
        del self.components
        self.parent = None
        World.destroy(self)
        del self
        
    def addTag(self, tag):
        self.tags.append(tag)
        
    def getComponent(self, name):
        return self.components.get(name.__name__, None)
    
    def addComponent(self, c):
        if c.__class__.__name__ in self.components.keys():
            print("Entity already has component width class name: " + c.__class__.__name__)
            return False
        else:
            self.components.update({str(c.__class__.__name__): c})
            c.setParent(self)
            
    def removeComponent(self, c):
        self.components.remove(c)
        
    def addChild(self, e):
        self.children.append(e)
        e.parent = self
        
    def update(self):
        for c in self.components.values():
            if c.active:
                c.update()
                
    def start(self):
        for c in self.components.values():
            c.start()

    def onCollisionEnter(self, collider):
        for c in self.components.values():
            c.onCollisionEnter(collider)

# ===============
# Component Class
# ===============
class Component:
    active = True
    parent = None
    def __init__(self):
        self.transform = None
        
    def setParent(self, parent):
        self.parent = parent
        self.transform = parent.transform
        
    def start(self):
        pass
    
    def update(self):
        pass
    
    def destroy(self):
        self.parent = None
        self.transform = None

    def onCollisionEnter(self, collision):
        pass

# ==============================
# ==============================
# Graphic Systems
# ==============================
# ==============================
class Renderer:
    sprites = []
    background = [55,155,255]
    drawGrid = False
    gridSize = 32
    gridColor = (44,44,44)
    class Camera:
        def __init__(self):
            self.location = Vector(0,0)
        def convertToCamera(self, pos):
            return pos.add(self.location.add(
                Vector(_pgwindowSize[0]/2, _pgwindowSize[1]/2)))
        
    camera = Camera()

    @staticmethod
    def convertToCamera(pos):
        global _pgwindowSize
        pos[0] -= Renderer.camera[0] - _pgwindowSize[0]/2
        pos[1] -= Renderer.camera[1] - _pgwindowSize[1]/2
        return pos

    def sortZLayerKey(e):
        return e.zLevel
    
    @staticmethod
    def addSprite(spriteRenderer):
        Renderer.sprites.append(spriteRenderer)
        Renderer.sprites.sort(reverse=True, key=Renderer.sortZLayerKey)

    @staticmethod
    def removeSprite(spriteRenderer):
        Renderer.sprites.remove(spriteRenderer)

    @staticmethod
    def draw():
        global _pgwindow, _pgwindowSize
        _pgwindow.fill(Renderer.background)
        r,g,b = Renderer.background
        Renderer.gridColor = (r - (r/6), g - (g/6), b - (b/6))

        if Renderer.drawGrid:
            remainderx = (_pgwindowSize[0]%Renderer.gridSize)/2
            remaindery = (_pgwindowSize[1]%Renderer.gridSize)/2
            for i in range(math.floor(_pgwindowSize[0]/Renderer.gridSize) + 1):
                pygame.draw.line(_pgwindow,Renderer.gridColor,
                                 (0,Renderer.gridSize*i - remaindery),
                                 (_pgwindowSize[0],Renderer.gridSize*i - remaindery))
            for i in range(math.floor(_pgwindowSize[1]/Renderer.gridSize) + 1):
                pygame.draw.line(_pgwindow,Renderer.gridColor,
                                 (Renderer.gridSize*i - remainderx,0),
                                 (Renderer.gridSize*i - remainderx,_pgwindowSize[0]))
        # Draw sprites
        for s in Renderer.sprites:
            drawLoc = Renderer.camera.convertToCamera(s.center())
            # Rotate sprite
            img = pygame.transform.rotate(s.sprite,s.transform.rotation)
            # Scale sprite
            img = pygame.transform.scale(img, (s.rectangle.getWidth(), s.rectangle.getHeight()))
            # Draw sprite
            _pgwindow.blit(img, (drawLoc.x, drawLoc.y))

        GUI.drawGUI()
        
        # Flip the display
        pygame.display.flip()

class Animation(Component):
    def __init__(self, data):
        self.data = data
        self.currentFrame = 0
        self.animationSpeed = 1
        self.currentAnimation = "None"
        self.renderer = None

    def setAnimaion(self, animName):
        if self.currentAnimation == animName:
            return
        self.currentAnimation = animName
        self.currentFrame = 0
        
    def start(self):
        self.renderer = self.parent.getComponent(SpriteRenderer)
        
    def update(self):
        if self.currentAnimation != "None":
            print(self.currentAnimation)
            currentData = self.data[self.currentAnimation]
            self.currentFrame += self.animationSpeed
            if self.currentFrame >= len(currentData):
                self.currentFrame = 0
            self.renderer.sprite = currentData[math.floor(self.currentFrame)]

class SpriteRenderer(Component):
    def __init__(self, x=0, y=0, width=32, height=32, sprite=None,
                 rotation = 0, zLevel = 0, alpha = 0):
        self.rectangle = Rectangle(x, y, width, height)
        self.sprite = sprite
        self.zLevel = zLevel
        self.alpha = alpha
        self.draw = True
        
    def start(self):
        Renderer.addSprite(self)
        
    def center(self):
        return self.transform.location.add(self.rectangle.center())
    
    def destroy(self):
        Renderer.removeSprite(self)

class SpriteSheet:
    def __init__(self, image, rows, columns, spriteWidth, spriteHeight):
        self.image = image
        self.rows = rows
        self.columns = columns
        self.spriteWidth = spriteWidth
        self.spriteHeight = spriteHeight
        self.images = [0] * (rows * columns)
        for x in range(columns * rows):
            self.images[x] = self.makeSprite(x%columns,math.floor(x/columns))
                
    def getSprite(self, x, y):
        return self.images[y * self.columns + x]
        
    def makeSprite(self, x, y):
        image = pygame.Surface((self.spriteWidth, self.spriteHeight)).convert()
        image.set_colorkey((255,255,255))
        image.blit(self.image, (0, 0),
                   (self.spriteWidth*x, self.spriteHeight*y,
                    self.spriteWidth*x + self.spriteWidth, self.spriteHeight*x + self.spriteHeight))
        image.set_colorkey((0,0,0))
        return image

# ==============================
# ==============================
# Physics Systems
# ==============================
# ==============================

DYNAMIC = 0
KINETIC = 1
STATIC = 3

class Physics:
    colliders = []
    ridgidBodys = []

    @staticmethod
    def addCollider(collider):
        Physics.colliders.append(collider)

    @staticmethod
    def removeCollider(collider):
        Physics.colliders.remove(collider)

    @staticmethod
    def addRigidBody(e):
        Physics.ridgidBodys.append(e)

    @staticmethod
    def removeRigidBody(e):
        Physics.ridgidBodys.remove(e)

    # collision left = 0, collision right = 1, collision up = 2, collision down = 3
    # TODO: add bounce
    @staticmethod
    def rigidBodyCollision(rb1, rb2, collisiondir):
        dirmatrix = Vector(0,0)
        if collisiondir == 0:
            dirmatrix.x = 1
            dirmatrix.y = 0
        elif collisiondir == 1:
            dirmatrix.x = 1
            dirmatrix.y = 0
        elif collisiondir == 2:
            dirmatrix.x = 0
            dirmatrix.y = 1
        elif collisiondir == 3:
            dirmatrix.x = 0
            dirmatrix.y = 1

        if rb1.physicsType != STATIC:
            force1 = rb2.velocity.scale(rb2.mass)
            force1 = force1.scale(1/rb1.mass)
            force1.x *= dirmatrix.x
            force1.y *= dirmatrix.y
            rb1.applyForce(force1)
        if rb2.physicsType != STATIC:
            force2 = rb1.velocity.scale(rb1.mass)
            force2 = force2.scale(-1/rb2.mass)
            force2.x *= dirmatrix.x
            force2.y *= dirmatrix.y
            rb1.applyForce(force2)

    @staticmethod
    def updatePhysics():
        global _gravity, _world_border
        ridgidBodys = Physics.ridgidBodys
        for rb in ridgidBodys:
            toMove = Vector(0,0)
            # Apply gravity
            if rb.physicsType == DYNAMIC:
                rb.velocity = rb.velocity.add(_gravity)

            
            toMove = toMove.add(rb.velocity)
            print(rb.velocity)
            #print(toMove)

            # Check if object has velocity
            # TODO: FIX IF VELOCITY
            if True:#not (rb.velocity.x == 0 and rb.velocity.y == 0):
                collider1 = rb.collider
                

                # Check for collision
                for rb2 in ridgidBodys:
                    if rb2 != rb:# and not (rb2.physicsType == STATIC and rb2.physicsType == STATIC):
                        collider2 = rb2.collider
                        rect1 = collider1.getRect()
                        rect2 = collider2.getRect()
                        if (
                                (rect1.getX() + toMove.x > rect2.getX() and
                                rect1.getX() + toMove.x < rect2.getX() + rect2.getWidth() and
                                rect1.getY() > rect2.getY() and
                                rect1.getY() < rect2.getY() + rect2.getHeight()) or
                                (rect1.getX() + rect1.getWidth() + toMove.x > rect2.getX() and
                                rect1.getX() + rect1.getWidth() + toMove.x < rect2.getX() + rect2.getWidth() and
                                rect1.getY() + rect1.getHeight() > rect2.getY() and
                                rect1.getY() + rect1.getHeight() < rect2.getY() + rect2.getHeight()) or
                                (rect1.getX() + rect1.getWidth() + toMove.x > rect2.getX() and
                                rect1.getX() + rect1.getWidth() + toMove.x < rect2.getX() + rect2.getWidth() and
                                rect1.getY() > rect2.getY() and
                                rect1.getY() < rect2.getY() + rect2.getHeight())
                            ):
                            if(rect1.getX() > rect2.getX()):
                                Physics.rigidBodyCollision(rb, rb2, 1)
                            if(rect1.getX() < rect2.getX()):
                                Physics.rigidBodyCollision(rb, rb2, 0)
                        elif (
                                (rect1.getX() + toMove.x > rect2.getX() and
                                rect1.getX() + toMove.x < rect2.getX() + rect2.getWidth() and
                                rect1.getY() + toMove.y > rect2.getY() and
                                rect1.getY() + toMove.y < rect2.getY() + rect2.getHeight()) or
                                (rect1.getX() + rect1.getWidth() + toMove.x > rect2.getX() and
                                rect1.getX() + rect1.getWidth() + toMove.x < rect2.getX() + rect2.getWidth() and
                                rect1.getY() + rect1.getHeight() + toMove.y > rect2.getY() and
                                rect1.getY() + rect1.getHeight() + toMove.y < rect2.getY() + rect2.getHeight()) or
                                (rect1.getX() + rect1.getWidth() + toMove.x > rect2.getX() and
                                rect1.getX() + rect1.getWidth() + toMove.x < rect2.getX() + rect2.getWidth() and
                                rect1.getY() > rect2.getY() and
                                rect1.getY() < rect2.getY() + rect2.getHeight())
                            ):
                            # Collided bottom
                            if(rect1.getY() > rect2.getY()):
                                Physics.rigidBodyCollision(rb, rb2, 2)
                            if(rect1.getY() < rect2.getY()):
                                Physics.rigidBodyCollision(rb, rb2, 3)
            rb.transform.translate(toMove.x, toMove.y)
            toMove.x = 0
            toMove.y = 0

        Physics.testCollision()
        
        for rb in ridgidBodys:
            rb.finalizeMove()

        # Keep all ridgid bodys in the border
        for rb in ridgidBodys:
            if(rb.transform.getX() < _world_border.getX()):
                rb.transform.location.x = _world_border.getX()
                rb.velocity.x += 1
            if(rb.transform.getY() < _world_border.getY()):
                rb.transform.location.y = _world_border.getY()
                rb.velocity.y += 1
            if(rb.transform.getX() > _world_border.getX() + _world_border.getWidth()):
                rb.transform.location.x = _world_border.getX() + _world_border.getWidth()
                rb.velocity.x -= 1
            if(rb.transform.getY() > _world_border.getY() + _world_border.getHeight()):
                rb.transform.location.y = _world_border.getY() + _world_border.getHeight()
                rb.velocity.y -= 1
            

    @staticmethod
    def testCollision():
        for c in Physics.ridgidBodys:
            rbcollider = c.collider
            for c2 in Physics.colliders:
                if not (rbcollider == c2):
                    if rbcollider.getRect().isCollided(c2.getRect()):
                        c.parent.onCollisionEnter(Collision(c2, c2.parent, None))

_gravity = Vector(0, 0.01)
_world_border = Rectangle(-250,-250,500,500)
def setGravity(gravity):
    global _gravity
    _gravity = gravity

class RigidBody(Component):

    def __init__(self, physicsType = DYNAMIC):
        self.velocity = Vector(0,0)
        self.collisionVelocity = Vector(0,0)
        self.physicsType = physicsType
        self.collider = None
        self.mass = 1
        
    def start(self):
        # TODO: Try to make this safer please
        if self.collider == None:
            self.collider = self.parent.getComponent(ColliderRect)
            
        Physics.addRigidBody(self)
        self.finalizeMove()

    def destroy(self):
        Physics.removeRigidBody(self)

    def undoMove(self):
        self.transform.x = self.lastLocation.x
        self.transform.y = self.lastLocation.y
        self.resetLastLoc()

    def resetLastLoc(self):
        self.lastLocation = Vector(self.transform.getX(), self.transform.getY())

    def finalizeMove(self):
        self.resetLastLoc()

    def applyForce(self, force):
        self.velocity = self.velocity.add(force)

    def applyCollisionForce(self, force):
        self.collisionVelocity = self.collisionVelocity.add(force)

class Collision():
    def __init__(self, collider, gameObject, rigidBody):
        self.collider = collider
        self.gameObject = gameObject
        self.rigidBody = rigidBody

class ColliderRect(Component):
    def start(self):
        Physics.addCollider(self)
    def destroy(self):
        Physics.removeCollider(self)
    def __init__(self, rectangle = Rectangle(0,0,32,32)):
        self.rectangle = rectangle
        self.isTrigger = True
        self.collisionListener = None
    def collided(self, c):
        if self.collisionListener is None:
            pass
        else:
            self.collisionListener(c)
    def getRect(self):
        world = Rectangle(self.rectangle.getX() + self.transform.getX(),
                  self.rectangle.getY() + self.transform.getY(),
                  self.rectangle.getWidth(),
                  self.rectangle.getHeight())
        return world

# ==============================
# ==============================
# Utils
# ==============================
# ==============================
_assets = {}

def loadImage(name):
    global ASSET_PATH, _assets
    transColor = pygame.Color(255, 255, 255)
    image = pygame.image.load(ASSET_PATH + "sprites/" + name + ".png").convert()
    image.set_colorkey(transColor)
    _assets[name] = image
    return image

def getImage(name):
    global _assets
    if name in _assets:
        return _assets[name]
    else:
        return loadImage(name)

class Grid:
    def __init__(self, width, height):
        self.width = width
        self.height = height
        self.grid = [0] * (width * height)

    def set(self, x, y, value):
        self.grid[y * self.width + x] = value

    def get(self, x, y):
        return self.grid[y * self.width + x]

class TileGrid(Component):
    
    class Chunk:
        def __init__(self, x, y, width, height, tile_set_data):
            self.x = x
            self.y = y
            self.grid = Grid(width, height)
            self.tile_set_data = tile_set_data

            # Used to determine if the chunk should be re-rendered
            self.flagged = True
            self.chunk_sprite = None

        def setTile(self, x, y, tile):
            self.grid.set(x, y, tile)
            self.flagged = True

        def getTile(self, x, y):
            return self.grid.get(x, y)

        def updateChuckSprite(self):
            tile_size = self.tile_set_data["Size"]
            image = pygame.Surface((self.grid.width*tile_size,
                        self.grid.height*tile_size)).convert()
            
            for x in range(self.grid.width):
                for y in range(self.grid.height):
                    image.blit(
                        self.tile_set_data[self.grid.get(x, y)]["sprite"],
                        (tile_size * x, tile_size * y))

            self.chunk_sprite = image
            self.flagged = False
        
    def __init__(self, tile_set_data):
        self.tile_set_data = tile_set_data

    def update(self):
        pass

    def start(self):
        pass

    def setGrid(self, grid):
        pass

class World:
    entities = []
    hasStarted = False

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
    def update():
        for e in World.entities:
            e.update()

    @staticmethod
    def addEntity(e):
        World.entities.append(e)
        if World.hasStarted:
            e.start()

# ==============================
# ==============================
# GUI System
# ==============================
# ==============================
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

        def draw(self):
            global _pgguiSurfaceHighlight, _pgguiSurface
            pygame.draw.rect(_pgguiSurface, (0,0,0,50), (self.x, self.y, self.width, self.height))
            super().draw()

            
            
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
            global _pgguiSurface, _pgguiSurfaceHighlight
            if self.sprite is None:
                pygame.draw.rect(_pgguiSurface, self.color, (self.x, self.y, self.width, self.height))
            else:
                _pgguiSurface.blit(self.sprite, (self.x, self.y))
            alpha = 50
            if self.mouseHover:
                if Input.mouseLeftPressed():
                    alpha = 100
                pygame.draw.rect(_pgguiSurfaceHighlight, (0,0,0,alpha), (self.x, self.y, self.width, self.height))

    def drawGUI():
        for e in GUI.elements:
            e.draw()
        global _pgguiSurface, _pgguiSurfaceHighlight, _pgwindow, _pgwindowSize
        screenWidth, screenHeight = _pgwindowSize
        _pgwindow.blit(_pgguiSurface, (0,0))
        _pgwindow.blit(_pgguiSurfaceHighlight, (0,0))
        _pgguiSurfaceHighlight.fill((255,255,255))
        

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
    keysDown = {}
    
    @staticmethod
    def getMouseX():
        return Input.mouseX

    def getWorldMouseX():
        global _pgwindowSize
        return Input.mouseX - Renderer.camera.location.x - _pgwindowSize[0]/2

    def getWorldMouseY():
        global _pgwindowSize
        return Input.mouseY - Renderer.camera.location.y - _pgwindowSize[1]/2
    
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
        if not (key in Input.keysDown):
            return False
        return Input.keysDown[key]

    @staticmethod
    def keyPressed(pyKey):
        if not (pyKey in Input.keysDown):
            Input.keysDown.update({pyKey:True})
        else:
            Input.keysDown[pyKey] = True

    @staticmethod
    def keyReleased(pyKey):
        Input.keysDown[pyKey] = False

    @staticmethod
    def mouseMoved(x, y):
        Input.mouseX = x
        Input.mouseY = y
        GUI.mouseMoved()
