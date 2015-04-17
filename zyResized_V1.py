#Author: ZY Ye
#Date: Jun 2014
#
#Purpose: Try to run the resize macro with python according to Bob' code
#The resize macro will change the size of all .tif files in the folder
#save a copy of each .tif in source as "resize" folder in destination
#
#Set numberOfChannels=2 and we will deinterleave and make _ch1/_ch2 pair
#
#to do:
#1) import the modules, def the dialog
#2) open the sourcefolder
#3) list all .tif without max file
#4) resize them and save in "resize" folder

import os
from ij import IJ, ImagePlus
from ij.io import FileSaver  
import sys
import re

#function to get user options
def getOptions():
	gd = GenericDialog("Options")
	gd.addNumericField("Number of Channels", 1, 0) # defaut as 1 channels and show 0 decimals
	gd.addNumericField("Change to width", 256, 0) 
	gd.addNumericField("change to height", 256, 0) 
	gd.addCheckbox("replace Destination .tif files", 0)
	gd.showDialog()

	# in case of cancel the resize
	if gd.wasCanceled():
		print "User canceled dialog."
		return -1
	# read options user input
	numberOfChannels = gd.getNextNumber()
	reWidth = gd.getNextNumber()
	reHeight = gd.getNextNumber()
	replaceExisting = gd.getNextBoolean()

	# make them as global to be used in next function
	global numberOfChannels
	global reWidth
	global reHeight
	global replaceExisting

	return 1 #int(numberOfChannels)

# function to resize
def run():
	print "=====ZY_Resizetif_V1===="

	#expecting one argument: the file path (choose the folder first)
	if len(sys.argv) < 2:
		print "We need at least one folder as input"
		print "Please choose the input folder"

		#prompt user to choose a folder"
		sourceFolder = DirectoryChooser("Please choose a directory of .tif files").getDirectory()
		if not sourceFolder:
			return
	else:
		sourceFolder = sys.argv[1] #assuming it ends in '/'

	#get user options

	okGo = getOptions()
	if okGo == -1:
		return 0
	destFolder = os.path.join(sourceFolder, 'resized')
	
	print destFolder
		
	# check or make the folder
	if not os.path.isdir(destFolder):
		os.makedirs(destFolder)

	print "Processing souce folder", sourceFolder
	print "Saving to destination folder", destFolder
	IJ.log("   ====== Startin ZY_resize_V1 ======")
	IJ.log("   Processing source folder: " + sourceFolder)
	IJ.log("   Saving to destination folder: " + destFolder)
	
	numOpened = 0
	numSaved = 0

	for filename in os.listdir(sourceFolder):
		startWithDot = filename.startswith(".")
	 	isMax = filename.endswith("max.tif")
	 	isTif = filename.endswith(".tif")

	 	if (not startWithDot) and (not isMax) and isTif:
	 		shortname, fileExtension = os.path.splitext(filename)
	 		outPath = destFolder + "/" + filename
	 		outPath1 = destFolder + "/" + shortname + "_ch1" + ".tif"
	 		outPath2 = destFolder + "/" + shortname + "_ch2" + ".tif"

	 		# before processing, check if eventual dest exists
	 		if not replaceExisting:
	 			if numberOfChannels == 2 and os.path.exists(outPath1) and os.path.exists(outPath2):
	 				msgStr = "        -->The file==" + filename + "== has been resized, not processing again"
	 				print msgStr
	 				IJ.log(msgStr)
	 				continue #with next iteration
	 			if numberOfChannels == 1 and os.path.exists(outPath):
	 				msgStr = "        -->The file==" + filename + "== has been resized, not processing again"
	 				print msgStr
	 				IJ.log(msgStr)
	 				continue #with next iteration
	 		
	 		print "================================"
	 		msgStr = str(numOpened+1) + ". opening>> " + sourceFolder + filename
	 		print msgStr
	 		IJ.log(msgStr)

	 		imp = IJ.openImage(sourceFolder+filename)
	 		if imp is None:
	 			msgStr = "        -->>Error: could not open image file:" + filename
	 			print msgStr
	 			IJ.log(msgStr)
				continue #with next iteration

			imp.show()
			numOpened +=1
 
			msgStr = "        -->Original size is:" + str(imp.width) + "x" + str(imp.height) + "x" + str(imp.getNSlices())
			print msgStr
	 		IJ.log(msgStr)

	 		if imp.width < reWidth or imp.height < reHeight:
	 			IJ.run(imp, "Size...", "width=" + str(reWidth) + " height=" + str(reHeight) + " depth=" + str(imp.getNSlices()) + " interpolation=Bilinear")
				msgStr = "        -> Changing size to:" + str(imp.width) + "x" + str(imp.height)+ "x" + str(imp.getNSlices())
	 			print msgStr
	 			IJ.log(msgStr)
				
				imp = IJ.getImage() 	

	 			if numberOfChannels == 2:
	 				print "deinterleaving"
	 				IJ.run("Deinterleaving", "how = 2") #make 2 windows

	 				#ch2
	 				imp2=IJ.getImage()
	 				fs = FileSaver(imp2)
	 				print "saving channel 2 file to", outPath2
	 				fs.saveAsTiffStack(outPath2)
	 				numSaved += 1
	 				imp2.changes = 0
	 				imp2.close()

	 				#ch1
	 				imp1 = IJ.getImage()
	 				fs= FileSaver(imp1)
	 				print "saving channel 1 file to", outPath1
	 				fs.saveAsTiffStack(outPath1)
	 				numSaved += 1
	 				imp1.changes = 0
	 				imp1.close()
	 			
	 			elif numberOfChannels == 1:
	 				fs= FileSaver(imp)
	 				print "saving file to", outPath
	 				fs.saveAsTiffStack(outPath)
	 				numSaved += 1
	 				imp.changes = 0
	 		else:
	 			msgStr = "        --> The file == " + filename + "== was ignored,because the size is bigger than setting"
				print msgStr
				IJ.log(msgStr)
	 		
	 		imp.close() #close original
	 			
		else: # showing that we ignoring the max

			if (not startWithDot) and isTif:
				#print "   ===================================="
				print filename
				msgStr = "        --> Ignoring .tif:" + filename
				print msgStr
				IJ.log(msgStr)	

	msgStr = "   ZY_Resized_V1.py is Done, Number Opened " + str(numOpened) + ", Number Saved " + str(numSaved)
	print "   ==="
	print msgStr
	print "   ==="
	IJ.log("==========")
	IJ.log(msgStr)

run() 		
	
	
