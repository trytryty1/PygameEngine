import aPYstate
from aPYstate import *
import math


init(750,750)

class Tower(Component):
    width = 0
    height = 0
    grid = []
    def start(self):
        self.grid = [[0]* self.width] * self.height

class Enemy(Component):
    def update(self):
        x1 = Input.getWorldMouseX()
        y1 = Input.getWorldMouseY()
        self.parent.setPos(x1,y1)

class Ani(Component):
    def __init__(self):
        self.x = 0
    def update(self):
        global sheet
        self.renderer.sprite = sheet.getSprite(math.floor(self.x),2)
        self.x += 0.3
        if(self.x > 9):
            self.x = 1
    def start(self):
        self.x = 0
        self.renderer = self.parent.getComponent(SpriteRenderer)


def block(x, y, sprite):
    obj1 = Entity()
    obj1.translate(x,y)
    rend1 = SpriteRenderer()
    rend1.sprite = getImage(sprite)
    rend1.width = 32
    rend1.height = 32
    rend1.zLevel = 1
    obj1.addComponent(rend1)
    aPYstate.World.addEntity(obj1)
    return obj1

exactLayout = GUI.GUIExactLayout()

panelLayout = GUI.GUIPanelLayout(5,0,False)
exactLayout.add(panelLayout, 0,0,300,50)

button = GUI.GUIButton("PRESS ME")
panelLayout.add(button, 0)

button = GUI.GUIButton("PRESS ME")
panelLayout.add(button, 0)
button.setSprite(getImage("wood"))

GUI.addGUIElement(exactLayout)

block(0,0,"wood")

metal = block(0,32,"metal")
collider = ColliderRect()
collider.setRect(0,0,32,32)
metal.addComponent(collider)

selector = block(0,0,"selector")
enemy = Enemy()
selector.addComponent(enemy)
collider = ColliderRect()
collider.setRect(0,0,32,32)
selector.addComponent(collider)

sheet = SpriteSheet(getImage("sprite sheet test"), 4, 9, 64, 64)
rend1 = SpriteRenderer()
rend1.sprite = sheet.getSprite(1,1)
rend1.width = 64
rend1.height = 64
obj = Entity()
obj.addComponent(rend1)
ani = Ani()
obj.addComponent(ani)
obj.translate(200,200)
aPYstate.World.addEntity(obj)

# Test Chunk
sample_tile_set_sprite_sheet = SpriteSheet(
    getImage("sample_tile_set_sprite_sheet"),
    5, 10, 64, 64)
sample_data = {
    "Size": 32,
    
    0: {
        "name": "Grass",
        "sprite": getImage("Wood"),#sample_tile_set_sprite_sheet.getSprite(0,2),
    },
    1: {
        "name": "Sand",
        "sprite": getImage("Metal"),#sample_tile_set_sprite_sheet.getSprite(0,1),
    },
}
chunk = TileGrid.Chunk(0,0,10,10,sample_data)

chunk.setTile(1,1,1)
chunk.setTile(1,2,1)
chunk.setTile(1,3,1)
chunk.setTile(1,4,1)
chunk.setTile(1,5,1)

chunk.updateChuckSprite()
chunkobj = block(0,0,"wood")
chunkobj.getComponent(SpriteRenderer).sprite = chunk.chunk_sprite
chunkobj.getComponent(SpriteRenderer).zLevel = 10
chunkobj.getComponent(SpriteRenderer). height = 500
chunkobj.getComponent(SpriteRenderer).width = 500



r = 0
def collide(c):
    global r
    r+=0.01
    Renderer.background[1] = abs(math.sin(r)) * 255

collider.collisionListener = collide

run()
