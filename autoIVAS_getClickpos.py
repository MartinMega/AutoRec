# -*- coding: utf-8 -*-
"""
Created on Mon Mar 30 21:52:51 2020

@author: Martin
"""

import os
import time
from PIL import Image
from PIL import ImageGrab
from time import sleep 
import pytesseract
import numpy as np
import regex


pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'



def clickPosByText(TextToSearch, boundingBox = None, extendBoundingBox = False):
    #Find the position of some text,  eg a button on the screen
    #bbox left_x, top_y, right_x, bottom_y
    #Take screenshot. Either a section or the entire screen.
    if (boundingBox == None):
        extendBoundingBox = False
        
    screenshot_image = ImageGrab.grab(bbox = boundingBox, include_layered_windows=True)
        
    #Text the text
    pytessoutput = pytesseract.image_to_data(image=screenshot_image, output_type=pytesseract.Output.DICT)
    
    #Put all the output in numpy arrays    
    foundtext = np.array(pytessoutput.get('text'))
    leftpos = np.array(pytessoutput.get('left'))
    toppos = np.array(pytessoutput.get('top'))
    widthpos = np.array(pytessoutput.get('width'))
    heightpos = np.array(pytessoutput.get('height'))
    
    #Do a regex-scan to check wether the specified text has been found in the image. The current regex does fuzzy matching!
    regexToSearch = str("(.*") + str(TextToSearch) + str(".*){e<=1}")
    matchElement = lambda inputTxt: (regex.match(regexToSearch,inputTxt) != None)
    matchVec = np.vectorize(matchElement)
    TextFoundIn = np.argwhere(matchVec(foundtext))
    
    if TextFoundIn.size == 0:
        if extendBoundingBox:
            [Clickpos_X, Clickpos_Y] = clickPosByText(TextToSearch, boundingBox=None)
            raise UserWarning("Text not found - extending search area to entire screen")
        else:
            #print(foundtext)
            raise UserWarning("Text not found on entire screen - cannot return clickposition")
    elif TextFoundIn.size > 1:
        #print(foundtext)
        raise UserWarning("Text found multiple times on screen - cannot return click position")
    else:
        #We found that we want!
        targetIndex = TextFoundIn[0]
        Clickpos_X = int(leftpos[targetIndex] + 0.5*widthpos[targetIndex])
        Clickpos_Y = int(toppos[targetIndex] + 0.5*heightpos[targetIndex])
        
    return [Clickpos_X, Clickpos_Y]
            
            
    

def isTextOnScreen(TextToSearch, boundingBox = None, extendBoundingBox = False):
    #Check wether a certain text is visible on the screen
    #bbox left_x, top_y, right_x, bottom_y
    #Take screenshot. Either a section or the entire screen.
    if (boundingBox == None):
        extendBoundingBox = False
        
    screenshot_image = ImageGrab.grab(bbox = boundingBox, include_layered_windows=True)
        
    #Text the text
    pytessoutput = pytesseract.image_to_data(image=screenshot_image, output_type=pytesseract.Output.DICT)
    
    #Put all the output in numpy arrays    
    foundtext = np.array(pytessoutput.get('text'))
    leftpos = np.array(pytessoutput.get('left'))
    toppos = np.array(pytessoutput.get('top'))
    widthpos = np.array(pytessoutput.get('width'))
    heightpos = np.array(pytessoutput.get('height'))
    #print(foundtext)
    
    #Do a regex-scan to check wether the specified text has been found in the image. The current regex does fuzzy matching!
    regexToSearch = str("(.*") + str(TextToSearch) + str(".*){e<=1}")
    matchElement = lambda inputTxt: (regex.match(regexToSearch,inputTxt) != None)
    matchVec = np.vectorize(matchElement)
    TextFoundIn = np.argwhere(matchVec(foundtext))
    
    
    if TextFoundIn.size == 0:
        if extendBoundingBox:
            [Clickpos_X, Clickpos_Y] = clickPosByText(TextToSearch, boundingBox=None)
            raise UserWarning("Text not found in boundingbox - extending search area to entire screen")
        else:
            return False
    else:
        return True


def waitForTextOnScreen(TextToSearch, boundingBox = None, extendBoundingBox = False, timeout = None, checkinterval = 5):
    #wait until a given text shows up on the screen. Throw error if timeout is reached before error shows up (the timeout might not exactly kept)
    if timeout == None:
        timeout = float("inf")   
    starttime = time.time()
    while (time.time() - starttime < timeout):
        if isTextOnScreen(TextToSearch, boundingBox, extendBoundingBox):
            return
        time.sleep(checkinterval)
    raise IOError("timeout reached and text not found")