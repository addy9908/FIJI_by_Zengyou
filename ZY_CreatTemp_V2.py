#Author: ZY Ye
#Date: 09/22/2016
#Creat Temp for time series file alignment

#1. choose file
#2. select slice for temp
#3. dupplicate the target slice
#4. duplicate target slice to nslice stack: copy then add/paste root
#5. save as temp.tif in temp folder


import os
from ij import IJ, ImagePlus
from ij.io import FileSaver  
import sys
import re

def run():
	printLog("=====ZY_CreatTemp_V2====",0)
	#Prompt user to open a image
	od = OpenDialog("Choose image file", None)
	if od is None:
	 	msgStr = "User Cancled"
		printLog(msgStr,1)
	else:	
		sourceFolder = od.getDirectory()
		fileName = od.getFileName()


		imp = IJ.openImage(sourceFolder+fileName)
		imp.show()
		n = imp.getNSlices()
		printLog("Processing source file: " + fileName,1)
		imp2= pickSlice(imp)
		if imp2:
			destFolder = os.path.join(sourceFolder, 'Temps')
			#outName = os.path.join(destFolder,fileName[:-4]+'_temp.tif') #remove the .tif in filename
			outName = os.path.join(destFolder,'temp.tif')
			# check or make the folder
			if not os.path.isdir(destFolder):
				os.makedirs(destFolder)	
			#make temp
			dupNSlice(imp2,n-1)

			printLog("Saving to: " + outName,1)
	 		fs = FileSaver(imp2)
	 		fs.saveAsTiffStack(outName)
	 		imp2.close()
		
	imp.close()
	msgStr = "ZY_CraetTemp_V2.py is Done."
	printLog(msgStr,0)

def pickSlice(imp):
	gd = NonBlockingGenericDialog("pick a slice")	#non-modal dialog will not block selecting others
	#gd.centerDialog(0) #this could enable the setLocation
	#gd.setLocation(380,0)
	gd.addNumericField('Target slice', 1, 0)
	gd.showDialog()
	
	if gd.wasCanceled():
		printLog("Mission Cancelled by user",0)
		return
	else:
		pickN = int(gd.getNextNumber())
		imp.setSlice(pickN) ##
		IJ.run(imp,"Duplicate...", "title=Temp")
		imp2=IJ.getImage()
		return imp2
		
def dupNSlice(imp,n):
		IJ.run(imp,"Copy","")
		for i in range(n):
			IJ.run(imp,"Add Slice","")
			IJ.run(imp,"Paste","")

def printLog(text, indent):
	msgStr = ''
	for i in (range(indent)):
		msgStr += '    '
	print msgStr,text #to command line
	IJ.log(msgStr + text)
	
if __name__ == '__main__': 
	run()	
	
	
