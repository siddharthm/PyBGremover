from sys import argv,exit
try:
	import Tkinter as tk
except:
	print "Failed to load GUI. Install Tkinter first"
try:
	from PIL import Image,ImageDraw
except:
	print "PIL not present."
	exit()
try:
	from PIL import ImageTk
except:
	print "ImageTk not present"
import os
try:
	import numpy as np
except:
	print "Numpy not present"
	exit()
import math
import region_shrinking as rs


# Dependencies
# -PIL
# -ImageTk
# -Numpy
# -region shrinking

class myApp:
	def __init__(self,parent,image):
		self.parent=parent
		defaultbg=parent.cget('bg')
		self.canvas=tk.Canvas(parent,width=image.size[0],height=image.size[1])
		self.canvas.pack(side=tk.TOP)
		self.image=image.copy()
		self.imagetk=ImageTk.PhotoImage(self.image)
		self.image_original=image.copy()

		self.isPolygon=False
		self.polygon=[]
		self.txt=""

		self.threshold=0.01
		self.item=self.canvas.create_image(image.size[0]//2,image.size[1]//2,image=self.imagetk)
		self.canvas.bind("<Motion>",self.imageMotion)
		self.canvas.bind("<Button-1>",self.imageClick)

		self.image_copy=image.copy()

		self.myCont1= tk.Frame(parent)
		self.myCont1.pack(side=tk.TOP)

		self.buttonReset=tk.Button(self.myCont1,text="Reset",background="tan")
		self.buttonReset.pack(side=tk.RIGHT)
		self.buttonReset.bind("<Button-1>",self.reset)

		self.buttonRemoveNoise=tk.Button(self.myCont1,text="Rm Noise",background="cyan")
		self.buttonRemoveNoise.pack(side=tk.LEFT)
		self.buttonRemoveNoise.bind("<Button-1>",self.remove_noise)

		self.buttonSave=tk.Button(self.myCont1,text="Save and close !",background="grey")
		self.buttonSave.pack(side=tk.LEFT)
		self.buttonSave.bind("<Button-1>",self.saveChanges)

		self.buttonUndo=tk.Button(self.myCont1,text="Undo",background="grey")
		self.buttonUndo.pack(side=tk.LEFT)
		self.buttonUndo.bind("<Button-1>",self.undo)

		self.myCont2=tk.Frame(parent)
		self.myCont2.pack(side=tk.TOP)

		self.button2=tk.Button(self.myCont2,text="Thres +.001 ",background="grey")
		self.button2.pack(side=tk.LEFT)
		self.button2.bind("<Button-1>",self.incThreshold)

		self.button3=tk.Button(self.myCont2,text="Thres -.001",background="grey")
		self.button3.pack(side=tk.LEFT)
		self.button3.bind("<Button-1>",self.decThreshold)

		self.buttonPoly=tk.Button(self.myCont2,text="Create Polygon")
		self.buttonPoly.pack(side=tk.LEFT)
		self.buttonPoly.bind("<Button-1>",self.createPolygon)


		self.myCont3=tk.Frame(parent)
		self.myCont3.pack(side=tk.TOP)

		self.buttonBGgreen=tk.Button(self.myCont3,text="Green BG",bg="green")
		self.buttonBGgreen.pack(side=tk.LEFT)
		self.buttonBGgreen.bind("<Button-1>",lambda event,arg="green":self.bgchange(event,arg))

		self.buttonBGred=tk.Button(self.myCont3,text="Red BG",bg="red")
		self.buttonBGred.pack(side=tk.LEFT)
		self.buttonBGred.bind("<Button-1>",lambda event,arg="red":self.bgchange(event,arg))

		self.buttonBGdefault=tk.Button(self.myCont3,text="Default BG",background=defaultbg)
		self.buttonBGdefault.pack(side=tk.LEFT)
		self.buttonBGdefault.bind("<Button-1>",lambda event,arg=defaultbg:self.bgchange(event,arg))

		self.labelThr=tk.Label(parent,text="Current Threshold: "+str(self.threshold))
		self.labelThr.pack(side=tk.RIGHT)

		self.labelPixels=tk.Label(parent,text="",fg="yellow",bg="black")
		self.labelPixels.pack(side=tk.LEFT)


	def imageClick(self,event):
		if not self.isPolygon:
			self.image_copy=self.image.copy()
			pixels=self.image.load()
			self.removeBG(pixels,event.x,event.y,self.image.size[0],self.image.size[1])	
			self.updateCanvas()
		else:
			self.polygon.append((event.x,event.y))
			draw=ImageDraw.Draw(self.image)
			draw.line(self.polygon,fill="black")
			del draw
			self.updateCanvas()

	def imageMotion(self,event):
		self.labelPixels["text"]="("+str(event.x)+","+str(event.y)+")"

	def createPolygon(self,event):
		if self.isPolygon:
			self.labelThr["text"]="Working..."
			self.labelThr.update_idletasks()
			self.image=self.image_copy.copy()
			#color_layer = Image.new('RGBA', self.image.size, (0,0,0,0))
			#alpha_mask = Image.new('L', self.image.size, 0)
			#alpha_mask_draw = ImageDraw.Draw(alpha_mask)
			#alpha_mask_draw.polygon(self.polygon, fill=255)
			#self.image= Image.composite(color_layer, self.image, alpha_mask)
			draw=ImageDraw.Draw(self.image)
			draw.polygon(self.polygon,fill=(0,0,0,0))
			self.cancelPolygon()	
		else:
			self.image_copy=self.image.copy()
			self.txt=self.labelThr["text"]
			self.labelThr["text"]="Select the vertices of polygon in order."
			self.buttonPoly["text"]="Click when Done"
			self.buttonCancel=tk.Button(self.myCont2,text="Cancel")
			self.buttonCancel.bind("<Button-1>",self.cancelPolygon)
			self.buttonCancel.pack(side=tk.LEFT)
			self.isPolygon=True

	def cancelPolygon(self,event=None):
		self.buttonPoly["text"]="Create Polygon"
		self.polygon=[]
		self.labelThr["text"]=self.txt
		self.isPolygon=False
		if event!=None: # When clicked on cancel button
			self.image=self.image_copy.copy()
		self.updateCanvas()
		self.buttonCancel.pack_forget()
		

	def bgchange(self,event,color):
		self.canvas.config(background=color)

	def saveChanges(self,event):
		self.remove_noise()
		#pxls_original=self.image_ref.load()
		#pxls_changed=self.image.load()
		#for x in range(self.image.size[0]):
		#	for y in range(self.image.size[1]):
		#		pxls_original[x,y]=pxls_changed[x,y]
		self.parent.destroy()
	

	def reset(self,event):
		self.image=self.image_original.copy()
		self.updateCanvas()

	def undo(self,event):
		self.image=self.image_copy.copy()
		self.updateCanvas()

	def incThreshold(self,event):
		self.threshold+=.001
		self.labelThr["text"]="Current Threshold: "+str(self.threshold)[:7]

	def decThreshold(self,event):
		self.threshold-=.001
		self.labelThr["text"]="Current Threshold: "+str(self.threshold)[:7]

	def updateCanvas(self):
		self.imagetk=ImageTk.PhotoImage(self.image)
		self.canvas.itemconfig(self.item,image=self.imagetk)

	def removeBG(self,pixels,c1,c2,X,Y):
		truevar=True
		area=np.zeros((X,Y),dtype=np.int8)
		area[c1,c2]=2
		thr=self.labelThr["text"]
		self.labelThr.config(text="Working!",background="red")
		self.labelThr.update_idletasks()
		while truevar:
			indexs=np.where(area==2)
			area2=np.copy(area)
			for i in range(len(indexs[0])):
				x,y=int(indexs[0][i]),int(indexs[1][i])
				for x1,y1 in self.neighbours(x,y,X,Y):
					if area[x1,y1]==0:
						if self.shouldMove(pixels[x,y],pixels[x1,y1]):
							area[x1,y1]=2
				area[x,y]=1
				pixels[x,y]=(0,0,0,0)
			truevar=False
			if 2 in area:
				truevar=True

#		self.remove_noise(pixels,X,Y)
		self.labelThr.config(text=thr,background="gray")

	def shouldMove(self,C1,C2):
		sum1=0.0
		if C2[-1]==0:
			return False
		for i in range(3):
			sum1+=(C1[i]-C2[i])**2	
		sum1=math.sqrt(sum1)/(255.0*3.0)
		if sum1<self.threshold:
			return True
		return False

	def neighbours(self,x,y,XX,YY):
		if x+1<XX and y+1<YY:
			yield (x+1,y+1)
		if y-1>=0 and x+1<XX:
			yield (x+1,y-1)
		if x-1>=0 and y-1>=0:
			yield (x-1,y-1)
		if y+1<YY and x-1>=0:
			yield (x-1,y+1)	
		if x+1<XX:
			yield (x+1,y)
		if y-1>=0:
			yield (x,y-1)
		if x-1>=0:
			yield (x-1,y)
		if y+1<YY:
			yield (x,y+1)	
			
	def remove_noise(self,event=None):
		txt=self.labelThr["text"]
		self.labelThr.config(text="Removing Noise",background="yellow")
		self.labelThr.update_idletasks()
		mat=self.image.load()
		XX,YY=self.image.size
		change=True
		indexs=[[],[]]
		for x in range(XX):
			for y in range(YY):
				if mat[x,y][-1]>0:
					indexs[0].append(x)
					indexs[1].append(y)
		while change:
			change=False
			for i in range(len(indexs[0])):
				x,y=int(indexs[0][i]),int(indexs[1][i])
				if mat[x,y][-1]!=0:
					k=0
					for (x1,y1) in rs.neighbours(x,y,XX,YY):
						if mat[x1,y1][-1]!=0: 
							k+=1
					if k<2:
						temp=list(mat[x,y])
						temp[-1]=0
						mat[x,y]=tuple(temp)
						change=True
		self.updateCanvas()		
		self.labelThr.config(text=txt,background="gray")

def main(input_image_path,out_image_path):
	window = tk.Tk()
	try:
		img=Image.open(input_image_path)
	except:
		print "\tInvalid Image"
		exit()
	app=myApp(window,img)
	window.mainloop()
	img=app.image
	print "\tSaving Image..."
	img.save(out_image_path,"PNG")

if __name__=="__main__":
	try:
		path=argv[1]
		out_path=argv[2]
	except:
		print "Please provide the input file name and output file name"
		exit()
	print "Doing image: ",path
	main(argv[1],argv[2])
