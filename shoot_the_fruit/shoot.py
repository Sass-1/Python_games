import pgzrun
apple = Actor("apple")

def draw():
    screen.clear( )
    apple.draw( )
    
def place_apple( ):
    apple.x = 300
    apple.y = 200
    
def on_mouse_down(pos):
    if apple.collidepoint(pos):
        print("Good shot!")
        place_apple()
    else:
        print("You missed!")
        quit()
 
place_apple()    

pgzrun.go()