import aPYstate
from aPYstate import *
import math
import random


init(750,750)

class FollowCursor(Component):
    def update(self):
        self.transform.location.x = Input.getWorldMouseX()
        self.transform.location.y = Input.getWorldMouseY()

class Player(Component):
    def update(self):
        
        self.rb = self.parent.getComponent(RigidBody)
        print(self.rb.velocity)
        if Input.isKeyDown(pygame.K_a):
            rb.applyForce(Vector(-self.speed,0))
        elif Input.isKeyDown(pygame.K_d):
            rb.applyForce(Vector(self.speed,0))
        elif Input.isKeyDown(pygame.K_w):
            rb.applyForce(self.jumpForce)
        else:
            #self.ani.setAnimaion("stop")
            pass
        print(self.rb.velocity)
        
    def start(self):
        self.speed = 3
        self.jumpForce = Vector(0,1)

def mkWall(x, y, width = 32, height = 32):
    WALL_SIZE = 32
    # Create wall
    obj = Entity(x = x, y = y)

    # Setup sprite for wall
    sprite_renderer = SpriteRenderer(sprite = getImage("wood"), width = width, height = height)
    obj.addComponent(sprite_renderer)

    # Add wall to world and return wall
    aPYstate.World.addEntity(obj)

    rb = RigidBody(physicsType = STATIC)
    obj.addComponent(rb)
    obj.addComponent(ColliderRect(Rectangle(0,0,width, height)))
    return obj

# setup player
obj = Entity(x = 0, y = 0)
# Setup sprite for wall
sprite_renderer = SpriteRenderer(sprite = getImage("metal"))
obj.addComponent(sprite_renderer)

rb = RigidBody()
obj.addComponent(rb)
obj.addComponent(ColliderRect(Rectangle(0,0,32, 32)))

obj.addComponent(Player())

# Add wall to world and return wall
aPYstate.World.addEntity(obj)

for i in range(10):
    physicsWall = mkWall(random.random()*500-250,random.random()*500-250, 150, 25)
    rb = RigidBody()
run()
