import xml.etree.ElementTree as ET
import numpy as np
from bs4 import BeautifulSoup
import openslide as ops
from PIL import Image, ImageDraw, ImageColor
import timeit
import cv2

class Parse_Xml():
    def __init__(self, xmlPath):
        infile = open(xmlPath,"r")
        contents = infile.read()
        self.soup = BeautifulSoup(contents,'lxml')
#        self.print_all_colors()
        startTime = timeit.default_timer()
        self.create_mask_for_color(255,'examples/36724.svs')
        endTime = timeit.default_timer()
        print('Time: ', endTime - startTime)
#        dict_regions = self.place_points_in_dict_per_region(8454143)
#        for key,val in dict_regions.items():
#            print(val)
#            print("\n")

    def print_all_colors(self):
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

    def create_mask_for_color(self,color,filePath):
        dict_regions = self.place_points_in_dict_per_region(color)
        slide = ops.open_slide(filePath)
        (w, h) = slide.dimensions
        print((w,h))
        img = Image.new('L',(w,h),0)
        for key,val in dict_regions.items():
            ImageDraw.Draw(img).polygon(val.tolist(),outline=1,fill=1)
        img = np.array(img)
        return img
        

Parse_Xml("examples/36724.xml")