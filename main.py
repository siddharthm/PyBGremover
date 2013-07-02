# Python program to process a feed file, download all images
# and process them to remove background from them automatically
# and then using a tool to manually remove background from
# suspected images

from sys import argv,exit
import interior_removal as ir
import region_shrinking as rs
try:
	from PIL import Image
except:
	print "PIL not installed. Install it before proceeding"
import os
import itertools


la=7
plus=3

def toSuspect(img,omg):
	img_LA=img.convert('RGBA').convert('LA')
	removeObject(img_LA,omg)
	omg_LA=omg.convert('LA')
	bg=getbgColor(img_LA)
	X,Y=img.size
	count,count2=0,0
	pixels=omg.load()
	pixel1=omg_LA.load()
	for x,y in itertools.product(range(X),range(Y)):
		if pixels[x,y][-1]==0:
			continue
		if bg==(la*int((pixel1[x,y][0]+plus)/la)):
			count+=1
		count2+=1
	if count>(count2/200):
		return True
	return False
		
def removeObject(img,omg):
	pixels=img.load()
	pixels2=omg.load()
	X,Y=img.size
	for x,y in itertools.product(range(X),range(Y)):
		if pixels2[x,y][-1]>0:
			pixels[x,y]=(0,0)

def getbgColor(img):
	pixels=img.load()
	X,Y=img.size
	dict2={}
	for x,y in itertools.product(range(X),range(Y)):
		if pixels[x,y][-1]>0:
			key=la*int((pixels[x,y][0]+plus)/la)
			if key not in dict2:
				dict2[key]=0
			dict2[key]+=1
	return max(dict2.items(),key=lambda x:x[1])[0]

def main(in_folder,out_folder):
	if not os.path.exists(out_folder+"/suspect"):
		os.makedirs(out_folder+"/suspect")
	for dirname,dirnames,filenames in os.walk(in_folder):
		for image in filenames:
			imagename=image.split(".")[0]
			print "Now doing image:",image
			img=Image.open(dirname+image)
			if not os.path.exists(out_folder+"/"+imagename+".png") and not os.path.exists(out_folder+"/suspect/"+imagename+".png"):
				omg,thresc=rs.region_shrink3(img,img.size[0],img.size[1])
				if toSuspect(img,omg):
					print "\tSuspected"
					omg.save(out_folder+"/suspect/"+imagename+".png","PNG")
				else:
					omg.save(out_folder+"/"+imagename+".png","PNG")


if __name__=="__main__":
	try:
		in_folder=argv[1]
		out_folder=argv[2]
		if not os.path.exists(out_folder):
			os.makedirs(out_folder)
	except:
		print "Provide the following arguments"
		print "1. Input folder name"
		print "2. Output folder name"
		exit()
	main(in_folder,out_folder)
		
