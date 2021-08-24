#################################################
# CMU Final Project: Island Escape (a game)
# name: Jack Chang
# andrew id: jackchan
#
#################################################

from cmu_112_graphics import *
import string, math, time
from random import randint
import pygame



# class for sound/music
class Sound(object):
    def __init__(self, path, channel):
        self.path = path
        self.loops = 1
        self.channel = channel

    # Returns True if the sound is currently playing
    def isPlaying(self):
        return bool(pygame.mixer.Channel(self.channel).get_busy())

    # Loops = number of times to loop the sound.
    # If loops = 1 or 1, play it once.
    # If loops > 1, play it loops + 1 times.
    # If loops = -1, loop forever.
    def start(self, loops = 1, volume = 1):
        self.loops = loops
        pygame.mixer.Channel(self.channel).play(pygame.mixer.Sound(self.path), loops = loops)
        pygame.mixer.Channel(self.channel).set_volume(volume)

    # Stops the current sound from playing
    def stop(self):
        pygame.mixer.Channel(self.channel).stop()



# button class for all buttons
class Button(object):

    def __init__(self, x0, y0, x1, y1, clickEvent, regularFill, hoverFill,
    textColor, outline, text, font, fontSize, bold):
        self.x0 = x0
        self.y0 = y0
        self.x1 = x1
        self.y1 = y1
        self.clickEvent = clickEvent
        self.regularFill = regularFill
        self.textColor = textColor
        self.outline = outline
        self.text = text
        self.font = font
        self.fontSize = fontSize
        self.bold = bold
        self.hoverFill = hoverFill
        self.fill = regularFill
    
    # calculates the actual number values of the bounds of the button
    def getBounds(self, app):
        return (app.width * self.x0, app.height * self.y0, app.width * self.x1,
        app.height * self.y1)
    
    # puts together the string representing the font
    def getFont(self):
        curFont = self.font + " " + str(self.fontSize)
        if self.bold:
            curFont += " bold"
        return curFont



# class to represent all objects on the playing grid
class GridObject(object):

    def __init__(self, row, col):
        self.row = row
        self.col = col
        self.visible = True
    
    def __repr__(self):
        return f"({self.row}, {self.col})"



# class that extends GridObject, which has an added attribute color
class Mine(GridObject):

    def __init__(self, row, col, color = "red"):
        super().__init__(row, col)
        self.color = color



# class that extends GridObject, which has added attributes interval and step
class BomberRobot(GridObject):

    def __init__(self, row, col, interval):
        super().__init__(row, col)
        self.interval = interval
        self.step = 0



class Item(GridObject):

    def __init__(self, row, col, name):
        super().__init__(row, col)
        self.name = name



# class that extends GridObject, which has added attributes for the wall and color
class GridButton(GridObject):

    def __init__(self, app, row, col, wallRow, wallCol, color):
        super().__init__(row, col)
        app.grid[wallRow][wallCol] = "rock"
        self.wallRow = wallRow
        self.wallCol = wallCol
        self.wallActive = True
        self.color = color
    
    def activate(self, app):
        app.grid[self.wallRow][self.wallCol] = "empty"
        self.wallActive = False



# class that represents a teleporter (stores two points on the grid)
class Teleporter(object):

    def __init__(self, x0, y0, x1, y1, color):
        self.x0 = x0
        self.y0 = y0
        self.x1 = x1
        self.y1 = y1
        self.color = color



# initializes the buttons for the title screen and returns them in a list
def initializeTitleScreenButtons(app):
    app.konamiIndex = 0
    startButton = Button(2 / 5, 7 / 20, 3 / 5, 9 / 20, "startGame", "orange",
        "yellow", "red", "black", "Start", "Arial", 25, True)
    settingsButton = Button(2 / 5, 31 / 60, 3 / 5, 37 / 60, "settings", "orange",
        "yellow", "red", "black", "Settings", "Arial", 25, True)
    quitButton = Button(2 / 5, 41 / 60, 3 / 5, 47 / 60, "quit", "orange",
        "yellow", "red", "black", "Quit", "Arial", 25, True)
    app.buttons.append(startButton)
    app.buttons.append(settingsButton)
    app.buttons.append(quitButton)

# initializes the buttons for the settings screen and returns them in a list
def initializeSettingsScreenButtons(app):
    musicToggleButton = Button(6 / 10 - 1 / 18, 5 / 12 - 1 / 20, 7 / 10 - 1 / 18, 6 / 12 - 1 / 20, "toggleMusic",
        "black", "gray", "aqua", "black", "On" if app.music else "Off", "Arial",
        18, True)
    SFXToggleButton = Button(6 / 10 - 1 / 18, 7 / 12 - 1 / 20, 7 / 10 - 1 / 18, 8 / 12 - 1 / 20, "toggleSFX",
        "black", "gray", "aqua", "black", "On" if app.sfx else "Off", "Arial",
        18, True)
    titleScreenButton = Button(1 / 3, 45 / 60, 2 / 3, 50 / 60, "titleScreen",
        "orange", "yellow", "red", "black", "Return To Title Screen", "Arial",
        18, True)
    app.buttons.append(musicToggleButton)
    app.buttons.append(SFXToggleButton)
    app.buttons.append(titleScreenButton)

# initializes the buttons for the level select screen and returns them in a list
def initializeLevelSelectScreenButtons(app):
    for i in range (2):
        for j in range (3):
            curLevel = i * 3 + j + 1
            h1 = 0
            h2 = 0
            if i == 0:
                h1 = 1 / 3
                h2 = h1 + 1 / 7
            else:
                h1 = 1 / 4 + i * 2 / 7
                h2 = 1 / 4 + (i * 2 + 1) / 7
            if curLevel in app.levelsUnlocked:
                curButton = Button((j * 2 + 1) / 7, h1, (j + 1) * 2 / 7, h2,
                    f"level{curLevel}", "orange", "yellow", "red", "black",
                    f"Level {curLevel}", "Arial", 20, True)
                app.buttons.append(curButton)
            else:
                curButton = Button((j * 2 + 1) / 7, h1, (j + 1) * 2 / 7, h2,
                    None, "black", "black", "red", "black", "LOCKED", "Arial",
                    20, True)
                app.buttons.append(curButton)
    titleScreenButton = Button(1 / 3, 55 / 60, 2 / 3, 58 / 60, "titleScreen",
        "purple", "magenta", "aqua", "black", "Return To Title Screen", "Arial",
        18, True)
    randomLevelButton = Button(11 / 30, 15 / 20, 19 / 30, 17 / 20, "randomLevel",
        "orange", "yellow", "red", "black", "Random Level", "Arial", 20, True)
    howToPlayButton = Button(11 / 30, 4 / 20, 19 / 30, 11 / 40, "howToPlay",
        "purple", "magenta", "aqua", "black", "How To Play", "Arial", 20, True)
    app.buttons.append(titleScreenButton)
    app.buttons.append(randomLevelButton)
    app.buttons.append(howToPlayButton)

# initializes the buttons for the how to play screen
def initializeHowToPlayScreen(app):
    app.teleporters.clear()
    app.robotSprite = app.scaleImage(app.robotImage, 0.1)
    app.bomberRobotSprite = app.scaleImage(app.bomberRobotImage, 0.25)
    app.playerSprite = app.scaleImage(app.playerImage, 0.25)
    app.shieldSprite = app.scaleImage(app.shieldImage, 0.05)
    levelSelectButton = Button(1.1 / 4, 17.5 / 20, 2.9 / 4, 19.25 / 20, "levelSelect", "purple",
        "magenta", "aqua", "black", "Return to Level Select", "Arial", 20, True)
    app.buttons.append(levelSelectButton)
    teleporter1 = Teleporter(0, 0, 0, 0, "green")
    teleporter2 = Teleporter(0, 0, 0, 0, "yellow")
    mine1 = Teleporter(0, 0, 0, 0, "red")
    app.teleporters.append(teleporter1)
    app.teleporters.append(teleporter2)
    app.teleporters.append(mine1)

def initializeGrid(app, rows, cols):
    app.grid.clear()
    app.robots.clear()
    app.bomberRobots.clear()
    app.gridButtons.clear()
    app.teleporters.clear()
    app.mines.clear()
    app.items.clear()
    app.shieldTicks = 0
    app.rows = rows
    app.cols = cols
    for i in range (app.rows):
        app.grid.append([])
        for j in range (app.cols):
            app.grid[i].append("empty")

def initializeLevel1(app):
    initializeGrid(app, 6, 6)
    app.grid[3][3] = "rock"
    app.player = GridObject(0, 0)
    app.exit = GridObject(5, 5)
    robot1 = GridObject(0, 5)
    app.robots.append(robot1)

def initializeLevel2(app):
    initializeGrid(app, 15, 15)
    app.grid[3][3] = "rock"
    for i in range (3):
        app.grid[4][5 + i] = "rock"
        app.grid[i][13] = "rock"
    for i in range (5):
        app.grid[12][i] = "rock"
    app.grid[14][1] = "rock"
    app.grid[13][3] = "rock"
    app.player = GridObject(0, 0)
    app.exit = GridObject(14, 14)
    robot1 = GridObject(0, 14)
    robot2 = GridObject(14, 0)
    app.robots.append(robot1)
    app.robots.append(robot2)

def initializeLevel3(app):
    initializeGrid(app, 11, 13)
    for i in range (9):
        app.grid[1][1 + i] = "rock"
        app.grid[9][1 + i] = "rock"
        app.grid[1 + i][1] = "rock"
        app.grid[1 + i][11] = "rock"
    app.grid[0][11] = "rock"
    for i in range (3):
        app.grid[2 + i][9] = "rock"
        app.grid[6 + i][9] = "rock"
    for i in range (5):
        app.grid[3][3 + i] = "rock"
        app.grid[3 + i][7] = "rock"
        app.grid[7][3 + i] = "rock"
    app.grid[4][3] = "rock"
    app.grid[6][3] = "rock"
    app.grid[9][0] = "rock"
    app.grid[5][5] = "rock"
    app.player = GridObject(0, 0)
    app.exit = GridObject(app.rows - 1, 0)
    robot1 = GridObject(0, app.cols - 1)
    app.robots.append(robot1)
    gridButton1 = GridButton(app, 5, 6, 10, 9, "orange")
    app.gridButtons.append(gridButton1)

def initializeLevel4(app):
    initializeGrid(app, 11, 12)
    for i in range (5):
        app.grid[1][i] = "rock"
        app.grid[1][7 + i] = "rock"
        app.grid[3][i] = "rock"
        app.grid[5][1 + i] = "rock"
        app.grid[6][6 + i] = "rock"
        app.grid[9][1 + i] = "rock"
        app.grid[9][6 + i] = "rock"
    for i in range (3):
        app.grid[3][5 + i] = "rock"
        app.grid[4][7 + i] = "rock"
    for i in range (2):
        app.grid[5 + i][11] = "rock"
        app.grid[3][9 + i] = "rock"
        app.grid[6 + i][2] = "rock"
        app.grid[7 + i][4] = "rock"
        app.grid[7 + i][6] = "rock"
    app.grid[1][6] = "rock"
    app.grid[7][8] = "rock"
    app.grid[8][10] = "rock"
    app.grid[7][0] = "rock"
    app.player = GridObject(0, 0)
    app.exit = GridObject(7, 7)
    robot1 = GridObject(0, app.cols - 1)
    robot2 = GridObject(4, 0)
    app.robots.append(robot1)
    app.robots.append(robot2)
    teleporter1 = Teleporter(1, 5, 2, 0, "green")
    teleporter2 = Teleporter(3, 8, 5, 0, "yellow")
    app.teleporters.append(teleporter1)
    app.teleporters.append(teleporter2)
    gridButton1 = GridButton(app, 8, 5, 10, 1, "orange")
    app.gridButtons.append(gridButton1)

def initializeLevel5(app):
    initializeGrid(app, 11, 13)
    app.player = GridObject(0, 0)
    app.exit = GridObject(8, 4)
    robot1 = GridObject(0, app.cols - 2)
    app.robots.append(robot1)
    bomberRobot1 = BomberRobot(app.rows - 1, 0, 5)
    app.bomberRobots.append(bomberRobot1)
    for i in range (10):
        curMine = Mine(1 + i, 1)
        app.mines.append(curMine)
    app.mines.append(Mine(0, 2))
    app.mines.append(Mine(1, 2))
    for i in range (9):
        app.grid[1][3 + i] = "rock"
    for i in range (8):
        app.grid[5][4 + i] = "rock"
    for i in range (3):
        app.grid[2 + i][4] = "rock"
        app.grid[7][3 + i] = "rock"
        app.grid[9][3 + i] = "rock"
        app.grid[6 + i][7] = "rock"
        app.grid[7][8 + i] = "rock"
        app.grid[3][6 + i * 2] = "rock"
    app.grid[7][11] = "rock"
    app.grid[8][11] = "rock"
    app.grid[9][9] = "rock"
    app.grid[3][12] = "rock"
    app.grid[10][5] = "rock"
    app.grid[8][5] = "rock"
    app.grid[9][7] = "rock"
    app.grid[9][11] = "rock"
    app.grid[10][9] = "rock"
    app.grid[4][10] = "rock"
    gridButton1 = GridButton(app, 3, 5, 5, 12, "orange")
    app.gridButtons.append(gridButton1)

def initializeLevel6(app):
    initializeGrid(app, 10, 16)
    app.player = GridObject(0, 7)
    app.exit = GridObject(3, 3)
    #robot1 = GridObject(0, app.cols - 1)
    #app.robots.append(robot1)
    bomberRobot1 = BomberRobot(0, app.cols - 1, 5)
    app.bomberRobots.append(bomberRobot1)
    #app.mines.append(Mine(0, 2))
    for i in range (5):
        app.grid[0][2 + i] = "rock"
        app.grid[4 + i][1] = "rock"
        app.grid[1][11 + i] = "rock"
        app.grid[3][8 + i] = "rock"
        app.grid[1 + i][6] = "rock"
    for i in range (3):
        app.grid[1][7 + i] = "rock"
        app.grid[6][6 + i] = "rock"
        app.grid[6 + i][5] = "rock"
        app.grid[8][2 + i] = "rock"
        app.grid[2][2 + i] = "rock"
        app.grid[4][2 + i] = "rock"
        app.grid[3 + i][14] = "rock"
    app.grid[3][4] = "rock"
    app.grid[6][3] = "rock"
    app.grid[5][8] = "rock"
    app.grid[5][9] = "rock"
    app.grid[4][9] = "rock"
    app.grid[3][13] = "rock"
    app.grid[6][14] = "rock"
    app.grid[7][14] = "rock"
    app.grid[8][14] = "rock"
    app.grid[9][12] = "rock"
    gridButton1 = GridButton(app, 3, 7, 2, 13, "orange")
    gridButton2 = GridButton(app, 2, 12, 4, 15, "purple")
    gridButton3 = GridButton(app, 4, 8, 5, 15, "magenta")
    gridButton4 = GridButton(app, 3, 5, 3, 2, "turquoise")
    app.gridButtons.append(gridButton1)
    app.gridButtons.append(gridButton2)
    app.gridButtons.append(gridButton3)
    app.gridButtons.append(gridButton4)
    teleporter1 = Teleporter(5, 7, 2, 14, "green")
    app.teleporters.append(teleporter1)
    shield1 = Item(7, 3, "shield")
    app.items.append(shield1)

def initializeRandomLevel(app):
    app.grid.clear()
    app.robots.clear()
    app.rows = randint(15, 25)
    app.cols = randint(15, 25)
    app.player = GridObject(0, 0)
    app.exit = GridObject(app.rows - 1, app.cols - 1)
    for i in range (app.rows):
        app.grid.append([])
        for j in range (app.cols):
            app.grid[i].append("")
    generateLevel(app)
    app.player.visible = True
    app.exit.visible = True

def initializeGameOverScreenButtons(app):
    retryButton = Button(11 / 30, 8 / 20, 19 / 30, 10 / 20, "retry",
        "red", "magenta", "lime", "black", "Try Again", "Arial", 24, True)
    levelSelectButton = Button(1 / 4, 12 / 20, 3 / 4, 14 / 20, "levelSelect", "green",
        "lime", "red", "black", "Return to Level Select", "Arial", 25, True)
    titleScreenButton = Button(3 / 10, 16 / 20, 7 / 10, 18 / 20, "titleScreen",
        "blue", "aqua", "red", "black", "Return To Title Screen", "Arial",
        20, True)
    app.buttons.append(retryButton)
    app.buttons.append(levelSelectButton)
    app.buttons.append(titleScreenButton)

def initializeWinScreenButtons(app):
    playAgainButton = Button(11 / 30, 8 / 20, 19 / 30, 10 / 20, "playAgain",
        "red", "magenta", "lime", "black", "Play Again", "Arial", 24, True)
    levelSelectButton = Button(1 / 4, 12 / 20, 3 / 4, 14 / 20, "levelSelect", "green",
        "lime", "red", "black", "Return to Level Select", "Arial", 25, True)
    titleScreenButton = Button(3 / 10, 16 / 20, 7 / 10, 18 / 20, "titleScreen",
        "blue", "aqua", "red", "black", "Return To Title Screen", "Arial",
        20, True)
    app.buttons.append(playAgainButton)
    app.buttons.append(levelSelectButton)
    app.buttons.append(titleScreenButton)

def playSong(app, songName):

    if not app.music or app.curSong.path == songName:
        return
    app.curSong.stop()
    app.curSong = Sound(songName, 0)
    vol = 0.5
    if songName == "Carefree Victory.mp3" or songName == "TereziTheme.mp3":
        vol = 0.22
    elif songName == "Showtime.mp3":
        vol = 0.6
    elif songName == "Harleboss.mp3":
        vol = 0.3
    elif songName == "Megalovania.mp3":
        vol = 0.35
    elif songName == "Doctor.mp3":
        vol = 0.42
    app.curSong.start(-1, vol * 0.5)

# switches screens by clearing the current screen and initializing buttons
def switchScreen(app, screen):
    app.mode = screen
    app.buttons.clear()
    if screen == "titleScreen":
        initializeTitleScreenButtons(app)
        playSong(app, "Homestuck.mp3")
    elif screen == "settingsScreen":
        initializeSettingsScreenButtons(app)
    elif screen == "levelSelectScreen":
        initializeLevelSelectScreenButtons(app)
        playSong(app, "Homestuck.mp3")
    elif screen == "howToPlayScreen":
        initializeHowToPlayScreen(app)
    elif screen == "level1":
        initializeLevel1(app)
        playSong(app, "Explore.mp3")
    elif screen == "level2":
        initializeLevel2(app)
        playSong(app, "Showtime.mp3")
    elif screen == "level3":
        initializeLevel3(app)
        playSong(app, "Harleboss.mp3")
    elif screen == "level4":
        initializeLevel4(app)
        playSong(app, "TavrosTheme.mp3")
    elif screen == "level5":
        initializeLevel5(app)
        playSong(app, "TereziTheme.mp3")
    elif screen == "level6":
        initializeLevel6(app)
        playSong(app, "Megalovania.mp3")
    elif screen == "randomLevel":
        initializeRandomLevel(app)
        playSong(app, "Doctor.mp3")
    elif screen == "gameOverScreen":
        initializeGameOverScreenButtons(app)
        playSong(app, "Game Over.mp3")
    elif screen == "winScreen":
        initializeWinScreenButtons(app)
        playSong(app, "Carefree Victory.mp3")

# checks if the click is within the bounds given
def insideButton(x0, y0, x1, y1, clickX, clickY):
    return clickX >= x0 and clickX <= x1 and clickY >= y0 and clickY <= y1

# loops through each button and checks if that button has been pressed
def checkForButtonPress(app, clickX, clickY):
    for button in app.buttons:
        (x0, y0, x1, y1) = button.getBounds(app)
        if insideButton(x0, y0, x1, y1, clickX, clickY):
            if app.sfx and button.clickEvent != None:
                app.clickSound.start(0, 0.15)
            return button.clickEvent

# loops through each button and checks if the mouse if hovering over that button
def checkForButtonHover(app, mouseX, mouseY):
    for button in app.buttons:
        (x0, y0, x1, y1) = button.getBounds(app)
        if insideButton(x0, y0, x1, y1, mouseX, mouseY):
            button.fill = button.hoverFill
            return
        else:
            button.fill = button.regularFill

# gets the shortest path between two objects on a grid, using only empty tiles
def getShortestPath(app, object1, object2):
    x0 = object1.row
    y0 = object1.col
    x1 = object2.row
    y1 = object2.col
    q = [(x0, y0, 0, [])]
    minDist = None
    path = []
    visited = set()
    while len(q) > 0:
        (curX, curY, curDist, curPath) = q.pop(0)
        if not isValidPos(app, curX, curY) or (curX, curY) in visited:
            continue
        visited.add((curX, curY))
        if curX == x1 and curY == y1:
            if minDist == None or curDist < minDist:
                minDist = curDist
                path = curPath
            continue
        q.append((curX + 1, curY, curDist + 1, curPath + [(curX + 1, curY)]))
        q.append((curX - 1, curY, curDist + 1, curPath + [(curX - 1, curY)]))
        q.append((curX, curY + 1, curDist + 1, curPath + [(curX, curY + 1)]))
        q.append((curX, curY - 1, curDist + 1, curPath + [(curX, curY - 1)]))
    return (minDist, path)

# checks if a position is valid (if it is on the grid, and isn't an obstacle)
def isValidPos(app, row, col):
    return not (row < 0 or col < 0 or row >= app.rows or col >= app.cols or \
        (app.grid[row][col] != "empty" and app.grid[row][col] != "" \
        and app.grid[row][col] != "exit"))

# finds shortest path through weighted 2D graph using Dijkstra
def createPath(app, startNode, endNode, weights):
    shortestPaths = {}
    for i in range (app.rows):
        for j in range (app.cols):
            shortestPaths[(i, j)] = (-1, [])
    q = [(startNode[0], startNode[1], 0, [])]
    while len(q) > 0:
        (curX, curY, curDist, curPath) = q.pop(0)
        if curX < 0 or curY < 0 or curX >= app.rows or curY >= app.cols:
            continue
        curPos = (curX, curY)
        if shortestPaths[curPos][0] == -1 or curDist < shortestPaths[curPos][0]:
            shortestPaths[curPos] = (curDist, curPath)
        else:
            continue
        if curPos == endNode:
            continue
        if curX + 1 < app.rows:
            q.append((curX + 1, curY, curDist + weights[(curX, curY, curX + 1, \
                curY)], curPath + [(curX + 1, curY)]))
        if curX - 1 > 0:
            q.append((curX - 1, curY, curDist + weights[(curX, curY, curX - 1, \
                curY)], curPath + [(curX - 1, curY)]))
        if curY + 1 < app.cols:
            q.append((curX, curY + 1, curDist + weights[(curX, curY, curX, \
                curY + 1)], curPath + [(curX, curY + 1)]))
        if curY - 1 > 0:
            q.append((curX, curY - 1, curDist + weights[(curX, curY, curX, \
                curY - 1)], curPath + [(curX, curY - 1)]))
    for (row, col) in shortestPaths[endNode][1]:
        app.grid[row][col] = "empty"

# creates a dictionary of randomized weights
def randomizeWeights(rows, cols):
    weights = {}
    for i in range (rows):
        for j in range (cols):
            if not i == rows - 1:
                curRandDist1 = randint(1000, 10000)
                curRandDist2 = randint(900, 999)
                curRandDist2 *= -1
                weights[(i, j, i + 1, j)] = curRandDist1
                weights[(i + 1, j, i, j)] = curRandDist2
            if not j == cols - 1:
                curRandDist1 = randint(1000, 10000)
                curRandDist2 = randint(900, 999)
                curRandDist2 *= -1
                weights[(i, j, i, j + 1)] = curRandDist1
                weights[(i, j + 1, i, j)] = curRandDist2
    return weights

# checks if a grid is valid (if all squares are reachable from all other squares)
def isValidGrid(app, row, col):
    components = []
    cComponent = 1
    visited = []
    app.grid[row][col] = "rock"
    for i in range (app.rows):
        components.append([])
        visited.append([])
        for j in range (app.cols):
            components[i].append(0)
            visited[i].append(True if app.grid[i][j] == "rock" else False)
    q = []
    for i in range (app.rows):
        for j in range (app.cols):
            if components[i][j] != 0:
                continue
            q.append((i, j))
            while len(q) > 0:
                (curX, curY) = q.pop(0)
                if visited[curX][curY]:
                    continue
                visited[curX][curY] = True
                components[curX][curY] = cComponent
                if isValidPos(app, curX + 1, curY):
                    q.append((curX + 1, curY))
                if isValidPos(app, curX - 1, curY):
                    q.append((curX - 1, curY))
                if isValidPos(app, curX, curY + 1):
                    q.append((curX, curY + 1))
                if isValidPos(app, curX, curY - 1):
                    q.append((curX, curY - 1))
            cComponent += 1
    app.grid[row][col] = "empty"
    for i in range (app.rows):
        for j in range (app.cols):
            if components[i][j] != 1 and components[i][j] != 0:
                return False
    return True


# generates a random level
def generateLevel(app):
    # previous code used to generate a random level that I don't want to delete
    # just yet
#    weights = randomizeWeights(app.rows, app.cols)
#    createPath(app, (app.player.row, app.player.col),
#        (app.exit.row, app.exit.col), weights)
    wallX = randint(2, 5)
    wallY = randint(2, 5)
    app.grid[wallX][wallY] = "rock"
    app.grid[wallX + 1][wallY] = "empty"
    app.grid[wallX - 1][wallY] = "empty"
    app.grid[wallX][wallY + 1] = "empty"
    app.grid[wallX][wallY - 1] = "empty"
    app.grid[wallX + 1][wallY + 1] = "empty"
    app.grid[wallX - 1][wallY + 1] = "empty"
    app.grid[wallX + 1][wallY - 1] = "empty"
    app.grid[wallX - 1][wallY - 1] = "empty"
    app.grid[app.player.row][app.player.col] = "empty"
    app.grid[app.exit.row][app.exit.col] = "exit"
    for i in range (app.rows):
        for j in range (app.cols):
            if app.grid[i][j] != "" or (i == app.exit.row and \
                j == app.exit.col) or not isValidGrid(app, i, j):
                continue
            app.grid[i][j] = "empty" if randint(1, 5) <= 3 else "rock"
    robot1 = GridObject(randint(app.rows - 6, app.rows - 1), \
        randint(app.cols - 6, app.cols - 1))
    while app.grid[robot1.row][robot1.col] != "empty":
        robot1.row = randint(app.rows - 6, app.rows - 1)
        robot1.col = randint(app.cols - 6, app.cols - 1)
    robot1.visible = True
    app.robots.append(robot1)



# gets the bounds of the cell at (row, col)
def getCellBounds(app, row, col):
    lMargin = app.width * app.leftMargin
    rMargin = app.width * app.rightMargin
    tMargin = app.height * app.topMargin
    bMargin = app.height * app.bottomMargin
    gridWidth  = app.width - lMargin - rMargin
    gridHeight = app.height - tMargin - bMargin
    cellWidth = gridWidth / app.cols
    cellHeight = gridHeight / app.rows
    x0 = lMargin + col * cellWidth
    x1 = lMargin + (col+ 1) * cellWidth
    y0 = tMargin + row * cellHeight
    y1 = tMargin + (row + 1) * cellHeight
    return (x0, y0, x1, y1)



def moveRobots(app):
    app.BFSPath.clear()
    for robot in app.robots:
        shortestPath = getShortestPath(app, robot, app.player)
        if len(shortestPath[1]) == 0:
            if app.sfx:
                app.deathSound.start(0, 0.4)
            loadGameOver(app)
            break
        robot.row = shortestPath[1][0][0]
        robot.col = shortestPath[1][0][1]
        if (app.player.row, app.player.col) == (robot.row, robot.col):
            if app.sfx:
                app.deathSound.start(0, 0.4)
            loadGameOver(app)
            break
        app.BFSPath.append(shortestPath[1])
    for bomberRobot in app.bomberRobots:
        shortestPath = getShortestPath(app, bomberRobot, app.player)
        if len(shortestPath[1]) == 0:
            if app.sfx:
                app.deathSound.start(0, 0.4)
            loadGameOver(app)
            break
        bomberRobot.step += 1
        if bomberRobot.step == bomberRobot.interval:
            curMine = Mine(bomberRobot.row, bomberRobot.col)
            app.mines.append(curMine)
            bomberRobot.step = 0
        bomberRobot.row = shortestPath[1][0][0]
        bomberRobot.col = shortestPath[1][0][1]
        if (app.player.row, app.player.col) == (bomberRobot.row, bomberRobot.col):
            if app.sfx:
                app.deathSound.start(0, 0.4)
            loadGameOver(app)
            break
        app.BFSPath.append(shortestPath[1])

# checks for grid button presses
def checkGridButtonPresses(app):
    for gridButton in app.gridButtons:
        if not gridButton.wallActive:
            continue
        if (app.player.row, app.player.col) == (gridButton.row, gridButton.col):
            if app.sfx:
                app.gridButtonPressSound.start(0, 0.5)
            gridButton.activate(app)

# checks if the player just got onto a teleporter
def checkTeleportation(app):
    for teleporter in app.teleporters:
        if (app.player.row, app.player.col) == (teleporter.x0, teleporter.y0):
            app.player.row = teleporter.x1
            app.player.col = teleporter.y1
            app.justTeleported = True
            break
        if (app.player.row, app.player.col) == (teleporter.x1, teleporter.y1):
            app.player.row = teleporter.x0
            app.player.col = teleporter.y0
            app.justTeleported = True
            break

# scales the robot image
def scaleRobotImage(app):
    app.robotSprite = app.scaleImage(app.robotImage, 1.5 / (max(app.rows, app.cols) + 2))

# scales the bomber robot image
def scaleBomberRobotImage(app):
    app.bomberRobotSprite = app.scaleImage(app.bomberRobotImage, 3 / (max(app.rows, app.cols) + 2))

# scales the player image
def scalePlayerImage(app):
    app.playerSprite = app.scaleImage(app.playerImage, 4 / (max(app.rows, app.cols) + 2))

def scaleShieldImage(app):
    app.shieldSprite = app.scaleImage(app.shieldImage, 1 / (max(app.rows, app.cols) + 2))

# loads the game over screen
def loadGameOver(app, type = "caught"):
    app.loseLevel = app.mode
    app.loseType = type
    switchScreen(app, "gameOverScreen")

# checks if the player has won (reached the exit)
def checkForWin(app):
    return (app.player.row, app.player.col) == (app.exit.row, app.exit.col)

# changes the colors of the teleporters
def animateTeleporters(app):
    for teleporter in app.teleporters:
        if teleporter.color == "green":
            teleporter.color = "lime"
        elif teleporter.color == "lime":
            teleporter.color = "green"
        elif teleporter.color == "red":
            teleporter.color = "magenta"
        elif teleporter.color == "magenta":
            teleporter.color = "red"
        elif teleporter.color == "orange":
            teleporter.color = "yellow"
        elif teleporter.color == "yellow":
            teleporter.color = "orange"

# changes the colors of the teleporters
def animateMines(app):
    for mine in app.mines:
        if mine.color == "red":
            mine.color = "magenta"
        elif mine.color == "magenta":
            mine.color = "red"

# changes the color of the player shield
def animateShield(app):
    app.shieldColor = "blue" if app.shieldColor == "aqua" else "aqua"

# checks to see if any robots or the player is on a mine
def checkMines(app):
    usedMines = []
    playerHit = False
    for i in range (len(app.mines)):
        mine = app.mines[i]
        if (app.player.row, app.player.col) == (mine.row, mine.col):
            if app.shieldTicks == 0:
                if app.sfx:
                    app.explosionSound.start(0, 0.3)
                loadGameOver(app, "mine")
            else:
                usedMines.append(i)
                playerHit = True
    deadRobots = []
    #deadBomberRobots = []
    for i in range (len(app.robots)):
        for j in range (len(app.mines)):
            if (app.robots[i].row, app.robots[i].col) == (app.mines[j].row, app.mines[j].col):
                deadRobots.append(i)
                if j not in usedMines:
                    usedMines.append(j)
    #for i in range (len(app.bomberRobots)):
    #    for j in range (len(app.mines)):
    #        if (app.bomberRobots[i].row, app.bomberRobots[i].col) == (app.mines[j].row, app.mines[j].col):
    #            deadBomberRobots.append(i)
    #            usedMines.append(j)
    deadRobots.reverse()
    #deadBomberRobots.reverse()
    usedMines.reverse()
    for index in deadRobots:
        del app.robots[index]
    #for index in deadBomberRobots:
    #    del app.bomberRobots[index]
    for index in usedMines:
        del app.mines[index]
    if len(deadRobots) > 0 and app.sfx:
        app.explosionSound.start(0, 0.3)
    if playerHit and app.sfx:
        app.shieldHitSound.start(0, 0.5)

# checks if the player is on an item pickup
def checkItems(app):
    for i in range (len(app.items)):
        if (app.player.row, app.player.col) == (app.items[i].row, app.items[i].col):
            if app.items[i].name == "shield":
                if app.sfx:
                    app.powerUpSound.start(0, 0.5)
                app.shieldTicks = 10
            del app.items[i]
            return

# loads the win screen
def loadWin(app):
    app.winLevel = app.mode
    if app.winLevel != "randomLevel" and app.winLevel != "level6":
        app.levelsUnlocked.add(int(app.winLevel[-1]) + 1)
    switchScreen(app, "winScreen")

# toggles the music on/off
def toggleMusic(app):
    app.music = not app.music
    if not app.music:
        app.curSong.stop()
    else:
        app.curSong = Sound("Homestuck.mp3", 0)
        app.curSong.start(-1, 0.5)

# toggles the sound effects on/off
def toggleSFX(app):
    app.sfx = not app.sfx

# loads/unlocks all the levels
def unlockAllLevels(app):
    app.levelsUnlocked.clear()
    for i in range (1, 7):
        app.levelsUnlocked.add(i)
    app.konamiUnlocked = True



# called when the app is first initialized
def appStarted(app):
    pygame.mixer.init()
    pygame.mixer.set_num_channels(10)
    app.robotImage = app.loadImage("robot1.png")
    app.robotSprite = app.scaleImage(app.robotImage, 1 / 12)
    app.bomberRobotImage = app.loadImage("robot2.png")
    app.bomberRobotSprite = app.scaleImage(app.bomberRobotImage, 1 / 12)
    app.playerImage = app.loadImage("person.png")
    app.playerSprite = app.scaleImage(app.playerImage, 1 / 2)
    app.shieldImage = app.loadImage("shield.png")
    app.shieldSprite = app.scaleImage(app.shieldImage, 1 / 2)
    app.curSong = Sound("TavrosTheme.mp3", 0)
    app.curSong.start(-1)
    app.clickSound = Sound("Click.mp3", 1)
    app.explosionSound = Sound("Explosion.mp3", 2)
    app.deathSound = Sound("DeathSound.mp3", 3)
    app.marioCoinSound = Sound("MarioCoin.mp3", 4)
    app.shieldBreakSound = Sound("GlassBreaking.mp3", 5)
    app.powerUpSound = Sound("MarioPowerUp.mp3", 6)
    app.shieldHitSound = Sound("MetalHit.mp3", 7)
    app.gridButtonPressSound = Sound("GridButtonPress.mp3", 8)
    app.music = True
    app.sfx = True
    app.levelsUnlocked = set()
    app.levelsUnlocked.add(1)
    app.grid = []
    app.rows = 0
    app.cols = 0
    app.leftMargin = 1 / 40
    app.rightMargin = 1 / 40
    app.topMargin = 1 / 7
    app.bottomMargin = 1 / 40
    app.robots = []
    app.bomberRobots = []
    app.buttons = []
    app.player = GridObject(0, 0)
    app.exit = GridObject(0, 0)
    app.visualizeBFS = False
    app.BFSPath = []
    app.items = []
    app.gridButtons = []
    app.teleporters = []
    app.justTeleported = False
    app.mines = []
    app.loseLevel = ""
    app.winLevel = ""
    app.shieldTicks = 0
    app.shieldColor = "blue"
    app.konamiSequence = ["Up", "Up", "Down", "Down", "Left", "Right", "Left", "Right", "b", "a"]
    app.konamiIndex = 0
    app.konamiUnlocked = False
    switchScreen(app, "titleScreen")

# draws all the buttons
def drawButtons(app, canvas):
    for button in app.buttons:
        (x0, y0, x1, y1) = button.getBounds(app)
        canvas.create_rectangle(x0, y0, x1, y1, fill = button.fill,
        outline = button.outline)
        canvas.create_text((x0 + x1) / 2, (y0 + y1) / 2, text = button.text,
        fill = button.textColor,
        font = button.getFont())

# draws a circle centered in a cell with the given radius and color
def drawCircleInCell(app, canvas, row, col, radius, color):
    (x0, y0, x1, y1) = getCellBounds(app, row, col)
    cX = (x0 + x1) / 2
    cY = (y0 + y1) / 2
    canvas.create_oval(cX - radius, cY - radius, cX + radius, cY + radius, fill = color)

# draws all the grid buttons
def drawGridButtons(app, canvas):
    for gridButton in app.gridButtons:
        drawCircleInCell(app, canvas, gridButton.row, gridButton.col, 10, gridButton.color)
        if gridButton.wallActive:
            (x0, y0, x1, y1) = getCellBounds(app, gridButton.wallRow, gridButton.wallCol)
            canvas.create_rectangle(x0, y0, x1, y1, fill = gridButton.color)

# draws all the teleporters
def drawTeleporters(app, canvas):
    for teleporter in app.teleporters:
        drawCircleInCell(app, canvas, teleporter.x0, teleporter.y0, 20, teleporter.color)
        drawCircleInCell(app, canvas, teleporter.x1, teleporter.y1, 20, teleporter.color)

# draws all the mines
def drawMines(app, canvas):
    for mine in app.mines:
        drawCircleInCell(app, canvas, mine.row, mine.col, 8, mine.color)

# draws all the items
def drawItems(app, canvas):
    for item in app.items:
        if item.name == "shield":
            (x0, y0, x1, y1) = getCellBounds(app, item.row, item.col)
            cX = (x0 + x1) / 2
            cY = (y0 + y1) / 2
            canvas.create_image(cX, cY, image = ImageTk.PhotoImage(app.shieldSprite))

# draws the shield on the player if it is active
def drawPlayerShield(app, canvas):
    if app.shieldTicks == 0:
        return
    (x0, y0, x1, y1) = getCellBounds(app, app.player.row, app.player.col)
    canvas.create_oval(x0 + 2, y0 + 2, x1 - 2, y1 - 2, fill = app.shieldColor)

# draws the grid
def drawGrid(app, canvas):
    for i in range (len(app.grid)):
        for j in range (len(app.grid[i])):
            lMargin = app.width * app.leftMargin
            rMargin = app.width * app.rightMargin
            tMargin = app.height * app.topMargin
            bMargin = app.height * app.bottomMargin
            tileWidth = (app.width - lMargin - rMargin) / app.cols
            tileHeight = (app.height - tMargin - bMargin) / app.rows
            canvas.create_rectangle(lMargin + tileWidth * j,
                tMargin + tileHeight * i,
                lMargin + tileWidth * (j + 1),
                tMargin + tileHeight * (i + 1),
                fill = "blue" if app.grid[i][j] == "empty" else "gray",
                outline = "black")

# draws the player
def drawPlayer(app, canvas):
    if not app.player.visible:
        return
    (x0, y0, x1, y1) = getCellBounds(app, app.player.row, app.player.col)
    cX = (x0 + x1) / 2
    cY = (y0 + y1) / 2
    #canvas.create_text((x0 + x1) / 2, (y0 + y1) / 2, text = "player",
        #fill = "lime", font = "Arial 15")
    canvas.create_image(cX, cY, image = ImageTk.PhotoImage(app.playerSprite))

# draws all the regular robots
def drawRobots(app, canvas):
    for robot in app.robots:
        if not robot.visible:
            continue
        (x0, y0, x1, y1) = getCellBounds(app, robot.row, robot.col)
        cX = (x0 + x1) / 2
        cY = (y0 + y1) / 2
        canvas.create_image(cX, cY, image = ImageTk.PhotoImage(app.robotSprite))

# draws all the bomber robots
def drawBomberRobots(app, canvas):
    for bomberRobot in app.bomberRobots:
        if not bomberRobot.visible:
            continue
        (x0, y0, x1, y1) = getCellBounds(app, bomberRobot.row, bomberRobot.col)
        cX = (x0 + x1) / 2
        cY = (y0 + y1) / 2
        canvas.create_image(cX, cY, image = ImageTk.PhotoImage(app.bomberRobotSprite))

# draws the exit
def drawExit(app, canvas):
    if not app.exit.visible:
        return
    (x0, y0, x1, y1) = getCellBounds(app, app.exit.row, app.exit.col)
    canvas.create_rectangle(x0, y0, x1, y1, fill = "yellow", outline = "black")

# draws the path of the BFS if toggled
def drawBFSPath(app, canvas):
    if not app.visualizeBFS:
        return
    for path in app.BFSPath:
        for (row, col) in path:
            (x0, y0, x1, y1) = getCellBounds(app, row, col)
            canvas.create_rectangle(x0, y0, x1, y1, fill = "purple",
                outline = "black")



# draws the background for the title screen
def drawTitleScreenBackground(app, canvas):
    canvas.create_rectangle(0, 0, app.width, app.height, fill = "turquoise")

# draws the text for the title screen
def drawTitleScreenText(app, canvas):
    canvas.create_text(app.width / 2, app.height / 5,
        text = "Island Escape", fill = "blue", font = "Arial 50 bold")

# the mousePressed function for the title screen
def titleScreen_mousePressed(app, event):
    clickEvent = checkForButtonPress(app, event.x, event.y)
    if clickEvent == "startGame":
        switchScreen(app, "levelSelectScreen")
    elif clickEvent == "settings":
        switchScreen(app, "settingsScreen")
    elif clickEvent == "quit":
        app.curSong.stop()
        app.quit()

def titleScreen_keyPressed(app, event):
    if app.konamiUnlocked:
        return
    if event.key == app.konamiSequence[app.konamiIndex]:
        app.konamiIndex += 1
        if app.konamiIndex == len(app.konamiSequence):
            if app.sfx:
                app.marioCoinSound.start(0, 0.15)
            unlockAllLevels(app)
    else:
        app.konamiIndex = 0

# the mouseMoved function for the title screen
def titleScreen_mouseMoved(app, event):
    checkForButtonHover(app, event.x, event.y)

# the redrawAll function for the title screen
def titleScreen_redrawAll(app, canvas):
    drawTitleScreenBackground(app, canvas)
    drawTitleScreenText(app, canvas)
    drawButtons(app, canvas)



# draws the background for the title screen
def drawSettingsScreenBackground(app, canvas):
    canvas.create_rectangle(0, 0, app.width, app.height, fill = "turquoise")

# draws the text for the title screen
def drawSettingsScreenText(app, canvas):
    canvas.create_text(app.width / 2, app.height / 6,
        text = "Settings", fill = "blue", font = "Arial 50 bold")
    canvas.create_text(app.width / 2 - app.width / 50 - app.width / 26, app.height * 11 / 24 - app.height / 18,
        text = "Music:", fill = "purple", font = "Arial 35")
    canvas.create_text(app.width / 2 - app.width / 26, app.height * 15 / 24 - app.height / 18,
        text = "SFX:", fill = "purple", font = "Arial 35")

# the mousePressed function for the title screen
def settingsScreen_mousePressed(app, event):
    clickEvent = checkForButtonPress(app, event.x, event.y)
    if clickEvent == "titleScreen":
        switchScreen(app, "titleScreen")
    elif clickEvent == "toggleMusic":
        toggleMusic(app)
        for button in app.buttons:
            if button.clickEvent == "toggleMusic":
                button.text = "On" if button.text == "Off" else "Off"
                return
    elif clickEvent == "toggleSFX":
        toggleSFX(app)
        for button in app.buttons:
            if button.clickEvent == "toggleSFX":
                button.text = "On" if button.text == "Off" else "Off"
                return

# the mouseMoved function for the title screen
def settingsScreen_mouseMoved(app, event):
    checkForButtonHover(app, event.x, event.y)

# the redrawAll function for the title screen
def settingsScreen_redrawAll(app, canvas):
    drawSettingsScreenBackground(app, canvas)
    drawSettingsScreenText(app, canvas)
    drawButtons(app, canvas)



# draws the background for the level select screen
def drawLevelSelectScreenBackground(app, canvas):
    canvas.create_rectangle(0, 0, app.width, app.height, fill = "turquoise")

# draws the text for the level select screen
def drawLevelSelectScreenText(app, canvas):
    canvas.create_text(app.width / 2, app.height / 9,
        text = "Level Select", fill = "blue", font = "Arial 50 bold")

# the mousePressed function for the level select screen
def levelSelectScreen_mousePressed(app, event):
    clickEvent = checkForButtonPress(app, event.x, event.y)
    if clickEvent == "level1":
        switchScreen(app, "level1")
    elif clickEvent == "level2":
        switchScreen(app, "level2")
    elif clickEvent == "level3":
        switchScreen(app, "level3")
    elif clickEvent == "level4":
        switchScreen(app, "level4")
    elif clickEvent == "level5":
        switchScreen(app, "level5")
    elif clickEvent == "level6":
        switchScreen(app, "level6")
    elif clickEvent == "randomLevel":
        switchScreen(app, "randomLevel")
    elif clickEvent == "titleScreen":
        switchScreen(app, "titleScreen")
    elif clickEvent == "howToPlay":
        switchScreen(app, "howToPlayScreen")

# the mouseMoved function for the level select screen
def levelSelectScreen_mouseMoved(app, event):
    checkForButtonHover(app, event.x, event.y)

# the redrawAll function for the level select screen
def levelSelectScreen_redrawAll(app, canvas):
    drawLevelSelectScreenBackground(app, canvas)
    drawLevelSelectScreenText(app, canvas)
    drawButtons(app, canvas)



# draws the background for the how to play screen
def drawHowToPlayScreenBackground(app, canvas):
    canvas.create_rectangle(0, 0, app.width, app.height, fill = "turquoise")

# draws the text for the how to play screen
def drawHowToPlayScreenText(app, canvas):
    canvas.create_text(app.width / 2, app.height / 11,
        text = "How To Play", fill = "blue", font = "Arial 50 bold")
    canvas.create_text(app.width / 2, app.height / 5,
        text = "This is you, the player", fill = "black", font = "Arial 20")
    canvas.create_text(app.width / 2, app.height / 5 + app.height / 16,
        text = "Use the arrow keys to move", fill = "black", font = "Arial 20")
    canvas.create_text(app.width / 2, app.height / 5 + app.height / 16 * 2,
        text = "You are trying to reach the exit of each level", fill = "black", font = "Arial 20")
    canvas.create_text(app.width / 2, app.height / 5 + app.height / 16 * 3, text = "Don't get caught or get blown up by any mines", font = "Arial 20")
    canvas.create_text(app.width / 2, app.height / 5 + app.height / 16 * 4,
        text = "Every time you make a move, all enemies will also make a move", fill = "black", font = "Arial 20")
    canvas.create_text(app.width / 2, app.height / 5 + app.height / 16 * 5,
        text = "There are two types of enemies", fill = "black", font = "Arial 20")
    canvas.create_text(app.width / 2, app.height / 5 + app.height / 16 * 6,
        text = "The chaser robot will just chase you around", fill = "black", font = "Arial 20")
    canvas.create_text(app.width / 2, app.height / 5 + app.height / 16 * 7,
        text = "The bomber robot will also chase you, but occassionaly drop a mine", fill = "black", font = "Arial 20")
    canvas.create_text(app.width / 2, app.height / 5 + app.height / 16 * 8, text = "Teleporters will teleport you to the other of the same color", font = "Arial 20")
    canvas.create_text(app.width / 2, app.height / 5 + app.height / 16 * 9, text = "Buttons need to be pressed to open their corresponding wall", font = "Arial 20")
    canvas.create_text(app.width / 2, app.height / 5 + app.height / 16 * 10, text = "The shield powerup grants you immunity to mines for 10 moves", font = "Arial 20")

# the mousePressed function for the how to play screen
def howToPlayScreen_mousePressed(app, event):
    clickEvent = checkForButtonPress(app, event.x, event.y)
    if clickEvent == "levelSelect":
        switchScreen(app, "levelSelectScreen")

# the mouseMoved function for the how to play screen
def howToPlayScreen_mouseMoved(app, event):
    checkForButtonHover(app, event.x, event.y)

# the timerFired function for the how to play screen
def howToPlayScreen_timerFired(app):
    animateTeleporters(app)

def drawSprites(app, canvas):
    canvas.create_image(app.width / 2 - 160, 135, image = ImageTk.PhotoImage(app.playerSprite))
    canvas.create_image(120, app.height / 2 + 40, image = ImageTk.PhotoImage(app.robotSprite))
    canvas.create_image(app.width - 120, app.height / 2 + 40, image = ImageTk.PhotoImage(app.bomberRobotSprite))
    canvas.create_image(130, app.height - 80, image = ImageTk.PhotoImage(app.shieldSprite))
    canvas.create_rectangle(app.width - 140, 217, app.width - 110, 239, fill = "yellow")
    canvas.create_oval(app.width - 130, 264, app.width - 114, 280, fill = app.teleporters[2].color)
    canvas.create_oval(20, app.height / 2 + 118, 60, app.height / 2 + 158, fill = app.teleporters[0].color)
    canvas.create_oval(app.width - 60, app.height / 2 + 118, app.width - 20, app.height / 2 + 158, fill = app.teleporters[1].color)
    canvas.create_oval(25, app.height / 2 + 174, 45, app.height / 2 + 194, fill = "magenta")
    canvas.create_rectangle(app.width - 50, app.height / 2 + 173, app.width - 20, app.height / 2 + 195, fill = "magenta")

# the redrawAll function for the how to play screen
def howToPlayScreen_redrawAll(app, canvas):
    drawHowToPlayScreenBackground(app, canvas)
    drawHowToPlayScreenText(app, canvas)
    drawSprites(app, canvas)
    drawButtons(app, canvas)



# draws the background for the random level
def drawRandomLevelBackground(app, canvas):
    canvas.create_rectangle(0, 0, app.width, app.height, fill = "aqua")

# draws the text for the random level
def drawRandomLevelText(app, canvas):
    canvas.create_text(app.width / 2, app.height / 14,
        text = "Random Level", fill = "red", font = "Arial 50 bold")

# the keyPressed function for the random level
def randomLevel_keyPressed(app, event):
    if event.key == "m":
        moveRobots(app)
    if event.key == "Up":
        if isValidPos(app, app.player.row - 1, app.player.col):
            app.player.row -= 1
            moveRobots(app)
    if event.key == "Down":
        if isValidPos(app, app.player.row + 1, app.player.col):
            app.player.row += 1
            moveRobots(app)
    if event.key == "Right":
        if isValidPos(app, app.player.row, app.player.col + 1):
            app.player.col += 1
            moveRobots(app)
    if event.key == "Left":
        if isValidPos(app, app.player.row, app.player.col - 1):
            app.player.col -= 1
            moveRobots(app)
    if event.key == "t":
        app.visualizeBFS = not app.visualizeBFS
    if event.key == "r":
        initializeRandomLevel(app)
    if event.key == "q":
        switchScreen(app, "levelSelectScreen")

# the timerFired function for the random level
def randomLevel_timerFired(app):
    scalePlayerImage(app)
    scaleRobotImage(app)
    if checkForWin(app):
        loadWin(app)

# the redrawAll function for the random level
def randomLevel_redrawAll(app, canvas):
    drawRandomLevelBackground(app, canvas)
    drawRandomLevelText(app, canvas)
    drawGrid(app, canvas)
    drawBFSPath(app, canvas)
    drawPlayer(app, canvas)
    drawRobots(app, canvas)
    drawExit(app, canvas)



# draws the background for the first level
def drawLevel1Background(app, canvas):
    canvas.create_rectangle(0, 0, app.width, app.height, fill = "aqua")

# draws the text for the first level
def drawLevel1Text(app, canvas):
    canvas.create_text(app.width / 2, app.height / 14,
        text = "Level 1", fill = "red", font = "Arial 50 bold")

# the keyPressed function for the first level
def level1_keyPressed(app, event):
    if event.key == "m":
        moveRobots(app)
    if event.key == "Up":
        if isValidPos(app, app.player.row - 1, app.player.col):
            app.player.row -= 1
            moveRobots(app)
    if event.key == "Down":
        if isValidPos(app, app.player.row + 1, app.player.col):
            app.player.row += 1
            moveRobots(app)
    if event.key == "Right":
        if isValidPos(app, app.player.row, app.player.col + 1):
            app.player.col += 1
            moveRobots(app)
    if event.key == "Left":
        if isValidPos(app, app.player.row, app.player.col - 1):
            app.player.col -= 1
            moveRobots(app)
    if event.key == "t":
        app.visualizeBFS = not app.visualizeBFS
    if event.key == "r":
        initializeLevel1(app)
    if event.key == "q":
        switchScreen(app, "levelSelectScreen")

# the timerFired function for the first level
def level1_timerFired(app):
    scalePlayerImage(app)
    scaleRobotImage(app)
    if checkForWin(app):
        loadWin(app)

# the redrawAll function for the first level
def level1_redrawAll(app, canvas):
    drawLevel1Background(app, canvas)
    drawLevel1Text(app, canvas)
    drawGrid(app, canvas)
    drawBFSPath(app, canvas)
    drawPlayer(app, canvas)
    drawRobots(app, canvas)
    drawExit(app, canvas)



# draws the background for the second level
def drawLevel2Background(app, canvas):
    canvas.create_rectangle(0, 0, app.width, app.height, fill = "aqua")

# draws the text for the second level
def drawLevel2Text(app, canvas):
    canvas.create_text(app.width / 2, app.height / 14,
        text = "Level 2", fill = "red", font = "Arial 50 bold")

# the keyPressed function for the second level
def level2_keyPressed(app, event):
    if event.key == "m":
        moveRobots(app)
    if event.key == "Up":
        if isValidPos(app, app.player.row - 1, app.player.col):
            app.player.row -= 1
            moveRobots(app)
    if event.key == "Down":
        if isValidPos(app, app.player.row + 1, app.player.col):
            app.player.row += 1
            moveRobots(app)
    if event.key == "Right":
        if isValidPos(app, app.player.row, app.player.col + 1):
            app.player.col += 1
            moveRobots(app)
    if event.key == "Left":
        if isValidPos(app, app.player.row, app.player.col - 1):
            app.player.col -= 1
            moveRobots(app)
    if event.key == "t":
        app.visualizeBFS = not app.visualizeBFS
    if event.key == "r":
        initializeLevel2(app)
    if event.key == "q":
        switchScreen(app, "levelSelectScreen")

# the timerFired function for the second level
def level2_timerFired(app):
    scalePlayerImage(app)
    scaleRobotImage(app)
    if checkForWin(app):
        loadWin(app)

# the redrawAll function for the second level
def level2_redrawAll(app, canvas):
    drawLevel2Background(app, canvas)
    drawLevel2Text(app, canvas)
    drawGrid(app, canvas)
    drawBFSPath(app, canvas)
    drawPlayer(app, canvas)
    drawRobots(app, canvas)
    drawExit(app, canvas)



# draws the background for the third level
def drawLevel3Background(app, canvas):
    canvas.create_rectangle(0, 0, app.width, app.height, fill = "aqua")

# draws the text for the third level
def drawLevel3Text(app, canvas):
    canvas.create_text(app.width / 2, app.height / 14,
        text = "Level 3", fill = "red", font = "Arial 50 bold")

# the keyPressed function for the third level
def level3_keyPressed(app, event):
    if event.key == "m":
        moveRobots(app)
    if event.key == "Up":
        if isValidPos(app, app.player.row - 1, app.player.col):
            app.player.row -= 1
            moveRobots(app)
    if event.key == "Down":
        if isValidPos(app, app.player.row + 1, app.player.col):
            app.player.row += 1
            moveRobots(app)
    if event.key == "Right":
        if isValidPos(app, app.player.row, app.player.col + 1):
            app.player.col += 1
            moveRobots(app)
    if event.key == "Left":
        if isValidPos(app, app.player.row, app.player.col - 1):
            app.player.col -= 1
            moveRobots(app)
    if event.key == "t":
        app.visualizeBFS = not app.visualizeBFS
    if event.key == "r":
        initializeLevel3(app)
    if event.key == "q":
        switchScreen(app, "levelSelectScreen")

# the timerFired function for the third level
def level3_timerFired(app):
    scalePlayerImage(app)
    scaleRobotImage(app)
    checkGridButtonPresses(app)
    if checkForWin(app):
        loadWin(app)

# the redrawAll function for the third level
def level3_redrawAll(app, canvas):
    drawLevel3Background(app, canvas)
    drawLevel3Text(app, canvas)
    drawGrid(app, canvas)
    drawBFSPath(app, canvas)
    drawGridButtons(app, canvas)
    drawPlayer(app, canvas)
    drawRobots(app, canvas)
    drawExit(app, canvas)



# draws the background for the fourth level
def drawLevel4Background(app, canvas):
    canvas.create_rectangle(0, 0, app.width, app.height, fill = "aqua")

# draws the text for the fourth level
def drawLevel4Text(app, canvas):
    canvas.create_text(app.width / 2, app.height / 14,
        text = "Level 4", fill = "red", font = "Arial 50 bold")

# the keyPressed function for the fourth level
def level4_keyPressed(app, event):
    if event.key == "m":
        moveRobots(app)
    if event.key == "Up":
        if isValidPos(app, app.player.row - 1, app.player.col):
            app.player.row -= 1
            moveRobots(app)
            app.justTeleported = False
    if event.key == "Down":
        if isValidPos(app, app.player.row + 1, app.player.col):
            app.player.row += 1
            moveRobots(app)
            app.justTeleported = False
    if event.key == "Right":
        if isValidPos(app, app.player.row, app.player.col + 1):
            app.player.col += 1
            moveRobots(app)
            app.justTeleported = False
    if event.key == "Left":
        if isValidPos(app, app.player.row, app.player.col - 1):
            app.player.col -= 1
            moveRobots(app)
            app.justTeleported = False
    if event.key == "t":
        app.visualizeBFS = not app.visualizeBFS
    if event.key == "r":
        initializeLevel4(app)
    if event.key == "q":
        switchScreen(app, "levelSelectScreen")

# the timerFired function for the fourth level
def level4_timerFired(app):
    scalePlayerImage(app)
    scaleRobotImage(app)
    checkGridButtonPresses(app)
    if not app.justTeleported:
        checkTeleportation(app)
    if checkForWin(app):
        loadWin(app)
    animateTeleporters(app)

# the redrawAll function for the fourth level
def level4_redrawAll(app, canvas):
    drawLevel4Background(app, canvas)
    drawLevel4Text(app, canvas)
    drawGrid(app, canvas)
    drawBFSPath(app, canvas)
    drawGridButtons(app, canvas)
    drawTeleporters(app, canvas)
    drawPlayer(app, canvas)
    drawRobots(app, canvas)
    drawExit(app, canvas)



# draws the background for the fifth level
def drawLevel5Background(app, canvas):
    canvas.create_rectangle(0, 0, app.width, app.height, fill = "aqua")

# draws the text for the fifth level
def drawLevel5Text(app, canvas):
    canvas.create_text(app.width / 2, app.height / 14,
        text = "Level 5", fill = "red", font = "Arial 50 bold")

# the keyPressed function for the fifth level
def level5_keyPressed(app, event):
    moved = False
    if event.key == "m":
        moveRobots(app)
    if event.key == "Up":
        if isValidPos(app, app.player.row - 1, app.player.col):
            app.player.row -= 1
            moveRobots(app)
            moved = True
    if event.key == "Down":
        if isValidPos(app, app.player.row + 1, app.player.col):
            app.player.row += 1
            moveRobots(app)
            moved = True
    if event.key == "Right":
        if isValidPos(app, app.player.row, app.player.col + 1):
            app.player.col += 1
            moveRobots(app)
            moved = True
    if event.key == "Left":
        if isValidPos(app, app.player.row, app.player.col - 1):
            app.player.col -= 1
            moveRobots(app)
            moved = True
    if moved:
        app.justTeleported = False
    if event.key == "t":
        app.visualizeBFS = not app.visualizeBFS
    if event.key == "r":
        initializeLevel5(app)
    if event.key == "q":
        switchScreen(app, "levelSelectScreen")

# the timerFired function for the fifth level
def level5_timerFired(app):
    scalePlayerImage(app)
    scaleRobotImage(app)
    scaleBomberRobotImage(app)
    checkGridButtonPresses(app)
    if not app.justTeleported:
        checkTeleportation(app)
    if checkForWin(app):
        loadWin(app)
    animateTeleporters(app)
    animateMines(app)
    checkMines(app)

# the redrawAll function for the fifth level
def level5_redrawAll(app, canvas):
    drawLevel5Background(app, canvas)
    drawLevel5Text(app, canvas)
    drawGrid(app, canvas)
    drawBFSPath(app, canvas)
    drawGridButtons(app, canvas)
    drawTeleporters(app, canvas)
    drawMines(app, canvas)
    drawPlayer(app, canvas)
    drawRobots(app, canvas)
    drawBomberRobots(app, canvas)
    drawExit(app, canvas)



# draws the background for the sixth level
def drawLevel6Background(app, canvas):
    canvas.create_rectangle(0, 0, app.width, app.height, fill = "aqua")

# draws the text for the sixth level
def drawLevel6Text(app, canvas):
    canvas.create_text(app.width / 2, app.height / 14,
        text = "Level 6", fill = "red", font = "Arial 50 bold")

# the keyPressed function for the sixth level
def level6_keyPressed(app, event):
    moved = False
    if event.key == "m":
        moveRobots(app)
    if event.key == "Up":
        if isValidPos(app, app.player.row - 1, app.player.col):
            app.player.row -= 1
            moveRobots(app)
            moved = True
    if event.key == "Down":
        if isValidPos(app, app.player.row + 1, app.player.col):
            app.player.row += 1
            moveRobots(app)
            moved = True
    if event.key == "Right":
        if isValidPos(app, app.player.row, app.player.col + 1):
            app.player.col += 1
            moveRobots(app)
            moved = True
    if event.key == "Left":
        if isValidPos(app, app.player.row, app.player.col - 1):
            app.player.col -= 1
            moveRobots(app)
            moved = True
    if moved:
        app.justTeleported = False
        wasShield = False
        if app.shieldTicks > 0:
            wasShield = True
            app.shieldTicks -= 1
        if wasShield and app.shieldTicks == 0 and app.sfx:
            app.shieldBreakSound.start(0, 0.5)
    if event.key == "t":
        app.visualizeBFS = not app.visualizeBFS
    if event.key == "r":
        initializeLevel6(app)
    if event.key == "q":
        switchScreen(app, "levelSelectScreen")

# the timerFired function for the sixth level
def level6_timerFired(app):
    scalePlayerImage(app)
    scaleRobotImage(app)
    scaleBomberRobotImage(app)
    scaleShieldImage(app)
    checkGridButtonPresses(app)
    if not app.justTeleported:
        checkTeleportation(app)
    if checkForWin(app):
        loadWin(app)
    animateTeleporters(app)
    animateMines(app)
    animateShield(app)
    checkMines(app)
    checkItems(app)

# the redrawAll function for the sixth level
def level6_redrawAll(app, canvas):
    drawLevel6Background(app, canvas)
    drawLevel6Text(app, canvas)
    drawGrid(app, canvas)
    drawBFSPath(app, canvas)
    drawGridButtons(app, canvas)
    drawTeleporters(app, canvas)
    drawMines(app, canvas)
    drawItems(app, canvas)
    drawPlayerShield(app, canvas)
    drawPlayer(app, canvas)
    drawRobots(app, canvas)
    drawBomberRobots(app, canvas)
    drawExit(app, canvas)



# draws the background for the game over screen
def drawGameOverScreenBackground(app, canvas):
    canvas.create_rectangle(0, 0, app.width, app.height, fill = "black")

# draws the text for the game over screen
def drawGameOverScreenText(app, canvas):
    canvas.create_text(app.width / 2, app.height / 8,
        text = "Game Over", fill = "orange", font = "Arial 50 bold")
    canvas.create_text(app.width / 2, app.height / 4,
        text = ("You were caught!" if app.loseType == "caught" else "You were blown up by a mine!"), fill = "red", font = "Arial 25 bold")

# the mousePressed function for the game over screen
def gameOverScreen_mousePressed(app, event):
    clickEvent = checkForButtonPress(app, event.x, event.y)
    if clickEvent == "retry":
        switchScreen(app, app.loseLevel)
    elif clickEvent == "titleScreen":
        switchScreen(app, "titleScreen")
    elif clickEvent == "levelSelect":
        switchScreen(app, "levelSelectScreen")

# the mouseMoved function for the game over screen
def gameOverScreen_mouseMoved(app, event):
    checkForButtonHover(app, event.x, event.y)

# the redrawAll function for the game over screen
def gameOverScreen_redrawAll(app, canvas):
    drawGameOverScreenBackground(app, canvas)
    drawGameOverScreenText(app, canvas)
    drawButtons(app, canvas)



# draws the background for the win screen
def drawWinScreenBackground(app, canvas):
    canvas.create_rectangle(0, 0, app.width, app.height, fill = "black")

# draws the text for the win screen
def drawWinScreenText(app, canvas):
    canvas.create_text(app.width / 2, app.height / 8,
        text = "You Won", fill = "orange", font = "Arial 50 bold")
    canvas.create_text(app.width / 2, app.height / 4,
        text = "You escaped!", fill = "green", font = "Arial 25 bold")

# the mousePressed function for the win screen
def winScreen_mousePressed(app, event):
    clickEvent = checkForButtonPress(app, event.x, event.y)
    if clickEvent == "playAgain":
        switchScreen(app, app.winLevel)
    elif clickEvent == "titleScreen":
        switchScreen(app, "titleScreen")
    elif clickEvent == "levelSelect":
        switchScreen(app, "levelSelectScreen")

# the mouseMoved function for the win screen
def winScreen_mouseMoved(app, event):
    checkForButtonHover(app, event.x, event.y)

# the redrawAll function for the win screen
def winScreen_redrawAll(app, canvas):
    drawWinScreenBackground(app, canvas)
    drawWinScreenText(app, canvas)
    drawButtons(app, canvas)



def main():
    runApp(width = 850, height = 700)



if __name__ == '__main__':
    main()