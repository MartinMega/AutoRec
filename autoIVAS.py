# -*- coding: utf-8 -*-
"""
Created on Sat Mar 28 22:13:23 2020

@author: Martin
"""




import os
import sys
import time
import logging

import pyautogui

import reconwizard_pages as recwiz
import ivas_controlfunctions as ictrl
#importlib.reload(recwiz.reconwizard_pages)



def IVAS_FullReconstruction(IVASlocation, IVASdirectory, ivas_javaproc_name, dummyRangeFilePath, rhitPath, projectName):
    
    pyautogui.PAUSE = 0.5

    #Go to the path with the IVAS clickimages
    os.chdir('C://Users//Martin//Documents//Spyder//IVASClickImages')
    
    #Launch IVAS
    time.sleep(1)
    starttime = time.time()
    IVASprocess = ictrl.Launch_IVAS(IVASlocation, IVASdirectory, ivas_javaproc_name)
    logging.info("Time for Launch: " + str(time.time() - starttime))

    #Load the dummy range file
    starttime = time.time()
    ictrl.loadDummyRanges(dummyRangeFilePath)
    logging.info("Time for Load Dummy Ranges: " + str(time.time() - starttime))

    #Create new project
    starttime = time.time()
    ictrl.createNewProject(rhitPath, projectName)
    logging.info("Time for create new project : " + str(time.time() - starttime))


    #Go through the reconstruction wizard
    starttime = time.time()
    recwiz.reconwizard_page1()
    logging.info("Time for Rec p1: " + str(time.time() - starttime))

    # second page - we want to export all of the csv file here. the number of csv files that we can expost might vary, depending on wether we reconstruct laser or voltage mode files!
    starttime = time.time()
    recwiz.reconwizard_page2()
    logging.info("Time for Rec p2: " + str(time.time() - starttime))

    # Select detector region of interest
    # what is the effect of disabling "detector region of interest auto compute"? this needs to be tested.
    starttime = time.time()
    recwiz.reconwizard_page3()
    logging.info("Time for Rec p3: " + str(time.time() - starttime))

    # ToF corrections
    starttime = time.time()
    recwiz.reconwizard_page4()
    logging.info("Time for Rec p4: " + str(time.time() - starttime))

    #Mass spectrum fit
    starttime = time.time()
    recwiz.reconwizard_page5()
    logging.info("Time for Rec p5: " + str(time.time() - starttime))

    #Ranging
    starttime = time.time()
    recwiz.reconwizard_page6()
    logging.info("Time for Rec p6: " + str(time.time() - starttime))

    #Actual reconstruction page
    starttime = time.time()
    ivasjavaprocess = ictrl.find_procID_by_name(ivas_javaproc_name)
    ivasjavaprocess = ivasjavaprocess[0]
    recwiz.reconwizard_page7(ivas_javaprocess_pid = ivasjavaprocess)
    logging.info("Time for Rec p7: " + str(time.time() - starttime))

    #Export epos
    starttime = time.time()
    ictrl.exportEpos()
    logging.info("Time for export epos: " + str(time.time() - starttime))





def IVAS_TidyUp(ivas_javaproc_name):

    pyautogui.PAUSE = 0.2

    #Delete project from disk
    starttime = time.time()
    ictrl.deleteProject()
    logging.info("Time for delete project: " + str(time.time() - starttime))

    # Close ivas
    # closing ivas and reopening for the next reconstruction is just easiyer than cleaning everything up.
    # I don't have a good method for this. This one is neither elegant nor reliable
    starttime = time.time()
    ictrl.Close_IVAS()
    pyautogui.press('enter') # popup asks wether want to exit the reconstruction wizard. Confirm

    time.sleep(5) #Important! If we don't wait, the window might not be fully closed. This could be a big problem if ivas is launched again quickly, bc it won't in that cas.

    logging.info("Time for close Ivas: " + str(time.time() - starttime))


    #done.









