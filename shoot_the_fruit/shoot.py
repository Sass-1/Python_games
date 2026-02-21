from random import randint
import pgzrun
import os

os.environ['SDL_VIDEO_CENTERED'] = '1'

count = 0
fruits = ["kiwi", "apple"]

target = Actor(fruits[0])


def draw():
    screen.clear( )
    target.draw( )
    
def place_target( ):
    
    random_index = randint(0, len(fruits) - 1)
    target.image = fruits[random_index]
    
    target.x = randint(50, 750)
    target.y = randint(50, 550)
    
def on_mouse_down(pos):
    global count
    if target.collidepoint(pos):
        print("Good shot!")
        count = count + 1
        place_target()
    else:
        print("You missed!")
        print (f"You've hit the fruit {count} times")
        quit()

place_target()    

pgzrun.go()