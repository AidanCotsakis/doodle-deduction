
import random
from bing_image_downloader import downloader
import cv2 as cv
import numpy as np
from PIL import Image, ImageDraw
import os
from moviepy.editor import CompositeAudioClip, AudioFileClip
import moviepy.video.io.ImageSequenceClip
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
from datetime import datetime, timedelta

# -----------------------------------------variables-----------------------------------------
characterFile = "Input/characters.txt"
downloadedImagesFile = "Input"
queueFile = "Queue/queue.txt"

numImagesDownloaded = 3

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

dateOrgin = datetime(2023,9,2,8,0,0)
hourOffset = 12

canvasImage = Image.open("Images/canvas.png")

months = {
	1:"Jan",
	2:"Feb",
	3:"Mar",
	4:"Apr",
	5:"May",
	6:"Jun",
	7:"Jul",
	8:"Aug",
	9:"Sep",
	10:"Oct",
	11:"Nov",
	12:"Dec"
}

videoTitle = "Can You Guess The Character Before The Drawing Is Finished?"

# numVideos = 10

def getNextQueue():
	with open(queueFile, "r") as f:
		content = f.read()

	content = content.split("\n")[:-1]

	if len(content) == 0:
		return None

	if len(content) != 1:
		with open(queueFile, "w") as f:
			f.write("\n".join(content[1:]) + "\n")
	else:
		with open(queueFile, "w") as f:
			f.write("")

	return content[0]

while True:
	
	print("Waiting for next queue")
	sourceFile = getNextQueue()
	while sourceFile == None:
		time.sleep(10)
		sourceFile = getNextQueue()
	print("Found next queue")

	# -----------------------------------------run bot-----------------------------------------
	# SETUP COLOUR
	f = open('Savedata/colourSave.txt', "r")
	contents = f.read()
	f.close()
	lastColour = int(contents)

	colourIndex = lastColour + 1
	if colourIndex >= len(colours):
		colourIndex = 0

	# FILL BACKGROUND OF PNG WITH SOLID COLOUR
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

	# CREATE AN ARRAY OF PIXLES
	print("Locating Pixels...")
	pixels = []

	currentPos = [currentPos[0] + offset[0], currentPos[1]+offset[1]]

	for y in range(drawingHeight):
		for x in range(drawingWidth):
			if img[y, x] == 255:
				pixels.append((x+offset[0],y+offset[1]))

	pixels.reverse()

	# GENERATE EACH FRAME OF THE VIDEO
	print("Generating Frames...")
	largeFrame = Image.new('RGB', (canvasWidth*2, canvasHeight*2), canvasColour)
	drawFrame = ImageDraw.Draw(largeFrame)

	targetFrameCount = videoLength*fps
	pixelSteps = int(len(pixels)/targetFrameCount)
	roughFrameCount = int(len(pixels)/pixelSteps)+1

	currentFrame = 0

	# RENDER BLANK FRAME FIRST
	newFrame = Image.new('RGB', (shortWidth, shortHeight), colours[colourIndex])
	newFrame.paste(canvasImage, (0,0), canvasImage)
	newFrame.save(f"Frames/frame{currentFrame}.png")
	currentFrame += 1

	searchRange = int(len(pixels)*searchPercent)

	while len(pixels) > 0:

		for i in range(pixelSteps):
			# locate closest pixel

			# generate search array
			if len(pixels) > searchRange:
				searchArray = pixels[:searchRange]
			else:
				searchArray = pixels[:]

			closestDistance = 10000000
			closestIndex = 0

			# Quick checks to see if neighboring pixels are in array
			if (currentPos[0],currentPos[1]+1) in searchArray:
				closestIndex = searchArray.index((currentPos[0],currentPos[1]+1))
			elif (currentPos[0]+1,currentPos[1]) in searchArray:
				closestIndex = searchArray.index((currentPos[0]+1,currentPos[1]))
			elif (currentPos[0]-1,currentPos[1]) in searchArray:
				closestIndex = searchArray.index((currentPos[0]-1,currentPos[1]))
			elif (currentPos[0],currentPos[1]-1) in searchArray:
				closestIndex = searchArray.index((currentPos[0],currentPos[1]-1))
			elif (currentPos[0]+1,currentPos[1]+1) in searchArray:
				closestIndex = searchArray.index((currentPos[0]+1,currentPos[1]+1))
			elif (currentPos[0]-1,currentPos[1]+1) in searchArray:
				closestIndex = searchArray.index((currentPos[0]-1,currentPos[1]+1))
			elif (currentPos[0]+1,currentPos[1]-1) in searchArray:
				closestIndex = searchArray.index((currentPos[0]+1,currentPos[1]-1))
			elif (currentPos[0]-1,currentPos[1]-1) in searchArray:
				closestIndex = searchArray.index((currentPos[0]-1,currentPos[1]-1))

			# deep check if no neighboring pixels are found
			else:
				for pixel in enumerate(searchArray):
					distance = pow((pixel[1][0]-currentPos[0]),2) + pow((pixel[1][1]-currentPos[1]),2)
					
					if distance <= closestDistance:
						closestDistance = distance
						closestIndex = pixel[0]

			currentPos = [pixels[closestIndex][0], pixels[closestIndex][1]]
			pixels.pop(closestIndex)

			drawFrame.rectangle((currentPos[0]-rectRadius, currentPos[1]-rectRadius, currentPos[0]+rectRadius, currentPos[1]+rectRadius), fill=inkColour)

			if len(pixels) == 0:
				break

		smallFrame = largeFrame.resize((canvasWidth, canvasHeight), resample=Image.Resampling.LANCZOS)

		newFrame = Image.new('RGB', (shortWidth, shortHeight), colours[colourIndex])
		newFrame.paste(canvasImage, (0,0), canvasImage)
		newFrame.paste(smallFrame, canvasOffset)

		newFrame.save(f"Frames/frame{currentFrame}.png")
		print(f"{currentFrame}/{roughFrameCount} {int(currentFrame/roughFrameCount*1000)/10}% / drawing {pixelSteps} pixels per frame with {len(pixels)} pixels left")

		currentFrame += 1

	print("Reading Frames...")

	f = open('Savedata/fileIndex.txt', "r")
	contents = f.read()
	f.close()
	fileIndex = int(contents)+1


	# COMBINE IMAGES TO MP4
	songs = os.listdir("Music/")
	song = random.choice(songs)

	image_files = []
	for i in range(currentFrame):
		image_files.append(f"Frames/frame{i}.png")

	for i in range(int(endLength*fps)):
		image_files.append(f"Frames/frame{currentFrame-1}.png")


	print("Combining Frames...")
	clip = moviepy.video.io.ImageSequenceClip.ImageSequenceClip(image_files, fps=fps)
	clip_duration = clip.duration

	audioclip = AudioFileClip(f"Music/{song}").set_duration(clip_duration)
	new_audioclip = CompositeAudioClip([audioclip])
	clip.audio = new_audioclip

	clip = clip.audio_fadeout(endLength)

	print("Writing Video...")
	clip.write_videofile(f'Output/output[{fileIndex}].mp4')

	# -----------------------------------------upload video-----------------------------------------
	with open("Savedata/timeOffset.txt", "r") as f:
		timeOffset = int(f.read())

	timeOffset += hourOffset
	scheduleDatetime = dateOrgin + timedelta(hours=timeOffset)

	year = scheduleDatetime.year
	month = months[scheduleDatetime.month]
	day = scheduleDatetime.day

	hour = scheduleDatetime.hour
	minute = scheduleDatetime.minute

	videoPath = f"Output\\output[{fileIndex}].mp4"
	videoDate = f"{month} {day}, {year}"
	videoTime = f"{hour}:{minute}"

	link = "https://studio.youtube.com/"

	PATH = "[PATH]\\chromedriver118.exe" #MODIFY THIS

	chrome_options = webdriver.ChromeOptions()
	chrome_options.add_argument("user-data-dir=[PATH]\\Chrome Beta\\User Data\\") #MODIFY THIS
	chrome_options.binary_location = "[PATH]\\chrome.exe" #MODIFY THIS

	driver = webdriver.Chrome(PATH, options=chrome_options)
	driver.get(link)

	# CLICK CREATE
	try:
		element = WebDriverWait(driver, 10).until(
			EC.presence_of_element_located((By.ID, "create-icon"))
		)
	except:
		driver.quit()

	element.click()

	# CLICK UPLOAD VIDEOS
	try:
		element = WebDriverWait(driver, 10).until(
			EC.presence_of_element_located((By.ID, "text-item-0"))
		)
	except:
		driver.quit()

	element.click()

	# UPLOAD VIDEO
	try:
		element = WebDriverWait(driver, 10).until(
			EC.presence_of_element_located((By.XPATH, '//*[@id="content"]/input'))
		)
	except:
		driver.quit()

	element.send_keys(videoPath)

	# TYPE TITLE
	try:
		element = WebDriverWait(driver, 10).until(
			EC.presence_of_element_located((By.ID, 'textbox'))
		)
	except:
		driver.quit()

	element.clear()
	element.send_keys(videoTitle)

	time.sleep(10)

	# CLICK NEXT BUTTON 3 TIMES
	for i in range(3):
		try:
			element = WebDriverWait(driver, 10).until(
				EC.presence_of_element_located((By.ID, "next-button"))
			)
		except:
			driver.quit()

		element.click()


	# CLICK SCHEDULE
	try:
		element = WebDriverWait(driver, 10).until(
			EC.presence_of_element_located((By.ID, 'schedule-radio-button'))
		)
	except:
		driver.quit()

	element.click()

	# CLICK DATE
	try:
		element = WebDriverWait(driver, 10).until(
			EC.presence_of_element_located((By.ID, 'datepicker-trigger'))
		)
	except:
		driver.quit()

	element.click()

	# TYPE DATE
	try:
		element = WebDriverWait(driver, 10).until(
			EC.presence_of_element_located((By.XPATH, '/html/body/ytcp-date-picker/tp-yt-paper-dialog/div/form/tp-yt-paper-input/tp-yt-paper-input-container/div[2]/div/iron-input/input'))
		)
	except:
		driver.quit()

	element.clear()
	element.send_keys(videoDate)
	element.send_keys(Keys.ENTER)

	# TYPE TIME
	try:
		element = WebDriverWait(driver, 10).until(
			EC.presence_of_element_located((By.XPATH, '/html/body/ytcp-uploads-dialog/tp-yt-paper-dialog/div/ytcp-animatable[1]/ytcp-uploads-review/div[2]/div[1]/ytcp-video-visibility-select/div[3]/ytcp-visibility-scheduler/div[1]/ytcp-datetime-picker/div/div[2]/form/ytcp-form-input-container/div[1]/div/tp-yt-paper-input/tp-yt-paper-input-container/div[2]/div/iron-input/input'))
		)
	except:
		driver.quit()

	element.clear()
	element.send_keys(videoTime)

	# CLICK SCHEDULE
	try:
		element = WebDriverWait(driver, 10).until(
			EC.presence_of_element_located((By.ID, "done-button"))
		)
	except:
		driver.quit()

	element.click()

	time.sleep(1)

	driver.quit()

	# -----------------------------------------save current state-----------------------------------------

	# colourIndex
	with open("Savedata/colourSave.txt", "w") as f:
		f.write(str(colourIndex))

	# fileIndex
	with open("Savedata/fileIndex.txt", "w") as f:
		f.write(str(fileIndex))

	# timeOffset
	with open("Savedata/timeOffset.txt", "w") as f:
		f.write(str(timeOffset))
