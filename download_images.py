#from xml.etree.ElementTree import iterparse
import csv
import unicodedata
import re
import os
from sys import argv,exit
try:
	from xml.etree import cElementTree as etree
except:
	print "Unable to load cElementTree, install it first "
import datetime
import urllib

def parseXML(infile,outfolder):
	print "Begin Parsing feed"
	if not os.path.exists(outfolder):
		os.makedirs(outfolder)
	regex=re.compile("'")
	with open(infile,"rb") as f:
		k=True
		proddict={}
		attribs=["productid","imageurl"]
		for event,elem in etree.iterparse(f):
#		for event,elem in iterparse(f):
			if elem.tag=="FC_Product_Catalog":
				print "End of XML File"
				break
			if elem.tag=="Product":
				prod={}
				for child in elem.iter():
					if child.tag=="Product":
						continue
#					if child.tag=="ProductName":
#						print "Current: ",child.text
					if child.text!=None:
						txt=child.text.encode("utf8")
					else:
						txt=None
					if child.tag in attribs:
						prod[child.tag]=txt
				prodid=prod["productid"]
				if not os.path.exists(outfolder+"/"+prodid):	
					imageurl=prod["imageurl"]
					print "Now downloading ",prodid
					urllib.urlretrieve(imageurl,outfolder+"/"+prodid)
					elem.clear()			
				else:
					print prodid," already present"
	print "XML Parsing done!"
	print "all Image downloaded to " + outfolder

if __name__=="__main__":
	try:
		feed=argv[1]
		outfolder=argv[2]
	except:
		print "Provide the following arguments"
		print "1.Input feed file"
		print "2.Outpt folder name"
		exit()
	parseXML(feed,outfolder)

