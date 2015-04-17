from ij import IJ, ImagePlus, ImageStack
from ij.io import FileSaver
import sys,os
import time


def zyAddProperty(imp):
	#add user defined field (numSlices, nunFrame, time) in the infor, with \n
	infoStr = imp.getProperty('Info')
	if 'numSlices' in infoStr or 'zNumSlices' in infoStr:
		SI_Info = infoStr.split('\n')[0]
	else:
		SI_Info = infoStr
	nSlices = int(infoStr.split('numberOfZSlices=')[1].split('\r')[0])
	nFrame = imp.getNSlices()/nSlices
	SI_nFrame = int(SI_Info.split('numberOfFrames=')[1].split('\r')[0])
	nStacks = nFrame/SI_nFrame if nFrame > SI_nFrame else 1
	newInfo = '\nzNumSlices='+str(nSlices)+'\nzNumFrame='+str(nFrame)+'\nzTotalSlices='+str(imp.getNSlices())+'\nzNumStacks='+str(nStacks)+'\nzModifiedTime='+"'"+time.strftime("%c")+"'\r"
	print newInfo
	infoStr = SI_Info+newInfo
	imp.setProperty('Info',infoStr)

def saveStack(destFolder,file_name,imp):	
	#rename the result and save it to subfolder
	if not os.path.isdir(destFolder):
		os.makedirs(destFolder)
	fullname=os.path.join(destFolder,file_name)
	#print (fullname)
	fs = FileSaver(imp)
	#print 'bSaveStack()', fullPath, 'nslices=', sr_imp.getNSlices()
	print('save result to: ',fullname)
	msgStr = "Dimension:" + str(imp.width) + " X " + str(imp.height) + " X " + str(imp.getNSlices())
	print (msgStr)
	IJ.log("   -Save "+file_name+" to "+destFolder)
	IJ.log("      -"+msgStr)
	fs.saveAsTiffStack(fullname)

imp = IJ.getImage()
file_name = imp.getTitle()
file_path = IJ.getDirectory('image')
zyAddProperty(imp)
saveStack(file_path,file_name,imp)
imp.close()
