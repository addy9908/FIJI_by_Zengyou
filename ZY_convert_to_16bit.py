# Purpose: Convert deconverlution file from 32 bit to 16 bit
# 1. set the option_convert_without scale
# 2. open deconvoluted file in <session>_raw
# 3. convert to 16 bit
# 4. save to overwrite
# 
# 
# 


from ij import IJ, ImagePlus, WindowManager
from ij.gui import GenericDialog, Roi
from ij.io import Opener, FileSaver, DirectoryChooser
from java.io import File, FilenameFilter
import sys, os, re, math
import time # for yyyymmdd, for wait

#don't forget to: #add ZY's deconvolution folder in sourcecode's make output folder section as:
	#add ZY's deconvolution folder
#	destDecFolder = destFolder + 'deconvolution/'
#	if not os.path.isdir(destDecFolder):
#		os.makedirs(destDecFolder)

class Filter(FilenameFilter):
	def accept(self, dir, name):
		reg = re.compile('\.tif$')
		regMax = re.compile('\max.tif$')
		m = reg.search(name)
		m2 = regMax.search(name)
		if m and not m2:
			return 1
		else:
			return 0

class Filter_LSM(FilenameFilter):
	def accept(self, dir, name):
		reg = re.compile('\.lsm$')
		regMax = re.compile('\max.lsm$')
		m = reg.search(name)
		m2 = regMax.search(name)
		if m and not m2:
			return 1
		else:
			return 0
			
def bPrintLog(text, indent):
	msgStr = ''
	for i in (range(indent)):
		msgStr += '    '
		print '   ',
	print text #to command line
	IJ.log(msgStr + text)

def convert32to16(fullFilePath): #overwrite the file!!!
	if not os.path.isfile(fullFilePath):
		bPrintLog('\nERROR: runOneFile() did not find file: ' + fullFilePath + '\n',0)
		return 0
	elif not fullFilePath.endswith('tif'):
		msg = fullFilePath +" is not a deconvoluted tif file"
		bPrintLog(msg,2)
	else:
		bPrintLog(time.strftime("%H:%M:%S") + ' starting runOneFile()for overwrite: ' + fullFilePath, 1)
	
		#open and overwrite the deconvoluted file as 16 bit
		imp = Opener().openImage(fullFilePath)	#deconvoluted file
		if imp.getBitDepth() == 32:
			imp.show()
			msgStr = "Converting 32 to 16-bit..."
			bPrintLog(msgStr,3)
			IJ.run("16-bit")
			
			msgStr = "Overwriting 32-bit with 16-bit File in" + fullFilePath
			bPrintLog(msgStr,3)
			IJ.run(imp,"Save","") #save as replace without asking
			
		imp.close()
	
def runOneFolder(sourceFolder):	#deconvolution folder
	if not os.path.isdir(sourceFolder):
		bPrintLog('\nERROR: runOneFolder() did not find folder: ' + sourceFolder + '\n',0)
		return 0
		
	tifNames = [file.name for file in File(sourceFolder).listFiles(Filter())]
	numTifs = len(tifNames)

	bPrintLog('source deconvolution Folder: ' + sourceFolder,1)
	bPrintLog('Number of deconvoluted tifs: ' + str(numTifs),1)
		
	count = 1
	for tifName in tifNames:
		msgStr = '--->>> Opening ' + str(count) + ' of ' + str(numTifs)
		bPrintLog(msgStr, 0)	
		if tifName.endswith('tif'):
			fileFullPath = os.path.join(sourceFolder,tifName)
			convert32to16(fileFullPath)
		else:
			msg = "Not a deconvoluted tif file: " +tifName
		count += 1

	bPrintLog('Done runOneFolder', 1)

def overWriteMouse(mouseFolder):

	mouseID = os.path.basename(mouseFolder[:-1]) #remove '/'
	bPrintLog('Mouse Folder is: ' + mouseFolder,1)
	bPrintLog('Mouse ID is: ' + mouseID,1)
	targetFolder = mouseFolder + mouseID +  '_raw'	#files moved to raw with python code
	if os.path.isdir(targetFolder):
		runOneFolder(targetFolder)
	else:
		bPrintLog('Not _raw folder exits!',1)

def overWriteDate(dayFolder):
	if not os.path.isdir(dayFolder):
		bPrintLog('\nERROR: runOneDay() did not find folder: ' + dayFolder + '\n',0)
		return 0

	dirNames = [file for file in os.listdir(dayFolder) if os.path.isdir(os.path.join(dayFolder,file))]
	numDirs = len(dirNames)
	bPrintLog('dayFolder is:' + dayFolder,0)
	bPrintLog('Number of subFolders: ' + str(numDirs),1)
	#put option here so we do not have to click for each folder
	for dirName in dirNames:
		mouseFolder = os.path.join(dayFolder, dirName)+ '/'	 # did not add '/' to the end
		bPrintLog('*********************************',0)
		msg = 'Mouse folder is: ' +mouseFolder
		bPrintLog(msg, 1)
		overWriteMouse(mouseFolder)

def runOneMonth(monthDir):
	dateDirs = [file for file in os.listdir(monthDir) if os.path.isdir(os.path.join(monthDir,file))]
	numDates = len(dateDirs)
	monthInfo = os.path.basename(monthDir)
	msg = " Number of dates imaged in month %s is %d" %(monthInfo,numDates)
	bPrintLog(msg,0)
 	ind = 1
	for imageDate in dateDirs:
		msg = "*Running imaging date %s (%d/%d)" %(imageDate, ind,numDates)
		bPrintLog(msg,0)
        	dateDir = os.path.join(monthDir,imageDate)
        	overWriteDate(dateDir)
        	ind += 1

#
def run():
	types = ['oneDay','oneMouse','oneFile','oneMonth','OneFolder','mapManager']

	gd = GenericDialog('Define Source Options')
	#gd.addMessage('Choose the Source type:')
	gd.addChoice('Source Type:',types,types[0])
	gd.showDialog()



	if gd.wasCanceled():
		bPrintLog('user cancel the plugin',1)
		return 0
	else:
		srcType = gd.getNextChoiceIndex()
		#run one day
		if srcType == 0:
			dayFolder = DirectoryChooser('Please Choose A Directory Of .tif Files').getDirectory()
			if not os.path.isdir(dayFolder):
				bPrintLog('\nERROR: runOneDay() did not find folder: ' + dayFolder + '\n',0)
				return 0

			overWriteDate(dayFolder)
		
		#run one mouse
		if srcType == 1:
			mouseFolder = DirectoryChooser('Please Choose A Mouse Directory Of .tif Files').getDirectory()
			if not mouseFolder:
				exit(1)
			overWriteMouse(mouseFolder)

		#run one file
		if srcType == 2:
			od = OpenDialog("Choose a convoluted tif file to overwrite", None)
			srcDirectory = od.getDirectory()
			srcFile = od.getFileName()
			if srcFile != None:
				fileFullPath = os.path.join(srcDirectory,srcFile)
				convert32to16(fileFullPath)
		#run one month
		if srcType == 3:
			monthFolder = DirectoryChooser('Please Choose A MONTH Directory Of .tif Files').getDirectory()
			if not os.path.isdir(monthFolder):
				bPrintLog('\nERROR: runOneMonth() did not find folder: ' + monthFolder + '\n',0)
				return 0

			runOneMonth(monthFolder)

		#run one Folder
		if srcType == 4:
			srcFolder = DirectoryChooser('Please Choose A folder Of .tif Files').getDirectory()
			if not os.path.isdir(srcFolder):
				bPrintLog('\nERROR: runOneFolder() did not find folder: ' + srcFolder + '\n',0)
				return 0

			runOneFolder(srcFolder)
		if srcType == 5:	#align centain map's raw folder
			mapPath = 'G:/ZY/MapManager3'
			#mapNames = raw_input('type maps initials seperated with ,: ').split(',')	#raw_input does not work here
			#mapNames = tuple(mapNames)
			mapNames = "F58,F59"	#preset
			#get map names
			gd = GenericDialog('Choose maps for alignment')
			gd.addStringField("maps root path",mapPath,50)
			gd.addStringField("maps name initials sep = ','(empty for all)",mapNames,50)
			gd.showDialog()
			if gd.wasCanceled():
				bPrintLog('user cancel the plugin',0)
				return 0
			mapPath = gd.getNextString()
			mapNames = tuple(gd.getNextString().split(','))
			mapFolders = [f for f in os.listdir(mapPath) if f.startswith(mapNames) and os.path.isdir(os.path.join(mapPath,f))]

			if len(mapFolders) == 0:
				bPrintLog('\nERROR: no map folder found',0)
				return 0
			
 			bPrintLog('Map Folder number: ' + str(len(mapFolders)),0)
        	#put option here so we do not have to click for each folder
			sourceFolders= [mapPath + '/' + mapFolder + '/raw/raw_userRaw' for mapFolder in mapFolders]
			for srcFolder in sourceFolders:
				runOneFolder(srcFolder)
			


		

if __name__ == '__main__': 
	bPrintLog(' ',0)
	bPrintLog('=================================================',0)
	bPrintLog('convert32to16',0)
	bPrintLog('Will convert deconvoluted 32-bit tif to 16-bit, without scale',1)
	bPrintLog('=================================================',0)
	# turn off scale for convertation
	IJ.run("Conversions...", " ")
	run()
	bPrintLog('=================================================',0)
	bPrintLog('All Done',0)




