import cv2
import numpy as np
import openslide as ops
from AppKit import NSScreen

class ViewSlide():
    
    cur_x = 3000
    cur_y = 13000
    zoom_level = 500

    click_x = cur_x
    click_y = cur_x

    LD = False
    LU = True

    def __init__(self, filePath):
        self.filePath = filePath
        self.slide = self.createSlide()
        self.img = self.getRegion()
        self.img = self.refitToScreenSize(self.img)
        cv2.namedWindow("image")
        cv2.setMouseCallback("image", self.getClickCoordinates)

        while True:
            # display the image and wait for a keypress
            cv2.imshow("image", self.img)
            key = cv2.waitKeyEx(1) & 0xFF
            self.handleKeyUpdate(key)
            if self.LD == True and self.LU == False:
                self.img = self.refitToScreenSize(self.updateRegion(self.click_x,self.click_y))
            # if the 'c' key is pressed, break from the loop
            if key == ord("q"):
                break        
                
        cv2.destroyAllWindows()

    def createSlide(self):
        slide = ops.open_slide(self.filePath)
        return slide

    def getRegion(self):
        if self.zoom_level < 2000:
            img = np.array(self.slide.read_region((self.cur_x,self.cur_y),0,(self.zoom_level,self.zoom_level)))
        else:
            img = np.array(self.slide.read_region((self.cur_x,self.cur_y),1,(self.zoom_level,self.zoom_level)))
        return img

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

    def getClickCoordinates(self, event, x, y, flags, param):
        if event == cv2.EVENT_LBUTTONDOWN:
            self.LD = True
            self.LU = False
            self.click_x = x
            self.click_y = y
        elif event == cv2.EVENT_MOUSEWHEEL:
            print(self.zoom_level)
            self.updateZoomLevel(flags)
            self.img = self.refitToScreenSize(self.getRegion())

        else:
            self.LD = False
            self.LU = True
            self.click_x = self.cur_x
            self.click_y = self.cur_y
            
    def updateZoomLevel(self, flags):
        # in is positive meaning we gotta make the zoom level smaller
        if flags > 0:
            self.zoom_level = self.zoom_level - int(self.zoom_level*.1)

        # out is negative meaning we gotta make the zoom level larger
        else:
            self.zoom_level = self.zoom_level + int(self.zoom_level*.1)

    def updateRegion(self,center_x,center_y):
        # ok so the center_x is entirely based on the openCV window. So the true center is actually
        # at cur_x + center_x. But first center_x needs to be scaled based on the midpoint. So
        # we gotta first do center_x - midpoint
        (x, y, w, h) = cv2.getWindowImageRect('image')
        center_x = center_x - int(w/2)
        center_y = center_y - int(h/2)

        self.cur_x = self.cur_x + center_x
        self.cur_y = self.cur_y + center_y

        img = self.getRegion()

        return img

    def handleKeyUpdate(self, key):
        (x, y, w, h) = cv2.getWindowImageRect('image')
        moveBy = int(self.zoom_level*.2)
        if key != 255:
            print(key)
        if key == 97:
            #left
            self.click_x = int(w/2)-moveBy
            self.click_y = int(h/2)
            self.img = self.refitToScreenSize(self.updateRegion(self.click_x,self.click_y))

        elif key == 119:
            # up
            self.click_x = int(w/2)
            self.click_y = int(h/2)-moveBy
            self.img = self.refitToScreenSize(self.updateRegion(self.click_x,self.click_y))
        
        elif key == 100:
            # right
            self.click_x = int(w/2)+moveBy
            self.click_y = int(h/2)
            self.img = self.refitToScreenSize(self.updateRegion(self.click_x,self.click_y))
        
        elif key == 115:
            #down
            self.click_x = int(w/2)
            self.click_y = int(h/2)+moveBy
            self.img = self.refitToScreenSize(self.updateRegion(self.click_x,self.click_y))