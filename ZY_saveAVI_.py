# -*- coding: utf-8 -*- 
#Zengyou Ye
#09/23/2016
#save t-series stack as AVI


from ij import IJ, ImagePlus
from ij.io import FileSaver
import os


global pixelSize_Linden2P
global barLeng
global FileType
barLeng = 20 #scalebar is 20 um
#defind pixelsize for 1024 with zoom 1
pixelSize_Linden2P = 0.54

def Options():
	fileTypes = ['T-series', 'Z-stack']
	gd = GenericDialog('Align Batch 7 Options')
	#gd.addStringField('Command: ', '')
	
	gd.addChoice('File Type', fileTypes, fileTypes[0])
	gd.showDialog()

	if gd.wasCanceled():
		print 'Options Was Cancelled by user'
		return 0
	else:
		fileType = gd.getNextChoice()
		return fileType

def run():
	imp = IJ.getImage()
	fileName = imp.getTitle()
	(width, height, nChannels, nSlices, nFrames) = imp.getDimensions()
	msgStr = "The original dimension is (xyczt): "+ str(width) +'x'+ str(height)+'x'+ str(nChannels)+'x'+ str(nSlices)+'x'+ str(nFrames)
	printLog(msgStr,1)
	#get infor from header, SCI 3.8 file
	infoStr = imp.getProperty("Info") #get all .tif tags
	#state.acq.zoomFactor=2.5, used for ccalculate pixelsize
	zoomFactor = float(infoStr.split('state.acq.zoomFactor=')[1].split('\r')[0]) 
	pixelSize = pixelSize_Linden2P*1024/(zoomFactor*width) #equition for converting pixelsize
	IJ.run(imp, "Set Scale...", "distance=1 known="+ str(pixelSize)+ " pixel=1 unit=um") #set resolution
	msgStr="zoom: " +str(zoomFactor)+ ", PixelSize: "+str(pixelSize)
	printLog(msgStr,1)
	

	fileType = Options()
	if nFrames == 1 and fileType == 'T-series': #for t series file
		temp = nSlices
		nSlices = nFrames
		nFrames = temp
		imp.setDimensions(nChannels, nSlices, nFrames)
		msgStr = "The new dimension for t-series is (xyczt): "+ str(width) +'x'+ str(height)+'x'+ str(nChannels)+'x'+ str(nSlices)+'x'+ str(nFrames)
		printLog(msgStr,1)
		frameRate = float(infoStr.split('state.acq.frameRate=')[1].split('\r')[0])
		timeStep = 1./frameRate
		msgStr="timeStep: "+str(timeStep)
		printLog(msgStr,1)
		#need to add label first, otherwise the salebar will not show
		IJ.run(imp, "Series Labeler", "stack_type=[time series or movie] label_format=[Custom Format] custom_suffix=sec custom_format=[] label_unit=[Custom Suffix] decimal_places=2 startup=0.000000000 interval="+str(timeStep)+" every_n-th=1 first=0 last=1515 location_presets=[Upper Right] x_=67 y_=0")
		printLog("Time series label added",2)
		
	else:
		#z-stack, state.acq.zStepSize=2
		zStep = float(infoStr.split('state.acq.zStepSize=')[1].split('\r')[0]) 
		msgStr="zStep: "+ str(zStep)
		printLog(msgStr,1)
		IJ.run(imp, "Series Labeler", "stack_type=z-stack label_format=Lengths custom_suffix=um custom_format=[] label_unit=um decimal_places=2 startup=0.000000000 interval="+str(zStep)+" every_n-th=1 first=0 last=198 location_presets=[Upper Right] x_=399 y_=0")
		printLog("Z-stack label added",2)
	
	#add scalebar
	IJ.run(imp, "Scale Bar...", "width=" +str(barLeng)+ " height=4 font=14 color=White background=None location=[Lower Right] hide overlay label")
	#IJ.run(imp, "Scale Bar...", "width=" +str(barLeng)+ " height=4 font=8 color=White background=None location=[Lower Right] overlay label")
	#add time stamp
	msgStr = "Scale Bar (length %d) is added" %barLeng
	printLog(msgStr,2)
	destFolder = "G:\\ZY\\imaging_2p\\Videos\\"
	if not os.path.isdir(destFolder):
		os.makedirs(destFolder)
	saveName = fileName[:-4]+".avi"
	destPath = os.path.join(destFolder, saveName)
	IJ.run(imp, "AVI... ", "compression=Uncompressed frame=60 save="+destPath)
	msgStr = "File saved: "+destPath
	printLog(msgStr,1)
	imp.changes = 0
	#imp.close()
	printLog("DONE",0)
	#print destPath

def printLog(text, indent):
	msgStr = ''
	for i in (range(indent)):
		msgStr += '    '
	print msgStr,text #to command line
	IJ.log(msgStr + text)
	
if __name__ == '__main__': 
	run()