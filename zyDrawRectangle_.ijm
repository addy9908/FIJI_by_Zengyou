//Author: Zengyou Ye
//Purpose: Draw a specific size of rectangle and add it to ROI.
//  Do NOT forget to save ROI if you want to use it later,
//	or you should remember the size to create
//Affiliation: Department of Neuroscience, Johns Hopkins University, Linden Lab
//Date: 09/25/2014



macro "zDrawRectangle" {
	recheck=true;//设置初始值
	title = getTitle();
	w = getWidth;
	h = getHeight;
	rWidth = 0;
	rHeight = 0;
	rRotation = 0;
	xStart = w/2;
	yStart = h/2;
	while (recheck==true){
		Dialog.create("zDrawRectangle Options");
	
		Dialog.addMessage("Draw a specific rectangle,");
		Dialog.addMessage("and add it to the ROI maneger.");
		Dialog.addMessage("For the image: " + title);

		Dialog.addSlider("Width",0,w,rWidth);
		Dialog.addSlider("Height",0,h,rHeight);
		Dialog.addNumber("Angle",rRotation);
		Dialog.addMessage("=================");
		Dialog.addSlider("xStart",0,w,xStart);
		Dialog.addSlider("yStart",0,h,yStart);
		Dialog.addCheckbox("Preview",recheck);//Step 2.2 设置Check fields和label
		Dialog.addCheckbox("Add to ROI",0);
	
		Dialog.addMessage("Do NOT forget to save the ROI file.");
		Dialog.show();

		rWidth = Dialog.getNumber();
		rHeight = Dialog.getNumber();
		rRotation = Dialog.getNumber();
		xStart = Dialog.getNumber();
		yStart = Dialog.getNumber();
		recheck=Dialog.getCheckbox();// Step 3.2 把用户的输入值存入recheck中，如果没有uncheck则不断循环这些步骤，这样做的作用是让用户检查所输入值的效果
		SavetoROI = Dialog.getCheckbox();

		xEnd = rWidth;
		yEnd = rHeight;
		makeRectangle(xStart, yStart, xEnd, yEnd);
		if (rRotation != 0){
			run("Rotate...", "angle="+rRotation);
		}


		if (SavetoROI == 1){
			
			run("ROI Manager...");
			roiManager("Add");
			//count the number of ROI in the manager
			//choose the last one add recently, change the name to size
			nROI = roiManager("count");
			roiManager("Select", nROI-1);
			roiManager("Rename", "W"+rWidth+"_H"+rHeight);
			recheck = false;
		}
	}
}//end
