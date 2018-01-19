#update this plugin for Bob's new bAlign_Batch_v7_1

import bAlignBatch_v7_1_zy as bab
from ij import IJ, ImagePlus, WindowManager
from ij.gui import GenericDialog, Roi
from ij.io import Opener, FileSaver, DirectoryChooser
import sys, os, re, math

#don't forget to: #add ZY's deconvolution folder in sourcecode's make output folder section as:
	#add ZY's deconvolution folder
#	destDecFolder = destFolder + 'deconvolution/'
#	if not os.path.isdir(destDecFolder):
#		os.makedirs(destDecFolder)


#
def run():
	types = ['oneDay','oneFolder','oneFile','mapmaneger','test']

	gd = GenericDialog('Define Source Options')
	#gd.addMessage('Choose the Source type:')
	gd.addChoice('Source Type:',types,types[0])
	gd.showDialog()



	if gd.wasCanceled():
		print 'user cancel the plugin'
		return 0
	else:
		srcType = gd.getNextChoiceIndex()

		#run one day
		if srcType == 0:
			dayFolder = DirectoryChooser('Please Choose A Directory Of .tif Files').getDirectory()
			if not os.path.isdir(dayFolder):
				bab.bPrintLog('\nERROR: runOneDay() did not find folder: ' + dayFolder + '\n',0)
				return 0

			dirNames = [file for file in os.listdir(dayFolder) if os.path.isdir(os.path.join(dayFolder,file))]
        		numDirs = len(dirNames)
        		bab.bPrintLog('dayFolder is:' + dayFolder,0)
        		bab.bPrintLog('Number of subFolders: ' + str(numDirs),1)
        		#put option here so we do not have to click for each folder
			if bab.Options(dayFolder + dirNames[0] + '/'):
				for dirName in dirNames:
		 			#sourceFolder = os.path.join(dayFolder, dirName) # did not add '/' to the end
					sourceFolder = dayFolder + '/' + dirName + '/'
		 			bab.runOneFolder(sourceFolder)
		
		#run one folder
		if srcType == 1:
			sourceFolder = DirectoryChooser('Please Choose A Directory Of .tif Files').getDirectory()
			if not sourceFolder:
				exit(1)
			if bab.Options(sourceFolder):
				bab.runOneFolder(sourceFolder)

		#run one file
		if srcType == 2:
			od = OpenDialog("Choose image file", None)
			srcDirectory = od.getDirectory()
			srcFile = od.getFileName()
			if srcFile != None and bab.Options(srcDirectory):
				bab.runOneFile(srcDirectory + srcFile)

		if srcType == 3: #align centain map's raw folder
			mapPath = 'G:/ZY/MapManager3'
			#mapNames = raw_input('type maps initials seperated with ,: ').split(',')	#raw_input does not work here
			#mapNames = tuple(mapNames)
			mapNames = "F58,F59"	#preset
			#get map names
			gd = GenericDialog('Choose maps for alignment')
			gd.addStringField("maps root path",mapPath,50)
			gd.addStringField("maps name initials sep = ','",mapNames,50)
			gd.showDialog()
			if gd.wasCanceled():
				bab.bPrintLog('user cancel the plugin',0)
				return 0
			mapPath = gd.getNextString()
			mapNames = tuple(gd.getNextString().split(','))
			mapFolders = [f for f in os.listdir(mapPath) if f.startswith(mapNames) and os.path.isdir(os.path.join(mapPath,f))]

			if len(mapFolders) == 0:
				bab.bPrintLog('\nERROR: no map folder found',0)
				return 0
			
 			bab.bPrintLog('Map Folder number: ' + str(len(mapFolders)),0)
        	#put option here so we do not have to click for each folder
			sourceFolders= [mapPath + '/' + mapFolder + '/raw/' for mapFolder in mapFolders]
			if bab.Options(sourceFolders[0]):
				for sourceFolder in sourceFolders:
					bab.runOneFolder(sourceFolder)

		if srcType == 4: #for test
			gd = GenericDialog('Choose maps')
			gd.addStringField('maps name initials','F58,F59')
			gd.showDialog()
			maps = gd.getNextString().split(',')
			maps = tuple(maps)
			bab.bPrintLog(maps[0],0)
			

if __name__ == '__main__': 
	run()
	bab.bPrintLog('All Done',0)
	bab.bPrintLog('Next step: deconvolution, change to 11 bit, and rename',0)



