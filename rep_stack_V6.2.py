# Date:02/05/2015
# version 6.1
# Author: ZY Ye
# Modified:
# 02/05/2015: merge channel with previously selected slice to see the alignment
# 02/06/2015 add a Z-projection preview for selected ones & add dimension infor
# 02/08/2015 get the nFrame out from infor: infoStr = imp.getProperty('info')
# 02/10/2015 add function to do the multiReg alignment on P_ stack, make IJ.log()
# 02/10/2015 make it easy to switch from opened or un-opened images, also make it easy to get scanimage info: zyGetProperty(imp,fields)
# 02/14/2015 montage into nStacks*numRep
# 02/16/2015 re-organized for 30'' monitor
# 02/20/2015 change the montage to 8-bit
#add break when cancel

#Goal: Choose the best frame from certain repeats
#      then make a single repeat stack, save as P_(filename)
#		save the extract as P_(filename) and resorted stack as the same name in a subfolder (Single_rep)
# Case: images moved a lot during awake imaging

#bug:


from ij import IJ, ImagePlus, ImageStack
from ij.io import FileSaver
import sys,os
import time

def run():
	#screen = IJ.getScreenSize()
	#screenWidth = screen.width
	#screenHeight = screen.height
	#impSize = imp.getWindow().getSize()
	
	od = OpenDialog("Choose image file", None)
	file_path = od.getDirectory() #dir=File.getParent(od)
	file_name = od.getFileName() #name=FIle.getName(od)
	if not file_name:
		printLog("--Cancelled by user.",0)
	else:
		imp =Opener().openImage(file_path, file_name)
		imp.show()
		selectBest(imp)
def selectBest(imp):
	imp.getWindow().setLocation(0,0)
	file_name = imp.getTitle()
	file_path = IJ.getDirectory('image')
	printLog("filepath is "+file_path,1)
	
	
	[SI_version,nFrame,zStepSize,nStacks]=zyGetProperty(imp,"SI_version,nFrame,zStepSize,nStacks")	#need correct nSlices? do not delete any
	nSlices = imp.getNSlices()/nFrame				#otherwise, calculate by fiji function  
	msgStr = "The image has "+str(nFrame)+" frames from "+str(nStacks)+" stacks, was collected by ScanImage version "+str(SI_version)
	printLog(msgStr,0)
	if nFrame == 1:
		printLog("User need to import a file with multi-frames",0)
	else:			
		#duplicate one for resorting
		IJ.run(imp,"Duplicate...", "title=resortStack duplicate range=1-%d" %imp.getNSlices()) #bad fiji set this getNSlice() as all slice 
		resort_stack=IJ.getImage()
		resort_stack.getWindow().setLocation(0,0)
		IJ.run(resort_stack, "Label...", "format=0 starting=1 interval=1 x=5 y=20 font=18");
		
		#number pickup for every numRep
		IJ.selectWindow(file_name)
		#(width, height, nChannels, nSlices, nFrames) = imp.getDimensions(), bad fiji alway get wrong
		numRep = int(nFrame)
		m = int(nSlices) #real slice number when correcting the nFrames
		
		sPick = []
		printLog("-Current tif file:"+file_name,1)
		printLog("-nSlice="+str(m)+", nFrame="+str(numRep),2)
		printLog("-start picking the best repeat.",1)
		for i in range(0,m):
			j = i*numRep+1 #Z-step number
			#make montage to check all repeats at the same time for pickup
			IJ.run(imp,"Make Montage...", "columns="+str(numRep/nStacks)+" rows="+str(nStacks)+" scale=1 first="+str(j)+" last="+str(j+numRep-1)+" increment=1 border=1 font=12 label")
			m1_imp = IJ.getImage()
			IJ.run(m1_imp,"8-bit", "")
			m1_imp.getWindow().setLocation(530,0)
			IJ.run(m1_imp,"Set... ", "zoom=92 x=0 y=0")
			m1_title=m1_imp.getTitle()
			#merge the previous one if i>0
			if i==0:
				prePick = 1	#use first slice as mask
				IJ.run(resort_stack,"Duplicate...", "title=Max_z duplicate range=1-1" )
				zMax=IJ.getImage()
				zMax_win = zMax.getWindow().setLocation(0,580)
			else:	
				prePick = sPick[i-1]	#use previous selected slice as mask
							
			#duplicate numRep times of previous, concatenate, make montage, for merging channel as red with m1_imp
			m2_imp = mkMask(imp,prePick,numRep,nStacks)
			
			#merge the mask, and make new m1_imp as a 2-slice stack: Green (original) with merged
			m1_imp = zyMergeView(m1_imp,m2_imp)

			#pickup the best slice with slice number
			pickN = pickNum(numRep,nStacks)
			if not pickN:
				break
			else:
				pickN = pickN+j-1
					
			#do the moveSlice on resort_stack: move to the initial of pick: j
			resort_stack = moveSlice(resort_stack,pickN,j)

			#preview Z projection in a copy of resort_stack
			zMax.close()	#clear previous Z projection
			zMax = preview_Z(resort_stack,numRep,i+1) #show the new preview based on new pick
				
				
			#store the lucky slice number for making the substack in the future	
			sPick.append(int(pickN))
			#mmp = IJ.getImage()
			m1_imp.close()
		
		if len(sPick) == m:
			#means you have pick all slices required, but not cancel during process (break all out)
			IJ.selectWindow(file_name)
			outList =",".join(str(e) for e in sPick) #better to make a str: outList="slices=1,2,3"
			printLog("-Slices picked by user:"+outList,1)
			#print outlist
	
			IJ.run(imp,"Make Substack...", "slices=%s" %(outList)) #all need to be str
			sr_imp = IJ.getImage()
			sr_imp.setTitle('P_'+file_name)
			#imp.changes = 0
			#imp.close()
			#zMax.close()
			#need to do: put a header for sr_imp here
		
			msgStr = "pixel_width=0.102857 pixel_height=0.102857 voxel_depth="+str(zStepSize)
			printLog("-Set the property of picked stack "+sr_imp.getTitle()+" to:"+msgStr,1) 
			IJ.run(sr_imp, "Properties...", msgStr)

			pickName = sr_imp.getTitle()
			destFolder_SR = os.path.join(file_path, 'Single_rep')
			#do multireg alignment
			doAlign(sr_imp,destFolder_SR)
			zyAddProperty(sr_imp)
			saveStack(destFolder_SR,pickName,sr_imp)
		
			destFolder_RS = os.path.join(file_path, 'reSort')
			#add Info
			zyAddProperty(resort_stack)
			saveStack(destFolder_RS,file_name,resort_stack)
		else:
			m1_imp.close()
			resort_stack.changes = 0
		imp.changes = 0
		imp.close()
		zMax.close()	
		resort_stack.close()

def mkMask(imp,prePick,numRep,nStacks):
	file_name = imp.getTitle()			
	IJ.selectWindow(file_name)
	IJ.setSlice(prePick)
	tempFileNames=[]
	for pp in range(0,numRep):
		tempFileNames.append('temp'+str(pp))
		IJ.run(imp,"Duplicate...", "title=" +tempFileNames[pp])
		IJ.run("8-bit", "")
	cont_imgs = " ".join('image%d=%s' %(c+1,w) for c,w in enumerate(tempFileNames))
	IJ.run("Concatenate...", "title=tempStack " +cont_imgs)
	tempStack = IJ.getImage()
	IJ.run(tempStack,"Make Montage...", "columns="+str(numRep/nStacks)+" rows="+str(nStacks)+" scale=1 first=1 last="+str(numRep)+" increment=1 border=1 font=12")
	m2_imp=IJ.getImage()
	m2_imp.setTitle("Mask")
	tempStack.close()
	return m2_imp

def zyMergeView(imp1,imp2):
	imp1_title = imp1.getTitle()
	IJ.run(imp1, "RGB Color", "")
	imp2_title = imp2.getTitle()
	IJ.run(imp2, "RGB Color", "")

	IJ.run("Merge Channels...", "c1="+imp2_title+" c2="+imp1_title+" keep")	#will be RGB
	IJ.run("Concatenate...", "  title=[PickPan] image1=RGB image2="+imp1_title)
	
	imp1 = IJ.getImage()
	imp1.getWindow().setLocation(530,0)
	IJ.run(imp1,"Set... ", "zoom=90 x=0 y=0")
	imp2.changes = 0
	imp2.close()
	return imp1
	
def pickNum(numRep,nStacks):
	pickRange=[str(e) for e in range(1,numRep+1)]
	#gd = GenericDialog("pick a slice")
	gd = NonBlockingGenericDialog("pick a slice")	#non-modal dialog will not block selecting others
	gd.centerDialog(0) #this could enable the setLocation
	gd.setLocation(380,0)
	nRow = int(nStacks)
	nCol = int(numRep/nStacks)
	gd.addRadioButtonGroup("Select sliceNumber",pickRange,nRow,nCol,"1")
	gd.showDialog()
	
	if gd.wasCanceled():
		printLog("PickNum Was Cancelled by user",0)
		return	#what should I return? here is no change
	else:
		pickN = int(gd.getNextRadioButton())
		return pickN

def saveStack(destFolder,file_name,imp):	
	#rename the result and save it to subfolder
	if not os.path.isdir(destFolder):
		os.makedirs(destFolder)
	fullname=os.path.join(destFolder,file_name)
	#print (fullname)
	fs = FileSaver(imp)
	#print 'bSaveStack()', fullPath, 'nslices=', sr_imp.getNSlices()
	msgStr = "Dimension:" + str(imp.width) + " X " + str(imp.height) + " X " + str(imp.getNSlices())
	printLog("-Save "+file_name+" to "+destFolder,1)
	printLog("-"+msgStr,2)
	fs.saveAsTiffStack(fullname)

def preview_Z(imp,numRep,prePickZ):
	#duplicate another copy without changing original
	IJ.run(imp,"Duplicate...", "title=zMaxTemp duplicate range=1-%d" %imp.getNSlices())
	zMaxTemp=IJ.getImage()
	IJ.run(zMaxTemp,"8-bit", "")
	nSlice_real=zMaxTemp.getNSlices()/numRep
	#transvert dimension from t along Z to Z along t
	IJ.run(zMaxTemp,"Stack to Hyperstack...", "order=xytzc channels=1 slices="+str(nSlice_real)+" frames="+str(numRep)+" display=Color")
	IJ.run(zMaxTemp, "Hyperstack to Stack", "")

	IJ.run(zMaxTemp, "Z Project...", "start=1 stop="+str(prePickZ)+" projection=[Max Intensity]")
	zMax=IJ.getImage()
	zMax.getWindow().setLocation(0,580)
	zMax.setTitle("Max_Z")
	#close input stack without saving
	zMaxTemp.changes=0
	zMaxTemp.close()
	return zMax

def moveSlice(imp,sourceNum,destNum):
	#move a slice order inside a stack from m to n, donot use imp since it is almost global
	#make sure this function is not for m<n
	m=int(sourceNum)
	n=int(destNum)
	if m != n:
		#metaString = imp.getProperty("Label")
		#1.copy the n slice,inset to n+1 (now m become m+1)
		imp.setSlice(n)
		IJ.run(imp,"Copy","")
		IJ.run(imp,"Add Slice","")
		IJ.run(imp,"Paste","")
		#2. go to m+1 slice, copy and delete
		if m>n:
			imp.setSlice(m+1)
		else:
			printLog("ZY expect: m<n",0)
			imp.setSlice(m)
		IJ.run(imp,"Copy","")
		IJ.run(imp,"Delete Slice","")
		#3. go to n again, paste here
		imp.setSlice(n)
		IJ.run(imp,"Paste","")
		IJ.run(imp, "Select None", "")
		#set metadata back
		#imp.setPropery("Label",metaString)
	else:
		imp.setSlice(n)	#when n=m, show the slice to indicate which one has been selected
	return imp

def doAlign(imp,destFolder):
	if not os.path.isdir(destFolder):
		os.makedirs(destFolder)
	middleSlice = int(imp.getNSlices() // 2) #int() is necc.
	imp.setSlice(middleSlice)
	filename=imp.getTitle()
	transformationFile = destFolder + '\\' + os.path.splitext(filename)[0] + '.txt'
	printLog('-MultiStackReg aligning:' + filename +" by Translation",1)
	stackRegParams = 'stack_1=[%s] action_1=Align file_1=[%s] stack_2=None action_2=Ignore file_2=[] transformation=[Translation] save' %(imp.getTitle(),transformationFile)
	IJ.run('MultiStackReg', stackRegParams)


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
	infoStr = SI_Info+newInfo
	imp.setProperty('Info',infoStr)
		

def zyGetProperty(imp,fields):
	##(width, height, nChannels, nSlices, nFrames, zStepSize) = zyGetProperty(imp,"fields"), fields sep with ",". =>scanimage file real dimensions
	dim = {}
	impTitle = imp.getTitle()
	infoStr=imp.getProperty("Info")
	dim["SI_version"] = infoStr.split('state.software.version=')[1].split('\r')[0]
	dim["height"] = infoStr.split('state.acq.linesPerFrame=')[1].split('\r')[0]
	dim["width"] = infoStr.split('state.acq.pixelsPerLine=')[1].split('\r')[0]
	dim["nChannels"] = infoStr.split('state.acq.numberOfChannelsSave=')[1].split('\r')[0]
	dim["nSlices"] = infoStr.split('state.acq.numberOfZSlices=')[1].split('\r')[0]
	dim["zStepSize"] = infoStr.split('state.acq.zStepSize=')[1].split('\r')[0]
	dim["SI_nFrame"] = infoStr.split('state.acq.numberOfFrames=')[1].split('\r')[0]
	dim["nFrame"] = imp.getNSlices()/int(dim['nSlices'])	#make need a try or if to get the SI_nFrame
	dim["nStacks"] = int(dim["nFrame"])/int(dim["SI_nFrame"]) if int(dim["nFrame"]) > int(dim["SI_nFrame"]) else 1
	
	if "," in fields:
		reqFields = fields.split(",")
		return [float(dim[field]) for field in reqFields]
	else:
		return float(dim[fields])

def printLog(text, indent):
	msgStr = ''
	for i in (range(indent)):
		msgStr += '    '
	print msgStr,text #to command line
	IJ.log(msgStr + text)
	
if __name__ == '__main__': 
	printLog("===========================================================",0)
	printLog("  ********rep_stack_V4:"+time.strftime("%c")+" ***********",0)
	imp = IJ.getImage()	#for opened image
	if imp is None:
		run()
	else:
		selectBest(imp)
	#run()	#prompt user to open an image
	printLog("  ********Finished on "+time.strftime("%X")+" ***********",0)
	printLog("===========================================================",0)