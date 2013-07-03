Python Background Removal Tool
===========

PyBGremover is a python tool that helps you remove background from images which have near same colour e.g a wall like background.
This project was created for eliminating background from a data set of 40,000+ specific kind of images and thus may not work on all kind of images.

## The project has two independent apps:

### **region_shrinking.py**: 
This app removes the background from around the object and adds a small 2px feather for smoothing the image.
A sample script that uses this has been demonstrated in main.py. main.py checks a directory for all images in it and calls region_shrinking on them.
It then classifies whether the image still has interior background remaining in it and then puts it into a suspect folder.

### **interior_removal.py**:
This is a GUI app that allows you to load an image to it and remove parts of background manually. Clicking on a pixel in image will remove
area similar to it, i.e part of background. You can increase or decrease the threshold of similarity for better results. This app allows you 
to remove polygonal area of images as well. You can view current image in three different background colors. 
A sample script to demonstrate the use of this app, manual.py has been provided. It takes in the output folder of main.py, loads
all suspect images into it, then after manual processing deletes the image from suspect folder and puts in the main folder.

Here's a screenshot of the app, the sample image here is from the output of region_shrinking.py
The image used is from http://photosinbox.com/photos/white-coffee-cup

<p style="text-align:center;"><img src="https://dl.dropboxusercontent.com/u/32781196/Screenshot%20from%202013-07-03%2012%3A54%3A23.png" style="text-align:center;" alt="Screenshot" /></p>

#### The applications require the following additional libraries:
  * PIL
  * Numpy
  * Tkinter (for GUI)
