#!/usr/bin/env python
""" 
snake.py

Yabas: Yet Another Blocky Amateur Snake.

Copyright (C) 2009 Peter Somerville

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program.  If not, see <http://www.gnu.org/licenses/>.

requires - python 2.x, pygame.

not overly pythonic - re-written to use getters and mutators
since I was doing Java courses at the time and trying to get
into that mind set.

all screen output is drawn using pygame, no images etc
the sounds were recorded by me; snaking & eating...

"""

__author__ = "Peter Somerville"
__email__ = "peterwsomerville@gmail.com"
__version__ = "1.0.1"
__date__ = "21/5/12"


import pygame
import random
import cPickle
import time
import os
from sys import exit

class Snake(pygame.sprite.Sprite):
    """ Sprite for player snake
        attributes:
            screen, image, rect, body, length, dir, 
            speed, score, alive, wrap
        methods:
            update()
            checkKeys()
            checkLevel()
            sortBody()
            move()
            checkBounds()
            checkCollision()
            moreScore()
            moreLength()
            getScore()
            getLength()
            setWrap()
        """
        
    def __init__(self,screen):
        pygame.sprite.Sprite.__init__(self)
        self.screen = screen
        self.image = pygame.Surface((16,16))
        self.image.fill((0,255,0))
        self.image = self.image.convert()
        self.rect = self.image.get_rect()
        self.rect.center = (screen.get_width()/2,screen.get_height()/2)
        self.body = []
        self.length = 3
        self.dir = 0
        self.speed = 3
        self.score = 0
        self.alive = True # snake not dead
        self.wrap = False # old or new snake
        if pygame.mixer is not None:
            self.sndSnake = pygame.mixer.Sound("snake.wav")
        else:
            print "no sound"
            self.sndSnake = None
            
    def update(self):
        """ each frame, call each method in turn """
        self.checkKeys()
        self.checkLevel()
        self.sortBody()
        self.move()
        self.checkBounds()
        self.checkCollision()

    def checkLevel(self):
        """ compare score to constants and set 
            speed accordingly """
        if self.score > 19:
            self.speed = 4
        if self.score > 39:
            self.speed = 5
        if self.score > 59:
            self.speed = 6
        if self.score > 79:
            self.speed = 7
        if self.score > 99:
            self.speed = 8
        if self.score > 119:
            self.speed = 9
        if self.score > 139:
            self.speed = 10

    def draw(self,screen):
        """ blit head then each part of body """
        screen.blit(self.image,self.rect.center)
        for b in self.body:
            screen.fill((0,255,0),(b[0],b[1],16,16))
                    
    def sortBody(self):
        """ put head into body then chop list to body's length"""
        self.body.insert(0, (self.rect.centerx,self.rect.centery))
        self.body = self.body[:self.length]
        
    def checkBounds(self):
        """ either kill snake or wrap-around screen according to
            game type """
        if not self.wrap: # playing old snake, kill on boundary
            if self.rect.centerx not in xrange(0,self.screen.get_width()-8):
                self.alive = False
            if self.rect.centery not in xrange(0,self.screen.get_height()-8):
                self.alive = False
        else: # playing new snake, wrap around
            if self.rect.x < 0:
                self.rect.x = self.screen.get_width()
            if self.rect.x > self.screen.get_width():
                self.rect.x = 0
            if self.rect.y < 0 :
                self.rect.y = self.screen.get_height()
            if self.rect.y > self.screen.get_height():
                self.rect.y = 0

    def checkCollision(self):
        """ see if snake has run into itself, if so kill snake """
        for b in self.body:
            if b == self.rect.center:
                self.alive = False
                
    def move(self):
        """ check direction then move at speed """
        if self.dir == 0:
            self.rect.y -= self.speed
        if self.dir == 90:
            self.rect.x -= self.speed
        if self.dir == 180:
            self.rect.y += self.speed
        if self.dir == 270:
            self.rect.x += self.speed

    def checkKeys(self):
        """ check pressed keys and adjust dir accordingly """
        keys = pygame.key.get_pressed()
        if keys[pygame.K_UP]:
            self.dir = 0
        if keys[pygame.K_LEFT]:
            self.dir = 90
        if keys[pygame.K_DOWN]:
            self.dir = 180
        if keys[pygame.K_RIGHT]:
            self.dir = 270

    def moreScore(self,score):
        """ add value of fruit to snake's score """
        self.score += score

    def getScore(self):
        return self.score

    def getSpeed(self):
        return int(self.speed)
    
    def getAlive(self):
        return self.alive
        
    def getSound(self):
        return self.sndSnake
    
    def playSound(self, playSounds):
        if playSounds:
            self.sndSnake.play(-1)
        else:
            self.sndSnake.stop()
            
    def moreLength(self):
        """ increase length of snake by 1 """
        self.length +=1

    def setWrap(self,wrap):
        """ wrap => new snake, not wrap => old snake  """
        self.wrap = wrap


class Item(pygame.sprite.Sprite):
    """ class for thing snake eats 
    
        attributes:
            screen, image, rect, duration, timeLeft, worth, Label
            
        methods:
            init(), reset(), update(), assesWorth()
            """
    def __init__(self,screen):

        pygame.sprite.Sprite.__init__(self)
        self.screen = screen
        self.image = pygame.Surface((16,16)).convert()
        self.image.fill((255,0,0))
        self.rect = self.image.get_rect()
        self.rect.centerx = random.randint(16,self.screen.get_width()-16)
        self.rect.centery = random.randint(16,self.screen.get_height()-16)
        self.duration = random.randint(90,300)
        self.timeLeft = self.duration
        self.worth = self.assesWorth()
        if pygame.mixer:
            self.sndMunch = pygame.mixer.Sound("munch.wav")
        else:
            self.sndMunch = None
            
        self.label = Label(14)
        self.label.setColour((255,255,255))
        self.label.setCenter(self.rect.center)
        self.label.setText("%s"% str(self.timeLeft/10))
        self.label.update()
        
    def reset(self):
        """ all new random values for fruit after it expires or is eaten """
        self.rect.centerx = random.randint(16,self.screen.get_width()-16)
        self.rect.centery = random.randint(16,self.screen.get_height()-16)
        self.duration = random.randint(90,300)
        self.timeLeft = self.duration
        self.worth = self.assesWorth()
        self.label.setCenter(self.rect.center)
        self.label.setColour((255,255,255))
    
    def draw(self,screen):
        screen.blit(self.image, self.rect.center)
        screen.blit(self.label.image, self.label.rect.center)
        
    def update(self,snake,playSound):
        self.timeLeft -=1 # reduce lifespan
        
        # if snake hits fruit
        if snake.rect.colliderect(self.rect):
            if playSound:
                self.sndMunch.play()
            snake.moreScore(self.worth) # add fruit's score to snake's score
            snake.moreLength() # increase snake's length
            self.reset() # new fruit needed
        
        
        self.label.setText("%s"% str(self.timeLeft/10)) # set label to new lifespan    
        self.label.update()
        
        # if near to expiring change label to red text
        if self.timeLeft < 100:
            self.label.setColour((0,0,0))
        # if expired reset
        if self.timeLeft < 0:
            self.reset()
        
    def assesWorth(self):
        """ calculate and return fruit's worth according to how long it 
            be on screen """
        worth = 0
        if self.duration in xrange(200,300):
            worth = 1
        if self.duration in xrange(150,199):
            worth = 2
        if self.duration in xrange(90,149):
            worth = 3
        return worth
            

class ScoreTable():
    """ class to load and display high scores
        loads a pickled list of tuples
        generates labels
        checks users score against current high scores
            if bigger score than bottom score
                add to list
                sort list
                remove last entry
        write data to file
        persistence is key
        """                
    def __init__(self):
        # new scoreboard game object
        self.highScores = self.loadData() # load pickled list
        self.labels = self.getLabels() # get labels from list

    def update(self):
        # make sure all is current
        self.highScores = self.loadData()
        self.labels = self.getLabels()
              
                    
    def checkScore(self,score,level):
        # is score better than worst?
        if score > self.highScores[-1][0]:
            # yes, get name
            name = getName(score,level)
            # add details to list
            self.highScores.append((score,name,level,time.strftime("%d/%m %H:%M")))
            self.highScores.sort()
            self.highScores.reverse()
            self.highScores = self.highScores[:9] # just the top ten
            self.writeData() # new list to file
            self.update() # new details in scoreTable
        
    def getHighScore(self):
        return self.highScores[0][0]
    
    def getLabels(self):
        """ generate labels and place in group """
        
        labels = pygame.sprite.Group()
        lineCount = 2 # start a bit down the screen
        for score in self.highScores:
            tmpLabel = Label(25)
            tmpLabel.setText("%d - %s - %d - %s"% (score[0], score[1], score[2], score[3]))
            tmpLabel.setColour((255,255,0))
            tmpLabel.setCenter((160,30*lineCount))
            labels.add(tmpLabel) # add this label
            lineCount+=1 # move down screen
        return labels               
    
    def writeData(self):
        # open scores file and write pickled list
        fileObj = open("scores.p", "w")
        cPickle.dump(self.highScores,fileObj)
        fileObj.close()

    def loadData(self):
        # open file and get pickled list
        fileObj = open("scores.p")
        data = cPickle.load(fileObj)
        fileObj.close()
        return data

class Label(pygame.sprite.Sprite):
    """ class for working with text and displaying it
        methods 
            __init__(fontSize)
            update()
            setText()
            setCenter()
            setColour
    """
    
    def __init__(self,size):
        """ new label object...
        font, text, center, color"""
        # label is a sprite
        pygame.sprite.Sprite.__init__(self)
        # initial values
        self.font = pygame.font.Font(None, size)
        self.colour = (255,255,255)
        self.text = ""
        self.center = (-100,-100)
        self.update()
    
    def update(self):
        """ update label values, render text """     
        self.image = self.font.render(self.text, 1, self.colour)
        self.rect = self.image.get_rect()
        self.rect.center = self.center

    def setText(self,words):
        """ give label new text """
        self.text = words
        self.update()
    def setColour(self,colour):
        """ give text new colour """
        self.colour = colour
        self.update()
    def setCenter(self,center):
        """ give label new center """
        self.center = center
        self.update()
    

def main():
    """main function
        call menu to determine game mode
        play game
        or exit """
    os.environ["SDL_VIDEO_CENTERED"] = "1"
    pygame.init()
    pygame.mixer.init()  
    
    playing = True
    score = 0
    while playing:
     
        playing, wrap = menu(score)
        if playing:
            score = game(wrap)

def menu(score):
    """ function to display game style menu and return choice
        user can also display high scores """
    # display     
    screen = pygame.display.set_mode((320,320))
    pygame.display.set_caption("YABAS...")
    # background
    bg = pygame.Surface(screen.get_size())
    bg.fill((0,0,0))
    scoreTable = ScoreTable()
    pygame.mouse.set_visible(False) # hide mouse 
    
    # text to be displayed in menu
    menu = (
    "Yet Another Blocky,",
    "Amateur Snake",
    "",
    "a - old snake",
    "b - new snake",
    "c - high scores",
    "d - instructions",
    "",
    "last score %d"%score,
    "high score %d"%scoreTable.getHighScore()
    )

    # put text into label group
    menuLabels = pygame.sprite.Group()
    lineCount = 1 # start near the top
    for line in menu:
            tempLabel = Label(30)
            tempLabel.setText(line)
            tempLabel.setColour((255,255,0))
            tempLabel.setCenter((160,30*lineCount))
            menuLabels.add(tempLabel) # add this line's label
            lineCount +=1 # move down a bit
            
    clock = pygame.time.Clock() # new clock
    
    wrap = True # game type option
    
    keepGoing = True # main loop control
    while keepGoing:
        clock.tick(30) # regulate frame rate
        screen.blit(bg,(0,0)) # clear screen
        
        # check for user input, set game mode and/or exit menu
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                exit()
            if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                keepGoing = False
                playing = False
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_a:
                    keepGoing = False
                    playing = True
                    wrap = False
                if event.key == pygame.K_b:
                    keepGoing = False
                    playing = True
                if event.key == pygame.K_c:
                    highScores(scoreTable)
                if event.key == pygame.K_d:
                    instructions()
        #render and draw menu
        menuLabels.update()
        menuLabels.draw(screen)
        pygame.display.flip()
    return (playing,wrap)

     
def game(wrap):
    """ game function, passed wrap to determine game style """
    
    screen = pygame.display.set_mode((320,320)) # new screen
    if wrap: # check game style
        pygame.display.set_caption("YABAS...New Snake")
    else:
        pygame.display.set_caption("YABAS...Old Snake")

    # snake and two fruits
    snake = Snake(screen)
    snake.setWrap(wrap)
       
    # sprite groups for updating and displaying fruits and their labels
    fruits = pygame.sprite.Group(Item(screen),Item(screen))
    
    # a score table for checking final score against
    scoreTable = ScoreTable()
    
    # labels for score, level and game over
    # added to another sprite.Group()
    lblScore = Label(25)
    lblScore.setCenter((60,15))
    lblLevel = Label(25)
    lblLevel.setCenter((200, 15))
    lblGameOver = Label(50)
    lblGameOver.setCenter((screen.get_width()/2,screen.get_height()/2))
    lblGameOver.setColour((0,255,255))
    mainLabels = pygame.sprite.Group(lblScore,lblGameOver,lblLevel)

    # new black background
    bg = pygame.Surface(screen.get_size())
    bg.fill((0,0,0)) # none,none,none more black

    # clock for regulating frames per second
    clock = pygame.time.Clock()

    # main loop control
    keepGoing = True
    paused = False
    
    # if sound enabled, set playSounds
    if snake.getSound() != None:
        playSounds = True
    else:
        playSounds = False
    
    snake.playSound(playSounds)  
    while keepGoing:
        clock.tick(30) # limit to 30 fps
        screen.blit(bg,(0,0)) # clear background
        pygame.mouse.set_visible(False) # hide mouse

        # check for user quit and set main loop control false
        for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    exit()
                if event.type == pygame.KEYDOWN: 
                    if event.key == pygame.K_ESCAPE:
                        keepGoing = False
                        snake.playSound(False)
                        playSounds = False
                    if event.key == pygame.K_s:
                        playSounds = not playSounds
                        snake.playSound(playSounds)
                    if event.key == pygame.K_p:
                        paused = not paused
                        snake.playSound(playSounds)
                       
                        
        if paused:
            lblGameOver.setText("Paused!!")
            mainLabels.draw(screen)
            snake.playSound(False)
            pygame.display.flip()
        else:               
            lblGameOver.setText("")          
      
            if not snake.getAlive():
                playSounds = False
                snake.playSound(playSounds)
                lblGameOver.setText("Game Over !!") # tell user
                keepGoing = False # stop main loop

            # update sprites that may have changed state
            snake.update()
            fruits.update(snake,playSounds)
        
            # draw snake
            snake.draw(screen)

            # draw each fruit and its label
            for fruit in fruits:
                fruit.draw(screen)
            # update text on main labels and draw 
            lblScore.setText("Score: %d"%snake.getScore())
            lblLevel.setText("Level: %d"%(snake.getSpeed()-2))
            mainLabels.update()
            mainLabels.draw(screen)
            pygame.display.flip()

    pygame.time.wait(1000) # snake has died, wait a second
    scoreTable.checkScore(snake.getScore(),snake.getSpeed()-2) # check score against score board
    
    return snake.getScore() # return game score

def instructions():
    screen = pygame.display.set_mode((320,320))
    pygame.display.set_caption("YABAS - Instructions")
    bg = pygame.Surface(screen.get_size())
    bg.fill((0,0,0))
    
    clock = pygame.time.Clock()
    pygame.mouse.set_visible(False) # hide mouse
    
    text = (
    "What? Are you kidding?",
    "You don't know",
    "how to play snake?",
    "Arrow keys to move",
    "(s) to toggle sound",
    "(p) to pause",
    "",
    "a pedros genuine copy 09.",
    "games that make you want",
    "to shout their name"
    )
    
    # put text into label group
    insLabels = pygame.sprite.Group()
    lineCount = 1 # start near the top
    for line in text:
            tempLabel = Label(30)
            tempLabel.setText(line)
            tempLabel.setColour((255,255,0))
            tempLabel.setCenter((160,30*lineCount))
            insLabels.add(tempLabel) # add this line's label
            lineCount +=1 # move down a bit
    
    showIns = True
    while showIns:
        clock.tick(30) # 30 fps
        screen.blit(bg,(0,0)) # clear screen
        

        # if quit or click, back to menu
        for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    exit()
                if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                    showIns = False
                    pygame.display.set_caption("YABAS...")
                if event.type == pygame.MOUSEBUTTONDOWN:
                    showIns = False
                    pygame.display.set_caption("YABAS...")
        
        # labels from score board, render then draw
        insLabels.update()
        insLabels.draw(screen)
        
        pygame.display.flip() # display frame
        
def highScores(scoreTable):
    """ function to display high score table
        data loaded from pickled list """
    # set up display and create new background    
    screen = pygame.display.set_mode((320,320))
    pygame.display.set_caption("YABAS - High Scores")
    bg = pygame.Surface(screen.get_size())
    bg.fill((0,0,0))

    clock = pygame.time.Clock() # clock object    
    
    # table heading
    lblHeadings = Label(25)
    lblHeadings.setText("Score - Player - Level - Time")
    lblHeadings.setCenter((160,15))
    heading = pygame.sprite.Group(lblHeadings)
    
    pygame.mouse.set_visible(False) # hide mouse
    
    showHS = True # main loop control
    while showHS:
        clock.tick(30) # 30 fps
        screen.blit(bg,(0,0)) # clear screen
        
        # if quit or click, back to menu
        for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    exit()
                if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                    showHS = False
                    pygame.display.set_caption("YABAS...")
                if event.type == pygame.MOUSEBUTTONDOWN:
                    showHS = False
                    pygame.display.set_caption("YABAS...")
        
        #render heading and draw
        heading.update()
        heading.draw(screen)
        # labels from score board, render then draw
        scoreTable.labels.update()
        scoreTable.labels.draw(screen)
        pygame.display.flip() # display frame

                
def getName(score,level):
    """ function to get high scoring user's name """
    # display
    screen = pygame.display.set_mode((320,320))
    pygame.display.set_caption("High Score - Enter Name")
    # background
    bg = pygame.Surface(screen.get_size())
    bg.fill((0,0,0))
    # clock
    clock = pygame.time.Clock()
    # labels and value-ising
    lblScore = Label(30)
    lblScore.setText("New High Score: %d. Level %d"%(score,level))
    lblScore.setCenter((160,45))
    lblScore.setColour((255,255,0))
    lblPrompt = Label(35)
    lblPrompt.setText("Enter Your Name...")
    lblPrompt.setCenter((160,95))
    lblPrompt.setColour((255,255,0))
    lblName = Label(35)
    lblName.setCenter((160,150))
    lblName.setColour((255,255,0))
    labels = pygame.sprite.Group(lblScore,lblPrompt,lblName)
    # main loop control and new name string
    gettingName = True
    name = u""
    
    while gettingName:
        clock.tick(30)
        screen.blit(bg,(0,0))
        # check user input
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                exit()
            # if typing add key to name string    
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_BACKSPACE:
                    name = name[:-1] # last char remove
                elif event.key == pygame.K_ESCAPE:
                    gettingName = False
                    name = "anon"
                elif event.key == pygame.K_RETURN:
                    gettingName = False # name finished
                else:
                    name = name + event.unicode
    
        # give name label current name value
        lblName.setText(name)    
        # update and display labels
        labels.update()
        labels.draw(screen)        
        pygame.display.flip() # display frame
            
    return name # final name for user

if __name__ == "__main__":
    main()