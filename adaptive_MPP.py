import numpy as np
import openslide as ops
from openslide import deepzoom
from PIL import Image, ImageDraw, ImageColor
from openslide import deepzoom
import cv2
from Parse_Xml import Parse_Xml

class Adaptive_MPP():
    def __init__(self, xmlPath, svsPath, color, patch_size, mag):
        self.pxml = Parse_Xml(xmlPath,svsPath)
        self.xmlPath = xmlPath
        self.svsPath = svsPath
        self.color = color
        self.patch_size = patch_size
        self.dict_mag_level = self.buildDictionary()
        print(self.dict_mag_level)
        self.mag = mag
        assert (float(self.mag) in self.dict_mag_level), 'Please Choose Valid Magnification'
        self.roi = self.extract_roi()


    def extract_roi(self):
        # get useful information
        start_col,start_row,end_col,end_row = self.find_tile_in_dz()
        slide = ops.open_slide(self.svsPath)
        dz = deepzoom.DeepZoomGenerator(slide,tile_size=self.patch_size,overlap=0, limit_bounds=True)
        level = self.dict_mag_level[self.mag]
        print("level: ", level)
        #initialize empty array the size of the ROI we need
        w = (end_col - start_col) * self.patch_size
        h = (end_row - start_row) * self.patch_size
        io = np.zeros((h,w,3),dtype='uint8')

        # not sure if it should by y,x or x,y but either all of the rows and columns needs to be flipped
        for i in range(start_col,end_col):
            for j in range(start_row,end_row):
                patch = dz.get_tile(level, (i, j))
                x_start = (i - start_col)*self.patch_size
                x_end = x_start + self.patch_size
                y_start = (j - start_row)*self.patch_size
                y_end = y_start+self.patch_size
                io[y_start:y_end , x_start:x_end , :] = patch
        
        return io

    def find_tile_in_dz(self):
        # get useful information
        (min_x, min_y, max_x, max_y) = self.get_bounding_box_around_mask(self.color)
        print(min_x, min_y, max_x, max_y)
        # get the start tile and end tile information
        start_col = np.divmod(min_x,self.patch_size)[0]
        start_row = np.divmod(min_y,self.patch_size)[0]
        end_col = np.divmod(max_x,self.patch_size)[0]+1
        end_row = np.divmod(max_y,self.patch_size)[0]+1

        print(start_col,start_row,end_col,end_row)
        return (start_col,start_row,end_col,end_row)


    def get_slide_tile_information(self):
        slide = ops.open_slide(self.svsPath)
        dz = deepzoom.DeepZoomGenerator(slide,tile_size=self.patch_size,overlap=0, limit_bounds=True)
        level = self.dict_mag_level[mag]
        w,h = dz.level_dimensions[level]
        n,m = dz.level_tiles[level]
        return (n,m,w,h)

    def buildDictionary(self):
        slide = ops.open_slide(self.svsPath)
        dz = deepzoom.DeepZoomGenerator(slide,tile_size=self.patch_size,overlap=0, limit_bounds=True)
        levels = dz.level_count
        max_mag = int(slide.properties['openslide.objective-power'])
        counter = 1
        dict_level_mag_correspondence = {}
        for i in reversed(range(0,levels)):
            dict_level_mag_correspondence[max_mag/counter] = i
            counter = counter*2
        return dict_level_mag_correspondence

    def get_bounding_box_around_mask(self,color):
        # if so, then determine how much to resize things by for the bounding box
        slide = ops.open_slide(self.svsPath)
        dz = deepzoom.DeepZoomGenerator(slide,tile_size=self.patch_size,overlap=0, limit_bounds=True)
        max_mag = int(slide.properties['openslide.objective-power'])
        resize_factor = float(self.mag/max_mag)

        # determine the original bounding box from the annotation
        regions = self.pxml.get_all_regions(color)
        all_x = np.array([])
        all_y = np.array([])
        for idx,each_region in enumerate(regions):
            for each_vertex in each_region.find_all('vertex'):
                all_x = np.append(all_x,int(float(each_vertex.get('x'))))
                all_y = np.append(all_y,int(float(each_vertex.get('y'))))

        all_x = all_x * resize_factor
        all_y = all_y * resize_factor
        # apply resize factor
        min_x = int(np.min(all_x))
        max_x = int(np.max(all_x))
        min_y = int(np.min(all_y))
        max_y = int(np.max(all_y))

        return (min_x, min_y, max_x, max_y)

app = Adaptive_MPP("examples/36724.xml","examples/36724.svs",16776960,256, 20)
roi = app.roi
new_im = Image.fromarray(roi)
new_im.show()