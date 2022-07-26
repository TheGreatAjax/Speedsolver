
from menu import mainMenu
from pygame import init, display

def main():
    init()

    # Create the main screen
    width, height = 1240, 800
    screen = display.set_mode((width, height))

    # Create and run the main menu
    main = mainMenu(width, height)
    main.mainloop(screen)

if __name__ == '__main__':
    main()