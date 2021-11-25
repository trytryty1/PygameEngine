import aPYstate
from aPYstate import *

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
exactLayout.add(panelLayout, 100,100,300,50)

button = GUI.GUIButton("PRESS ME")
panelLayout.add(button, 0)

button = GUI.GUIButton("PRESS ME")
panelLayout.add(button, 0)
button.setSprite(getImage("wood"))

GUI.addGUIElement(exactLayout)

block(0,0,"wood")
block(0,32,"metal")
selector = block(0,0,"selector")
enemy = Enemy()
selector.addComponent(enemy)

run()
