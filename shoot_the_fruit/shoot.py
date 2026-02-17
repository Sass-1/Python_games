from random import randint
import pgzrun
count = 0
apple = Actor("apple")


def draw():
    screen.clear( )
    apple.draw( )
    
def place_apple( ):
    apple.x = randint(10, 800)
    apple.y = randint(10, 600)
    
def on_mouse_down(pos):
    global count
    if apple.collidepoint(pos):
        print("Good shot!")
        count = count + 1
        place_apple()
    else:
        print("You missed!")
        print (f"You've hit the fruit {count} times")
        quit()

place_apple()    

pgzrun.go()