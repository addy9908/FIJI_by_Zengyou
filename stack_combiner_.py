
#set a user defined field realNFrame=6\n

from ij import IJ, ImagePlus
from ij import WindowManager as WM 
import sys,os
import time

#open several image seperately with od(i)
#get the nSlice into a list, take the max and min with index
#set the od(max) as template, length(list) as the add slice times, copy from each and paste
# if they have this slice


def zyGetProperty(imp,fields):
	##(width, height, nChannels, nSlices, nFrames, zStepSize) = zyGetproperty(imp,"fields"), fields sep with ",". =>scanimage file real dimensions
	dim = {}
	#impTitle = imp.getTitle()
	infoStr=imp.getProperty("Info")
	dim["SI_version"] = infoStr.split('state.software.version=')[1].split('\r')[0]
	dim["height"] = infoStr.split('state.acq.linesPerFrame=')[1].split('\r')[0]
	dim["width"] = infoStr.split('state.acq.pixelsPerLine=')[1].split('\r')[0]
	dim["nChannels"] = infoStr.split('state.acq.numberOfChannelsSave=')[1].split('\r')[0]
	dim["nSlices"] = infoStr.split('state.acq.numberOfZSlices=')[1].split('\r')[0]
	dim["zStepSize"] = infoStr.split('state.acq.zStepSize=')[1].split('\r')[0]
	dim["SI_nFrame"] = infoStr.split('state.acq.numberOfFrames=')[1].split('\r')[0]
	dim["nFrame"] = imp.getNSlices()/int(dim['nSlices'])
	dim["nStacks"] = int(dim["nFrame"])/int(dim["SI_nFrame"]) if int(dim["nFrame"]) > int(dim["SI_nFrame"]) else 1
	
	if "," in fields:
		reqFields = fields.split(",")
		return [float(dim[field]) for field in reqFields]
	else:
		return float(dim[fields])

def impDup(imp,nStacks):
	#duplicate imp as a container for all stacks
	#test great
	#IJ.run(imp, "Label...", "format=0 starting=1 interval=1 x=5 y=20 font=18")
	#numRep = zyGetProperty(imp,"nFrame")
	numSlice = imp.getNSlices()
	realSlice = numSlice/numRep
	nTotal = int((nStacks-1)*numRep)
	for i in sorted(range(realSlice),reverse=True):
		j = int((i+1)*numRep)
		imp.setSlice(j)
		[IJ.run(imp,"Add Slice","") for _ in range(nTotal)]	#repeat the func for nTotal times
		
	
def binder(imp,imp1,nStacks,n):
	#bind imp1 to imp to the position determined by n: num n of all nStacks
	#test great
	nSlice1 = imp1.getNSlices()	
	realSlice1 = nSlice1/numRep
	for i in sorted(range(realSlice1),reverse = True):
		#bind from floor to roof
		mSlice = int(i*numRep+1)
		tSlice = i*(nStacks*numRep)+1+n*numRep
		tSlice = int(tSlice)
		for j in range(3):
			sourceSlice = int((mSlice)+j)
			imp1.setSlice(sourceSlice)
			IJ.run(imp1,"Copy","")
			destSlice = tSlice+j
			imp.setSlice(destSlice)
			IJ.run(imp,"Paste","")
	imp1.close()

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
	newInfo = '\nzNumSlices='+str(nSlices)+'\nzNumFrame='+str(nFrame)+'\nzTotalSlices='+str(imp.getNSlices())+'\nzNumStacks='+str(nStacks)+'\nzModifiedTime='+"'"+time.strftime("%c")+"'"
	infoStr = SI_Info+newInfo
	imp.setProperty('Info',infoStr)
	
def run():
	global numRep		
	images = map(WM.getImage, WM.getIDList())
	nStacks = len(images)	#num of stacks opened
	numSlices = [images[i].getNSlices() for i in range(nStacks)] #[12,13,12]
	maxSlice = max(numSlices)	#the max number of slices among all opened stacks
	#maxIndex = [i for i,j in enumerate(numSlices) if j == maxSlice] # the index of the image with maxSlice
	#move max to the head and min to the end
	imps = [image for (numSlice,image) in sorted(zip(numSlices,images),reverse = True)] #sort the images base on their nSlices

	numRep = zyGetProperty(imps[0],"nFrame")

	#add slices in imp[0], base on (nStacks-1)*numRep
	impDup(imps[0],nStacks)
	#for other imps, loop them and copy/paste every 3(numRep) into imp
	for i in range(nStacks-1):
		n = i+1
		binder(imps[0],imps[n],nStacks,n)
	
	#set the nFrame = nStacks*numRep, and save the image
	# record the numSlices, numFrame, totalSlices and numStacks in the infoStr
	zyAddProperty(imps[0])
	
	msgStr = "nslices="+str(maxSlice/numRep)+" nframes="+str(nStacks*numRep)
	#IJ.run(imps[0], "Properties...", msgStr)
	IJ.log("For real: "+msgStr)
	file_path = IJ.getDirectory('image')
	file_name = imps[0].getTitle()
	filename = 'C_'+file_name
	imps[0].setTitle(filename)
	destPath = os.path.join(file_path,'combined')
	saveStack(destPath,filename,imps[0])

if __name__ == '__main__': 
	IJ.log("===========================================================")
	IJ.log("  ********stack_combiner:"+time.strftime("%c")+" ***********")
	run()	#prompt user to open an image
	IJ.log("  ********Finished on "+time.strftime("%X")+" ***********")
	IJ.log("===========================================================")
