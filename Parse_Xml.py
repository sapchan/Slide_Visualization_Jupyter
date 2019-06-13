import xml.etree.ElementTree as ET
import numpy as np
from bs4 import BeautifulSoup
import openslide as ops
from PIL import Image, ImageDraw, ImageColor
import timeit
import cv2
"""
So the most important function here is create_mask_for_color

    Functions:
        print_all_colors: No Input, No Output
        
        get_all_regions: Inputs -> int Aperio_ImageScope_Color
                        Outputs -> list XML_tree
        
        get_number_of_regions_in_each_annotation_group: Inputs -> int Aperio_ImageScope_Color
                                                       Outputs -> None

        place_points_in_dict_per_region: Inputs -> int Aperio_ImageScope_Color
                                        Outputs -> dict with structure [int region #]: np.array([x1,y1,x2,y2,...])

        create_mask_for_color: Inputs -> int Aperio_ImageScope_Color
                                      -> String Image_File_Path
                              Outputs -> np.array Binary Mask

        extract_ROI: Inputs -> int Aperio_ImageScope_Color
                    Outputs -> np.array BGR Image

"""
class Parse_Xml():
    def __init__(self, xmlPath, svsPath):
        infile = open(xmlPath,"r")
        contents = infile.read()
        self.soup = BeautifulSoup(contents,'lxml')
        self.print_all_colors()
        self.svsPath = svsPath
#        startTime = timeit.default_timer()
#        self.img = self.create_mask_for_color(255,'examples/36724.svs')
#        self.get_bounding_box_around_mask(8454143)
#        self.get_bounding_box_around_mask(img)
#        endTime = timeit.default_timer()
#        print('Time: ', endTime - startTime)
#        dict_regions = self.place_points_in_dict_per_region(8454143)
#        for key,val in dict_regions.items():
#            print(val)
#            print("\n")

    def print_all_colors(self):
        print('Annotation Colors Present:')
        for group in self.soup.find_all('annotation'):
            print(group.get('linecolor'))

    def get_all_regions(self,color):
        regions = self.soup.find(linecolor = color).find_all('region')
        return regions

    def get_number_of_regions_in_each_annotation_group(self,color):
        regions = self.get_all_regions(color)
        print('# Regions: ' , len(regions))

    def place_points_in_dict_per_region(self,color):
        regions = self.get_all_regions(color)
        dict_regions = {}
        for idx,each_region in enumerate(regions):
            arr = np.array([])
            for each_vertex in each_region.find_all('vertex'):
                x = int(float(each_vertex.get('x')))
                arr = np.append(arr,x)
                y = int(float(each_vertex.get('y')))
                arr = np.append(arr,y)
            dict_regions[idx] = arr
        return dict_regions

    def create_mask_for_color(self,color):
        dict_regions = self.place_points_in_dict_per_region(color)
        slide = ops.open_slide(self.svsPath)
#        (w, h) = slide.dimensions
#        print((w,h))
        (min_x, min_y, max_x, max_y) = self.get_bounding_box_around_mask(color)
        w = max_x - min_x
        h = max_y - min_y
        img = Image.new('L',(w,h),0)
        for key,val in dict_regions.items():
            val[0::2] = val[0::2] - min_x
            val[1::2] = val[1::2] - min_y
            ImageDraw.Draw(img).polygon(val.tolist(),outline=1,fill=1)
        img = np.array(img)
        return img

    def get_bounding_box_around_mask(self,color):
        regions = self.get_all_regions(color)
        all_x = np.array([])
        all_y = np.array([])
        for idx,each_region in enumerate(regions):
            for each_vertex in each_region.find_all('vertex'):
                all_x = np.append(all_x,int(float(each_vertex.get('x'))))
                all_y = np.append(all_y,int(float(each_vertex.get('y'))))

        min_x = int(np.min(all_x))
        max_x = int(np.max(all_x))
        min_y = int(np.min(all_y))
        max_y = int(np.max(all_y))
        return (min_x, min_y, max_x, max_y)

    def extract_ROI(self,color):
        # first get the bounding box for the annotation
        (min_x, min_y, max_x, max_y) = self.get_bounding_box_around_mask(color)

        # next extract the max using the annotation
        mask = self.create_mask_for_color(color)

        # So that you don't have to re-run create_mask_for_color
        self.bm = mask

        # load the image using openslide
        x = min_x
        y = min_y
        w = max_x - min_x
        h = max_y - min_y
        slide = ops.open_slide(self.svsPath)

        # Some slides tend to have a bounds
        try:
            x = x + int(slide.properties['openslide.bounds-x'])
            y = y + int(slide.properties['openslide.bounds-y'])
        except:
            print('No Bounds Detected on Image')

        roi = np.array(slide.read_region((x,y),0,(w,h)))

        # take the bitwise and operation to get only the desired ROI
        res = cv2.bitwise_and(roi,roi, mask = mask)
        return res
        
    def refitToScreenSize(self,img):
#        width_screen = NSScreen.mainScreen().frame().size.width
#        height_screen = NSScreen.mainScreen().frame().size.height
        width_screen = 1280
        height_screen = 800
        width, height, channel = img.shape
       
        screen_size = np.array((width_screen,height_screen))
        image_size = np.array((width,height))
        
        resize_factor = screen_size[np.argmin(screen_size)]/image_size[np.argmin(screen_size)]
        resize_factor = resize_factor*.8
        newWidth,newHeight = image_size[0]*resize_factor, image_size[1]*resize_factor

        img = cv2.resize(img,(int(newWidth),int(newHeight)))
        return img

        
#pxml = Parse_Xml("examples/GLEE029.xml","examples/GLEE029.scn")
#startTime = timeit.default_timer()
#ROI = pxml.extract_ROI(65280)
#stopTime = timeit.default_timer()
#print("Time: ", stopTime - startTime)
#resized_ROI = pxml.refitToScreenSize(ROI)
#new_im = Image.fromarray(resized_ROI)
#new_im.show()
