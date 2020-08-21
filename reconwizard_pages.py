import time
import pyautogui
import psutil

import ivas_controlfunctions as ictrl





def reconwizard_page1():
    time.sleep(1)
    ictrl.bringIVAStoForeGround()
    ictrl.check_ivas_foreground_and_OK(bringToFg=True)
    ictrl.awaitSymbol("IVAS_Reconwizard_InfoDetailsTab.png", presstab=True, mousemove=True) # Wait until this symbol shows up
    clickpos = ictrl.awaitSymbol("IVAS_ReconWizard_NextButton.png", presstab=True, mousemove=True)  # problem: tab scrolling won't work this time! we need to search for the "next" button.
    pyautogui.click(clickpos) 



def reconwizard_page2():
    # second page - we want to export all of the csv file here. the number of csv files that we can expost might vary, depending on wether we reconstruct laser or voltage mode files!
    # here is how it works: 
    # 0. increase the size of the reconstruction selection such that the entire dataset is reconstructed
    # 1. first click the save-as-csv button and just save the file in the analysis folder.
    # 2. then we use shift-tap to go back to the dropdown menu and use the down key to select the next entry.
    # 3. When we have saved all files from the dropdown menu, pressung the down key another time will have no efffect.
    # 4. this means that when we attempt to save the file,  we will actually try to save the same file again. ivas will respond by asking us whether we want to overwrite the existing file.
    # 5. This is how we know that we've saved all files and can proceed.
    # this is very slow
    ictrl.check_ivas_foreground_and_OK(bringToFg=True)
    ictrl.awaitSymbol("IVAS_ReconWizard_Page2Heading.png")
    ictrl.waitBar_awaitReady(timeout=300)
    pyautogui.moveTo(1,1,0.1)

    windowposition = ictrl.getIVASWindowPosition()
    br_dragto = [windowposition[0] + windowposition[2] - 3,  windowposition[1] + windowposition[3] - 3]
    bottomright = ictrl.awaitSymbol("IVAS_ReconWizard_page_VoltageSliderBottomRight.png")
    pyautogui.moveTo(bottomright)
    pyautogui.dragTo(br_dragto[0], br_dragto[1] , duration=1, button="left", tween=pyautogui.easeInOutCubic)
    tl_dragto = [windowposition[0] + 3,  windowposition[1] + 3]
    topleft = ictrl.awaitSymbol("IVAS_ReconWizard_page_VoltageSliderTopLeft.png", allow_timeout=True, timeout=15) #allow not finding this symbol here bc it might overlap with the y axis, in this case ift won't be found but this is fine bc it aleary is where we want it then.
    if not(topleft == None):
        pyautogui.moveTo(topleft)
        pyautogui.dragTo(tl_dragto[0], tl_dragto[1] , duration=1, button="left", tween=pyautogui.easeInOutCubic)
    time.sleep(0.5)
    clickpos = ictrl.awaitSymbol("IVAS_ReconWizard_Page2CommitButton.png")
    pyautogui.click(clickpos)
    time.sleep(2)
    ictrl.waitBar_awaitReady(timeout = 180)

    while True:
        ictrl.check_ivas_foreground_and_OK(bringToFg=True)
        time.sleep(1)
        ictrl.waitBar_awaitReady(timeout=180)
        pyautogui.moveTo(1,1,0.1)
        clickpos = ictrl.awaitSymbol("IVAS_ReconWizard_ExportCSV.png", presstab=True, mousemove=False, timeout=10)
        # clickpos = None
        # while clickpos == None:
        #     ictrl.check_ivas_foreground_and_OK(bringToFg=True)
        #     print("searching export csv...")
            
        #     clickpos = pyautogui.locateOnScreen("IVAS_ReconWizard_ExportCSV.png") # tab scrolling doesn't work reliably - and this really sucks here. So we need to search for the export buttn instead.
        #     pyautogui.press('\t')   #need to press tab and move mouse bc the button has another color when active/hovered and therefore cannot be recognised
        #     pyautogui.moveTo(1,1,0.2) 
        pyautogui.click(clickpos)    

        ictrl.awaitQuestionDialog()
        pyautogui.press('enter', presses = 2,interval=2)# dialogs: "use analysis folder", "save"  

        if (ictrl.awaitQuestionDialog(timeout=3, allow_timeout=True) != None): #eventually, the "overwrite?" dialog will pop up. Ww check this for 2 seconds.
            break
        time.sleep(1)
        for _ in range(5): 
            pyautogui.hotkey('shift', 'tab') #back to dropdown menu 
            time.sleep(1)
        
        pyautogui.press('down') #select next element of drowpdown menu 
        time.sleep(2)
        ictrl.waitBar_awaitReady(timeout=700)
        time.sleep(1)
    pyautogui.press('\t', presses = 2, interval=0.2) #go to "not overwrite" button
    pyautogui.press('enter')
    ictrl.check_ivas_foreground_and_OK(bringToFg=True)
    pyautogui.press('\t', presses = 2, interval=0.2) # got to "next" button
    pyautogui.press('enter')

def reconwizard_page3():
    # just go to the next page and hit enter
    ictrl.check_ivas_foreground_and_OK(bringToFg=True)
    ictrl.awaitSymbol("IVAS_ReconWizard_Page3Heading.png")

    pyautogui.press('\t', presses = 6, interval=0.2) 
    pyautogui.press('enter')
    time.sleep(1)

def reconwizard_page4():
    #wait until waitbar says ready, hit the "start" button, then wait until waitbar says ready again.
    ictrl.check_ivas_foreground_and_OK(bringToFg=True)
    ictrl.awaitSymbol("IVAS_ReconWizard_Page4Heading.png")

    ictrl.waitBar_awaitReady()
    time.sleep(0.5)
    clickpos = ictrl.awaitSymbol("IVAS_ReconWizard_StartToFcorrButton.png", presstab=True, mousemove=True) #press the start button ond wait
    pyautogui.click(clickpos)
    time.sleep(1) # Make sure the "Ready" has disappeared after pressing the button
    ictrl.waitBar_awaitReady(timeout=300)

    clickpos = ictrl.awaitSymbol("IVAS_ReconWizard_NextButton.png", presstab=True, mousemove=True, timeout=240)  # problem: tab scrolling won't work this time! we need to search for the "next" button.
    pyautogui.click(clickpos) 

def reconwizard_page5():
    #do nothing. Just go to the next page
    ictrl.check_ivas_foreground_and_OK(bringToFg=True)
    ictrl.bringIVAStoForeGround()
    ictrl.awaitSymbol("IVAS_ReconWizard_Page5Heading.png")
    pyautogui.moveTo(1,1,0.1)
    clickpos = ictrl.awaitSymbol("IVAS_ReconWizard_NextButton.png", presstab=True, mousemove=True)  # problem: tab scrolling won't work this time! we need to search for the "next" button.
    pyautogui.click(clickpos) 

def reconwizard_page6():
    #Watch out: dummy range file needed!!!
    # we actually don't want to range anything,  but ivas will not allow us to preceed without doing so.
    # Therefore we use a dummy range file. This was was loaded right in the beginning before we even created the project.
    ictrl.check_ivas_foreground_and_OK(bringToFg=True)
    ictrl.awaitSymbol("IVAS_ReconWizard_Page6Heading.png")

    pyautogui.press('up') #select the dummy range file. If only the dummy range file is loaded and it starts with a 
                        #letter/number below the ivas generated range file name for the sampe,  it will be above the auto generated
                        #range in the file. pressing "up" will therefore select it.
    time.sleep(5)

    clickpos = ictrl.awaitSymbol("IVAS_ReconWizard_NextButton.png")  # problem: tab scrolling won't work this time! we need to search for the "next" button.
    pyautogui.click(clickpos) 


def reconwizard_page7(ivas_javaprocess_pid):
    #will create one preview and save it.
    #Waits until file is saved and ivas is ready before concluding.
    #the java provess id is needed to check for tjhe cpu usage. This is the indicator for wether the reconstruction ios still running.
    #I have tried really hard but could not find any better solution to test wether the reconstruction is still running!

    ictrl.check_ivas_foreground_and_OK(bringToFg=True)
    ictrl.awaitSymbol("IVAS_ReconWizard_Page7Heading.png")

    pyautogui.press('enter') #Start the reconstruction preview

    clickpos = ictrl.awaitSymbol("IVAS_ReconWizard_SaveReconstruction.png") #wait until preview is created (when this is done, the "save" button will show up), then click it
    time.sleep(1)
    pyautogui.click(clickpos)

    ictrl.awaitSymbol("IVAS_massSpectrum_caption.png", sleeptime=4, timeout=900) # when the reconstruction is readu IVAS will open and disply it. this will also display the mass spectrum with the corresponding caption.
    
    ivasprocess = psutil.Process(pid=ivas_javaprocess_pid)

    ivascpuusage = ivasprocess.cpu_percent(interval=3)
    while (ivascpuusage >= 2.0):
        print("ivasproc cpu usage is" + str(ivascpuusage))
        time.sleep(0.5)
        ivascpuusage = ivasprocess.cpu_percent(interval=3)
    