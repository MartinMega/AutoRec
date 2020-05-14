import time
import pyautogui
import psutil

import ivas_controlfunctions as ictrl





def reconwizard_page1():
    ictrl.check_ivas_foreground()
    clickpos = ictrl.awaitSymbol("IVAS_Reconwizard_InfoDetailsTab.png", presstab=True, mousemove=True) #Click on the register symbil (will do nothing  for the reconstruction but set the input focus on the reconstruction wizard)
    pyautogui.click(clickpos) 
    pyautogui.press('\t', presses=2, interval=0.2) #go to next page
    pyautogui.press('enter')



def reconwizard_page2():
    # second page - we want to export all of the csv file here. the number of csv files that we can expost might vary, depending on wether we reconstruct laser or voltage mode files!
    # here is how it works: 
    # 1. first click the save-as-csv button and just save the file in the analysis folder.
    # 2. then we use shift-tap to go back to the dropdown menu and use the down key to select the next entry.
    # 3. When we have saved all files from the dropdown menu, pressung the down key another time will have no efffect.
    # 4. this means that when we attempt to save the file,  we will actually try to save the same file again. ivas will respond by asking us whether we want to overwrite the existing file.
    # 5. This is how we know that we've saved all files and can proceed.
    ictrl.check_ivas_foreground()
    ictrl.awaitSymbol("IVAS_ReconWizard_Page2Heading.png")

    oldpause = pyautogui.PAUSE # otherwise this is annoyingly slow, but we set it back after the while loop
    pyautogui.PAUSE = 0.5

    while True:
        ictrl.check_ivas_foreground()
        time.sleep(1)
        print("waiting for ready bar...")
        ictrl.waitBar_awaitReady()
        clickpos = None
        while clickpos == None:
            ictrl.check_ivas_foreground()
            print("searching export csv...")
            clickpos = pyautogui.locateOnScreen("IVAS_ReconWizard_ExportCSV.png") # tab scrolling doesn't work reliably - and this really sucks here. So we need to search for the export buttn instead.
            pyautogui.press('\t')   #need to press tab and move mouse bc the button has another color when active/hovered and therefore cannot be recognised
            pyautogui.moveTo(1,1,0.2) 
        pyautogui.click(clickpos)    

        ictrl.awaitQuestionDialog()
        pyautogui.press('enter', presses = 2,interval=2)# dialogs: "use analysis folder", "save"  

        if (ictrl.awaitQuestionDialog(timeout=2) != None): #eventually, the "overwrite?" dialog will pop up. Ww check this for 2 seconds.
            break

        for k in range(5): pyautogui.hotkey('shift', 'tab') #back to dropdown menu 
        
        pyautogui.press('down') #select next element of drowpdown menu    
    pyautogui.PAUSE = oldpause
    pyautogui.press('\t', presses = 2, interval=0.2) #go to "not overwrite" button
    pyautogui.press('enter')
    ictrl.check_ivas_foreground()
    pyautogui.press('\t', presses = 2, interval=0.2) # got to "next" button
    pyautogui.press('enter')

def reconwizard_page3():
    # just go to the next page and hit enter
    ictrl.check_ivas_foreground()
    ictrl.awaitSymbol("IVAS_ReconWizard_Page3Heading.png")

    pyautogui.press('\t', presses = 6, interval=0.2) 
    pyautogui.press('enter')
    time.sleep(1)

def reconwizard_page4():
    #wait until waitbar says ready, hit the "start" button, then wait until waitbar says ready again.
    ictrl.check_ivas_foreground()
    ictrl.awaitSymbol("IVAS_ReconWizard_Page4Heading.png")

    ictrl.waitBar_awaitReady()
    time.sleep(0.5)
    clickpos = ictrl.awaitSymbol("IVAS_ReconWizard_StartToFcorrButton.png", presstab=True, mousemove=True) #press the start button ond wait
    pyautogui.click(clickpos)
    time.sleep(1) # Make sure the "Ready" has disappeared after pressing the button
    ictrl.waitBar_awaitReady()

    clickpos = ictrl.awaitSymbol("IVAS_ReconWizard_NextButton.png", presstab=True, mousemove=True)  # problem: tab scrolling won't work this time! we need to search for the "next" button.
    pyautogui.click(clickpos) 

def reconwizard_page5():
    #do nothing. Just go to the next page
    #ictrl.check_ivas_foreground()
    ictrl.awaitSymbol("IVAS_ReconWizard_Page5Heading.png")

    clickpos = pyautogui.locateOnScreen("IVAS_ReconWizard_NextButton.png")  # problem: tab scrolling won't work this time! we need to search for the "next" button.
    pyautogui.click(clickpos) 

def reconwizard_page6():
    #Watch out: dummy range file needed!!!
    # we actually don't want to range anything,  but ivas will not allow us to preceed without doing so.
    # Therefore we use a dummy range file. This was was loaded right in the beginning before we even created the project.
    ictrl.check_ivas_foreground()
    ictrl.awaitSymbol("IVAS_ReconWizard_Page6Heading.png")

    pyautogui.press('up') #select the dummy range file. If only the dummy range file is loaded and it starts with a 
                        #letter/number below the ivas generated range file name for the sampe,  it will be above the auto generated
                        #range in the file. pressing "up" will therefore select it.
    time.sleep(5)

    clickpos = pyautogui.locateOnScreen("IVAS_ReconWizard_NextButton.png")  # problem: tab scrolling won't work this time! we need to search for the "next" button.
    pyautogui.click(clickpos) 


def reconwizard_page7(ivas_javaprocess_pid):
    #will create one preview and save it.
    #Waits until file is saved and ivas is ready before concluding.
    #the java provess id is needed to check for tjhe cpu usage. This is the indicator for wether the reconstruction ios still running.
    #I have tried really hard but could not find any better solution to test wether the reconstruction is still running!

    ictrl.check_ivas_foreground()
    ictrl.awaitSymbol("IVAS_ReconWizard_Page7Heading.png")

    pyautogui.press('enter') #Start the reconstruction preview

    clickpos = ictrl.awaitSymbol("IVAS_ReconWizard_SaveReconstruction.png") #wait until preview is created (when this is done, the "save" button will show up), then click it
    time.sleep(1)
    pyautogui.click(clickpos)

    ictrl.awaitSymbol("IVAS_massSpectrum_caption.png", sleeptime=4) # when the reconstruction is readu IVAS will open and disply it. this will also display the mass spectrum with the corresponding caption.
    
    ivasprocess = psutil.Process(pid=ivas_javaprocess_pid)

    ivascpuusage = ivasprocess.cpu_percent(interval=3)
    while (ivascpuusage >= 2.0):
        print("ivasproc cpu usage is" + str(ivascpuusage))
        time.sleep(0.5)
        ivascpuusage = ivasprocess.cpu_percent(interval=3)
    