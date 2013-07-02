import os 
import operator,itertools
import numpy as np
import math
from PIL import Image,ImageColor
#from skimage import color

def glowPixels(x,y,(c1,c2),n=3):
	deltax=x-c1
	deltay=y-c2
	if deltax==0:
		if y>c2:
			for i in range(0,n):
				yield (x,y-i)
		else:
			for i in range(0,n):
				yield (x,y+i)
	else:	
		error=0.0
		deltaerr=abs(float(deltay)/float(deltax))
		y1=y
		ct=1
		if y1<c2:
			if x>c1:
				ct=-1
				n=-1*n
			if len(range(0,n,ct))==0:
				print "sucks"
				raw_input()
			for i in range(0,n,ct):
				x1=x+i
				yield (x1,y1)
				error=error+deltaerr
				if error>=0.5:
					y1+=1
					error-=1.0
		else:
			if x>c1:
				ct=-1
				n=-1*n
			if len(range(0,n,ct))==0:
				print "sucks"
				raw_input()
			for i in range(0,n,ct):
				x1=x+i
				yield (x1,y1)
				error=error+deltaerr
				if error>=0.5:
					y1-=1
					error-=1.0

def neighbours(x,y,XX,YY):
	if x+1<XX:
		yield (x+1,y)
	if y-1>=0:
		yield (x,y-1)
	if x-1>=0:
		yield (x-1,y)
	if y+1<YY:
		yield (x,y+1)	

def crossNeighbours(x,y,XX,YY):
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

def rgbToHsl(lst):
	E=0.00001
	r,g,b=lst
	r/=255.0
	g/=255.0 
	b/=255.0
	max1 = max([r,g,b])
	min1 = min([r,g,b])
	l=(max1+min1)/2;

	if max1-min1<E:
		h=s=0
	else:
		d=max1 - min1
		if l>0.5:
			s=d/float(2-max1-min1)
		else:
			s=d/float(max1+min1)
		if max1-r<E:
			if g<b:
				h =(g-b)/float(d) + 6.0
			else:
				h =(g-b)/float(d) 
		elif max1-g<E: 
			h = (b-r)/float(d) + 2.0
		elif max1-b<E:
			h = (r-g)/float(d) + 4.0
		else:
			print "Eror"
			raw_input()
		h/=6.0
	return [h,s,l]

def shouldMove(C1,C2,thres=None):
	if thres!=None:
		return shouldMoveLA_thres(C1,C2,thres)
	else:
		return shouldMoveLA(C1,C2)

def shouldMoveLA_thres(C1,C2,thresC):
	if C2[1]==0:
		return False
	if abs(C2[1]-C1[0])<thresC:
		return True
	return False

def shouldMoveLA(C1,C2):
	if C2[1]==0:
		return False
	if abs(C2[0]-C1[0])<5:
		return True
	return False

# Based on HSL
def shouldMoveHSL(C1,C2):
	if C2[3]==0:
		return False
	h1=rgbToHsl(list(C1)[:3])
	h2=rgbToHsl(list(C2)[:3])
	if abs(h1[0]-h2[0])<.2 and abs(h1[1]-h2[1])<.01 and abs(h1[2]-h2[2])<.01:
		return True
	return False



# Based on gray scale
def shouldMove3(C1,C2):
	if C2[3]==0:
		return False
	gs1=.11*float(C1[2])+.59*float(C1[1])+.30*float(C1[0])
	gs2=.11*float(C2[2])+.59*float(C2[1])+.30*float(C2[0])
	diff=abs(gs1-gs2)/2.56	
	if diff<1.5:
		return True
	return False

# Based on L*a*b*, expensive, not going to use it
def shouldMove1(C1,C2):
	if C2[3]==0:
		return False
	x,y=np.zeros((1,1,3)),np.zeros((1,1,3))
	x[0,0]=list(C1)[:3]
	y[0,0]=list(C2)[:3]
	lab1=color.rgb2lab(x)
	lab2=color.rgb2lab(y)
	Eab=0.0
	for i in range(3):
		Eab+=(lab1[0,0,i]-lab2[0,0,i])**2
	Eab=math.sqrt(Eab)
	if Eab<1.0:
		return True
	return False

# Based on simple sqrt diff between RGB values
def shouldMoveRGB(C1,C2):
	sum2=0
	if C2[3]==0:
		return False
	for i in range(3):
		sum2+=(C1[0]-C2[0])**2
	sum2=math.sqrt(sum2)/(255.0*3.0)
	if sum2<.01: 
		return True
	return False

def genBoundary(mat,XX,YY):
	bound=np.zeros((XX,YY),np.int8)
	for x in range(XX):
		for y in range(YY):
			if mat[x,y][-1]!=0:
				k,km=0,0
				for x1,y1 in neighbours(x,y,XX,YY):
					if mat[x1,y1][-1]!=0:
						k+=1
					km+=1
				if k<km and k>0:
					bound[x,y]=1
					mat[x,y]=(0,0,0,255)
	return bound

	"""
	bound1=np.zeros((XX,YY),dtype=np.int8)
	bound2=np.zeros((XX,YY),dtype=np.int8)
	bound3=np.zeros((XX,YY),dtype=np.int8)
	bound4=np.zeros((XX,YY),dtype=np.int8)
	rxy=itertools.product(range(XX),range(YY))
	for y in range(YY):
		bound1[0,y]=1
		bound2[XX-1,y]=1
	for x in range(XX):
		bound3[x,0]=1
		bound4[x,YY-1]=1
	truevar=True
	x=0
	while truevar:
		for y in range(YY):
			if bound1[x,y]==1:
				bound1[x,y]=0
				if mat[x,y][-1]>0:
					bound1[x,y]=2
				elif x+1<XX:
					bound1[x+1,y]=1
				if x+1<XX:
					for i in range(y-1,-1,-1):
						if mat[x+1,i][-1]==0:
							bound1[x+1,i]=1
						else:
							break
					for i in range(y+1,YY):
						if mat[x+1,i][-1]==0:
							bound1[x+1,i]=1
						else:
							break
		x+=1
			
		truevar=False
		if x<XX:
			for y in range(YY):
				if bound1[x,y]==1:
					truevar=True
					break
	truevar=True
	x=XX-1
	while truevar:
		for y in range(YY):
			if bound2[x,y]==1:
				bound2[x,y]=0
				if mat[x,y][-1]>0:
					bound2[x,y]=2
				elif x-1>=0:
					bound2[x-1,y]=1
				if x-1>=0:
					for i in range(y-1,-1,-1):
						if mat[x-1,i][-1]==0:
							bound2[x-1,i]=1
						else: 
							break
					for i in range(y+1,YY):
						if mat[x-1,i][-1]==0:
							bound2[x-1,i]=1
						else: 
							break
		x-=1
		truevar=False
		if x>=0:
			for y in range(YY):
				if bound2[x,y]==1:
					truevar=True
					break

	truevar=True
	y=0
	while truevar:
		for x in range(XX):
			if bound3[x,y]==1:
				bound3[x,y]=0
				if mat[x,y][-1]>0:
					bound3[x,y]=2
				elif y+1<YY:
					bound3[x,y+1]=1
				if y+1<YY:
					for i in range(x-1,-1,-1):
						if mat[i,y+1][-1]==0:
							bound3[i,y+1]=1
						else:
							break
					for i in range(x+1,XX):
						if mat[i,y+1][-1]==0:
							bound3[i,y+1]=1
						else:
							break

		y+=1
		truevar=False
		if y<YY:
			for x in range(XX):
				if bound3[x,y]==1:
					truevar=True
					break

	truevar=True
	y=YY-1	
	while truevar:
		for x in range(XX):
			if bound4[x,y]==1:
				bound4[x,y]=0
				if mat[x,y][-1]>0:
					bound4[x,y]=2
				elif y-1>=0:
					
					bound4[x,y-1]=1
				if y-1>=0:
					for i in range(x-1,-1,-1):
						if mat[i,y-1][-1]==0:
							bound4[i,y-1]=1
						else:
							break
					for i in range(x+1,XX):
						if mat[i,y-1][-1]==0:
							bound4[i,y-1]=1
						else:
							break
		y-=1
		truevar=False
		if y>=0:
			for x in range(XX):
				if bound4[x,y]==1:
					truevar=True
					break
				
				
	bound=np.zeros((XX,YY),dtype=np.int8)
	indexs=np.where((bound1==2)|(bound2==2)|(bound3==2)|(bound4==2))
	for i in range(len(indexs[0])):
		x,y=int(indexs[0][i]),int(indexs[1][i])
		for x1,y1 in crossNeighbours(x,y,XX,YY):
			if mat[x1,y1][-1]==0:
				bound[x1,y1]=1	
	return bound
	"""
def glow(mat,XX,YY,toMove):
	dist=int(XX/100)
	trans=32.0
	print "\tGlow radius is ",dist
	indexs=np.where(toMove==2)	
	X=len(indexs[0])
	for k in range(X):
		x,y=int(indexs[0][k]),int(indexs[1][k])
		x=int(x+dist-2)		
		for j in range(dist):
			if x-j<0:
				break
			temp=list(mat[x-j,y])
			temp[3]=int(trans*float(1.0-float(j+1)/float(dist)))
			mat[x-j,y]=tuple(temp)
		
		
	indexs=np.where(toMove==3)	
	X=len(indexs[0])
	for k in range(X):
		x,y=int(indexs[0][k]),int(indexs[1][k])
		x=int(x-dist+2)		
		for j in range(dist):
			if x+j>=(XX-1):
				break
			temp=list(mat[x+j,y])
			temp[3]=int(trans*float(1.0-float(j+1)/float(dist)))
			mat[x+j,y]=tuple(temp)
	return mat

def remove_noise(mat,XX,YY,toMove,toMove2=None):
	if toMove2==None:
		toMove2=np.zeros((XX,YY))
		
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
				for (x1,y1) in neighbours(x,y,XX,YY): 				
					if mat[x1,y1][-1]!=0: 
						k+=1
				if k<2:
					temp=list(mat[x,y])
					temp[-1]=0
					mat[x,y]=tuple(temp)
					change=True
	indexs=np.where((toMove>1) | (toMove2>1))
	for i in range(len(indexs[0])):
		x,y=int(indexs[0][i]),int(indexs[1][i])
		if toMove[x,y]==2 and mat[x+1,y][-1]==0:
			toMove[x,y]=0
		if toMove[x,y]==3 and mat[x-1,y][-1]==0:
			toMove[x,y]=0
		if toMove2[x,y]==4 and mat[x,y+1][-1]==0:
			toMove2[x,y]=0
		if toMove2[x,y]==5 and mat[x,y-1][-1]==0:
			toMove2[x,y]=0
	return mat,toMove,toMove2

def radial_glow(mat,XX,YY,toMove,toMove2,n=2):
	indexs=np.where((toMove>1) | (toMove2>1))
	center=[0,0]
	for i in range(len(indexs[0])):
		x,y=int(indexs[0][i]),int(indexs[1][i])	
		center[0]+=x
		center[1]+=y
#		mat[x,y]=(0,0,0,255)

	center[0]/=len(indexs[0])
	center[1]/=len(indexs[1])
	bound=genBoundary(mat,XX,YY)
	indexs=np.where((bound==1))
	start=128
	diff=(255-start)/n
	for i in range(len(indexs[0])):
		x2,y2=int(indexs[0][i]),int(indexs[1][i])
#		mat[x2,y2]=(0,0,0,255)
		trans=start
		g=glowPixels(x2,y2,center,n)
		x,y=g.next()
		x,y=x1,y1=g.next()

		cont=True
		while cont:
			if mat[x1,y1]!=(0,0,0,0):
				temp=list(mat[x1,y1])
				temp[3]=trans
				mat[x1,y1]=tuple(temp)
				trans+=diff
			try:
				(x1,y1)=g.next()
			except StopIteration:
				cont=False
		
	return mat,bound

def getThresholdColor(img2):
	img=img2.copy()
	XX=8
	YY=int(XX*float(img.size[1])/float(img.size[0]))
	img.thumbnail((XX,YY),Image.ANTIALIAS)
	img=img.convert('LA')
	pixels=img.load()
	lst=[pixels[i,j][0] for (i,j) in itertools.product(range(XX),range(YY)) ]
	diff=max(lst)-min(lst)
	return diff/10

def region_shrink4(img,XX,YY):
	mat_color=img.load()
	pixels=img.convert('LA').load()
	toMove=np.zeros((XX,YY),dtype=np.int8)
	toMove2=np.zeros((XX,YY),dtype=np.int8)
	bg=Image.new("LA",(XX,YY))
	bg2=Image.new("LA",(XX,YY))
	mat=bg.load()
	mat2=bg2.load()
	
	thresC=getThresholdColor(img)

	for x in range(XX):
		for y in range(YY):
			mat[x,y]=pixels[x,y]
			mat2[x,y]=pixels[x,y]
			
	for y in range(YY):
		toMove[0,y]=1
		toMove[XX-1,y]=1	
	for x in range(XX):
		toMove2[x,0]=1
		toMove2[x,YY-1]=1	
	# Shrink Boundary

	x1=0
	x2=XX-1
	truevar=True
	trans=0
	while truevar:
		for y in range(YY):
			if toMove[x1,y]==1:
				toMove[x1,y]=2
				if shouldMove(mat[x1,y],mat[x1+1,y],thresC):
					toMove[x1+1,y]=1
					toMove[x1,y]=0
				if y-1>=0:
					if shouldMove(mat[x1,y],mat[x1+1,y-1],thresC):
						toMove[x1+1,y-1]=1
				if y+1<YY:
					if shouldMove(mat[x1,y],mat[x1+1,y+1],thresC):
						toMove[x1+1,y+1]=1
				temp1=list(mat[x1,y])
				temp1[1]=trans
				mat[x1,y]=tuple(temp1)
				if mat[x1+1,y][-1]==0:
					toMove[x1,y]=0
					
						
		x1+=1
		for y in range(YY):
			if toMove[x2,y]==1:
				toMove[x2,y]=3
				if shouldMove(mat[x2,y],mat[x2-1,y],thresC):
					toMove[x2-1,y]=1
					toMove[x2,y]=0
				if y-1>=0:
					if shouldMove(mat[x2,y],mat[x2-1,y-1],thresC):
						toMove[x2-1,y-1]=1	
				if y+1<YY:
					if shouldMove(mat[x2,y],mat[x2-1,y+1],thresC):
						toMove[x2-1,y+1]=1
				temp1=list(mat[x2,y])
				temp1[1]=trans
				mat[x2,y]=tuple(temp1)
				if mat[x2-1,y][-1]==0:
					toMove[x2,y]=0
		x2-=1
		truevar=False
		for y in range(YY):
			if toMove[x1,y]==1 or toMove[x2,y]==1:
				truevar=True
				break

	y1=0
	y2=YY-1
	truevar=True
	trans=0
	while truevar:
		for x in range(XX):
			if toMove2[x,y1]==1:
				toMove2[x,y1]=4
				if shouldMove(mat2[x,y1],mat2[x,y1+1],thresC):
					toMove2[x,y1+1]=1
					toMove2[x,y1]=0
				if x-1>=0:
					if shouldMove(mat2[x,y1],mat2[x-1,y1+1],thresC):
						toMove2[x-1,y1+1]=1
				if x+1<XX:
					if shouldMove(mat2[x,y1],mat2[x+1,y1+1],thresC):
						toMove2[x+1,y1+1]=1
				temp1=list(mat2[x,y1])
				temp1[1]=trans
				mat2[x,y1]=tuple(temp1)
				if mat2[x,y1+1][-1]==0:
					toMove2[x,y1]=0
		y1+=1

		for x in range(XX):
			if toMove2[x,y2]==1:
				toMove2[x,y2]=5
				if shouldMove(mat2[x,y2],mat2[x,y2-1],thresC):
					toMove2[x,y2-1]=1
					toMove2[x,y2]=0
				if x-1>=0:
					if shouldMove(mat2[x,y2],mat2[x-1,y2-1],thresC):
						toMove2[x-1,y2-1]=1
				if x+1<XX:
					if shouldMove(mat2[x,y2],mat2[x+1,y2-1],thresC):
						toMove2[x+1,y2-1]=1
				temp1=list(mat2[x,y2])
				temp1[1]=trans
				mat2[x,y2]=tuple(temp1)
				if mat2[x,y2-1][-1]==0:
					toMove2[x,y2]=0

		y2-=1
		truevar=False
		for x in range(XX):
			if toMove2[x,y1]==1 or toMove2[x,y2]==1:
				truevar=True
				break

		


	# End Shrinking

	# Glow Code
	
		# Finding index of all forward boundaries


	# End Glow
	bg3=Image.new("RGBA",(XX,YY))
	mat3=bg3.load()
	for x in range(XX):
		for y in range(YY):
			if mat[x,y]==mat2[x,y] and mat[x,y][1]>0 and mat2[x,y][1]>0:
				mat3[x,y]=tuple(list(mat_color[x,y])+[255])
			else:
				mat3[x,y]=(0,0,0,0)
	mat3,toMove,toMove2=remove_noise(mat3,XX,YY,toMove,toMove2)
	mat3,boundary=radial_glow(mat3,XX,YY,toMove,toMove2)	
#	bg.save(out_dir+"/.png","PNG")
	return bg3,thresC


def region_shrink3(img,XX,YY):
	mat_color=img.load()
	pixels=img.convert('LA').load()
	toMove=np.zeros((XX,YY),dtype=np.int8)
	toMove2=np.zeros((XX,YY),dtype=np.int8)
	bg=Image.new("LA",(XX,YY))
	bg2=Image.new("LA",(XX,YY))
	mat=bg.load()
	mat2=bg2.load()
	
	thresC=getThresholdColor(img)

	for x in range(XX):
		for y in range(YY):
			mat[x,y]=pixels[x,y]
			mat2[x,y]=pixels[x,y]
			
	for y in range(YY):
		toMove[0,y]=1
		toMove[XX-1,y]=1	
	for x in range(XX):
		toMove2[x,0]=1
		toMove2[x,YY-1]=1	
	# Shrink Boundary

	x1=0
	x2=XX-1
	truevar=True
	trans=0
	while truevar:
	
		for y in range(YY):
			if toMove[x1,y]==1:
				toMove[x1,y]=2
				if shouldMove(mat[x1,y],mat[x1+1,y],thresC):
					toMove[x1+1,y]=1
					toMove[x1,y]=0
				if y-1>=0:
					if shouldMove(mat[x1,y],mat[x1+1,y-1],thresC):
						toMove[x1+1,y-1]=1
				if y+1<YY:
					if shouldMove(mat[x1,y],mat[x1+1,y+1],thresC):
						toMove[x1+1,y+1]=1
				temp1=list(mat[x1,y])
				temp1[1]=trans
				mat[x1,y]=tuple(temp1)
				if mat[x1+1,y][-1]==0:
					toMove[x1,y]=0
					
						
		x1+=1
		for y in range(YY):
			if toMove[x2,y]==1:
				toMove[x2,y]=3
				if shouldMove(mat[x2,y],mat[x2-1,y],thresC):
					toMove[x2-1,y]=1
					toMove[x2,y]=0
				if y-1>=0:
					if shouldMove(mat[x2,y],mat[x2-1,y-1],thresC):
						toMove[x2-1,y-1]=1	
				if y+1<YY:
					if shouldMove(mat[x2,y],mat[x2-1,y+1],thresC):
						toMove[x2-1,y+1]=1
				temp1=list(mat[x2,y])
				temp1[1]=trans
				mat[x2,y]=tuple(temp1)
				if mat[x2-1,y][-1]==0:
					toMove[x2,y]=0
		x2-=1
		truevar=False
		for y in range(YY):
			if toMove[x1,y]==1 or toMove[x2,y]==1:
				truevar=True
				break

	y1=0
	y2=YY-1
	truevar=True
	trans=0
	while truevar:
		for x in range(XX):
			if toMove2[x,y1]==1:
				toMove2[x,y1]=4
				if shouldMove(mat2[x,y1],mat2[x,y1+1],thresC):
					toMove2[x,y1+1]=1
					toMove2[x,y1]=0
				if x-1>=0:
					if shouldMove(mat2[x,y1],mat2[x-1,y1+1],thresC):
						toMove2[x-1,y1+1]=1
				if x+1<XX:
					if shouldMove(mat2[x,y1],mat2[x+1,y1+1],thresC):
						toMove2[x+1,y1+1]=1
				temp1=list(mat2[x,y1])
				temp1[1]=trans
				mat2[x,y1]=tuple(temp1)
				if mat2[x,y1+1][-1]==0:
					toMove2[x,y1]=0
		y1+=1

		for x in range(XX):
			if toMove2[x,y2]==1:
				toMove2[x,y2]=5
				if shouldMove(mat2[x,y2],mat2[x,y2-1],thresC):
					toMove2[x,y2-1]=1
					toMove2[x,y2]=0
				if x-1>=0:
					if shouldMove(mat2[x,y2],mat2[x-1,y2-1],thresC):
						toMove2[x-1,y2-1]=1
				if x+1<XX:
					if shouldMove(mat2[x,y2],mat2[x+1,y2-1],thresC):
						toMove2[x+1,y2-1]=1
				temp1=list(mat2[x,y2])
				temp1[1]=trans
				mat2[x,y2]=tuple(temp1)
				if mat2[x,y2-1][-1]==0:
					toMove2[x,y2]=0

		y2-=1
		truevar=False
		for x in range(XX):
			if toMove2[x,y1]==1 or toMove2[x,y2]==1:
				truevar=True
				break

		


	# End Shrinking

	# Glow Code
	
		# Finding index of all forward boundaries


	# End Glow
	bg3=Image.new("RGBA",(XX,YY))
	mat3=bg3.load()
	for x in range(XX):
		for y in range(YY):
			if mat[x,y]==mat2[x,y] and mat[x,y][1]>0 and mat2[x,y][1]>0:
				mat3[x,y]=tuple(list(mat_color[x,y])+[255])
			else:
				mat3[x,y]=(0,0,0,0)
	mat3,toMove,toMove2=remove_noise(mat3,XX,YY,toMove,toMove2)
	mat3,boundary=radial_glow(mat3,XX,YY,toMove,toMove2)	
#	bg.save(out_dir+"/.png","PNG")
	return bg3,thresC
