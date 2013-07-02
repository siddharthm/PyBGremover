from interior_removal import main
import os
from sys import argv,exit


if __name__=="__main__":
	try:
		in_folder=argv[1]
	except:
		print "Please provide input folder name as arguments"
	print "Press Ctrl+C and wait to exit in middle"
	base=in_folder+"/suspect/"
	if not os.path.exists(base):
		print "Input folder does not have any suspect folder. Exiting..."
		exit()
	for dirname,dirs,filenames in os.walk(base):
		for image in filenames:
			print "Starting app for: ",image		
			main(base+image,"test/"+image)
			print "\tDeleting original file"
			#os.remove(base+image)
