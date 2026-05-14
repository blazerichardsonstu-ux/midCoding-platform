import pgzero

WIDTH = 800
HEIGHT = 800
player = Rect((100, 400), (40, 40))

def draw():
    # This function draws things on the screen
    pass
    screen.clear()
    screen.clear()
    screen.draw.filled_rect(player, "blue")
def update():
    # This function updates the game over and over
    pass 
    if keyboard.left:
        player.x -= 5

    if keyboard.right:
        player.x += 5
    if keyboard.left:
        player.x -= 5

    if keyboard.right:
        player.x += 5 
    if player.right > WIDTH:
        player.right = WIDTH
