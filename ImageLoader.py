
import random
from bing_image_downloader import downloader
import cv2 as cv
import os
import numpy as np
from PIL import Image, ImageDraw

from threading import Thread
from threading import active_count

import time

import pygame
pygame.init()

win = pygame.display.set_mode((1920,1080), pygame.NOFRAME)
clock = pygame.time.Clock()

# -----------------------------------------variables-----------------------------------------
characterFile = "Input/characters.txt"
queueFile = "Queue/queue.txt"
downloadedImagesFile = "Input"
font_name = pygame.font.match_font('Arial')

numImagesDownloaded = 5

threshold1 = 60
threshold2 = 138
currentPos = [940,4876]
videoLength = 20
endLength = 2

fps = 30
widthMargin = 20
canvasWidth = 980
canvasHeight = 1820
canvasOffset = (50,50)
rectRadius = 3
shortWidth = 1080
shortHeight = 1920
pixelSteps = 1000
searchPercent = 0.1

colours = [
(255,174,173),
(255,214,166),
(253,255,182),
(203,255,191),
(155,246,255),
(160,196,255)]
canvasColour = (255,255,255)
inkColour = (0,0,0)
fillColour = (0,255,0)

hourOffset = 12

h = 1080/2+1
w = int(h * 1080/1920)+1

characterReady = False
selectingCharacter = False
character = ""
oldCharacter = ""
oldCharacterImages = []

def loadNewImages():
	global characterReady, character, characterImages
	characterReady = False

	# -----------------------------------------pick a character-----------------------------------------
	with open(characterFile, "r") as f:
		content = f.read()

	characters = content.split("\n")

	character = random.choice(characters)

	# -----------------------------------------download images-----------------------------------------
	downloader.download(character, limit = numImagesDownloaded, output_dir=f"{downloadedImagesFile}/pass1", adult_filter_off=True, force_replace = True, timeout = 60, filter = "transparent")
	downloader.download(character, limit = numImagesDownloaded, output_dir=f"{downloadedImagesFile}/pass2", adult_filter_off=True, force_replace = True, timeout = 60)

	characterImages = [f"Input/pass1/{character}/{i}" for i in os.listdir(f"Input/pass1/{character}")]

	for i in os.listdir(f"Input/pass2/{character}"):
		characterImages.append(f"Input/pass2/{character}/{i}")

	n = 0

	for sourceFile in characterImages:

		img = Image.open(sourceFile)

		img = img.convert("RGBA")   # it had mode P after DL it from OP
		if img.mode in ('RGBA', 'LA'):
			background = Image.new(img.mode[:-1], img.size, fillColour)
			background.paste(img, img.split()[-1]) # omit transparency
			img = background

		img.convert("RGB").save("Images/save.png")

		# LOAD AND RESIZE IMAGE
		img = cv.imread("Images/save.png")
		imageDimensions = img.shape
		drawingWidth = canvasWidth*2-widthMargin*4
		drawingHeight = int(drawingWidth*imageDimensions[0]/imageDimensions[1])

		offset = [widthMargin*2,canvasHeight-drawingHeight/2] #calculate offset for later

		# if the height is too big make the hight the limit instead of the width
		if drawingHeight > canvasHeight*2-widthMargin*4:
			drawingHeight = canvasHeight*2-widthMargin*4
			drawingWidth = int(drawingHeight*imageDimensions[1]/imageDimensions[0])

			offset = [canvasWidth-drawingWidth/2,widthMargin*2]

		img = cv.resize(img, (drawingWidth, drawingHeight))

		print(drawingWidth,drawingHeight)

		# create outline of image
		img = cv.Canny(img, threshold1, threshold2)

		bg = np.ones((1920*2,1080*2), dtype=np.uint8)*30

		x_end = img.shape[1]
		y_end = img.shape[0]

		bg[0:y_end,0:x_end] = img

		down_height = int(1080/2)
		down_width = int(down_height * 1080/1920)
		down_points = (down_width, down_height)
		resized_down = cv.resize(bg, down_points, interpolation= cv.INTER_AREA)

		cv.imwrite(f"images/canny{n}.png", resized_down)

		n += 1

	characterReady = True

def topleft_text(surf, text, size, x, y, colour):
		font = pygame.font.Font(font_name, size)
		text_surface = font.render(text, True, (colour))
		text_rect = text_surface.get_rect()
		text_rect.topleft = (x, y)
		surf.blit(text_surface, text_rect)

def draw():
	win.fill((0,0,0))
	
	if selectingCharacter == True:
		h = 1080/2+1
		w = int(h * 1080/1920)+1

		x = 0
		y = 0
		n = 0

		for image in images:
			win.blit(image, (x,y))

			n += 1
			x += w
			if n == 5:
				y += h
				x = 0

		topleft_text(win, oldCharacter, 30, w*5+10, 10, (255,255,255))
		topleft_text(win, "SKIP", 100, w*5+10, 100, (0,255,0))
		
	else:
		topleft_text(win, "LOADING", 300, 100, 300, (255,0,0))

	pygame.display.update()

t = Thread(target = loadNewImages)
t.start()

while True:
	clock.tick(30)

	for event in pygame.event.get():
		if event.type == pygame.QUIT:
			pygame.quit()

		if event.type == pygame.MOUSEBUTTONDOWN:
			if event.button == 1 and selectingCharacter:
				mousePos = pygame.mouse.get_pos()

				# select character
				if int(mousePos[0]/w) < 5:
					with open(queueFile, "a") as f:
						f.write(oldCharacterImages[int(mousePos[0]/w)+int(mousePos[1]/h)*5] + "\n")

					selectingCharacter = False

				elif mousePos[1] > 100 and mousePos[1] < 200:
					selectingCharacter = False


	# open new character when ready
	if characterReady and not selectingCharacter:
		oldCharacter = character
		oldCharacterImages = characterImages[:]
		images = [pygame.image.load(f"Images/canny{i}.png") for i in range(10)]
		selectingCharacter = True
		t = Thread(target = loadNewImages)
		t.start()
	
	draw()
