import time
import pyautogui
import psutil
import win32gui
import win32con
import win32process
import subprocess


ivas_MainWin_Handle = None # Will on launch be set to the Main Window handle and back to None on close

class ErrorInAutoIvas(Exception): # an error during the automated usage of ivas
    pass

class GeneralIvasError(Exception): # an error that is definitely not due to the dataset, like ivas complaining about having no license
    pass


def waitBar_awaitReady(timeout = 60):
    #wait until the waitbar in the Reconstruction Wizard shows "Ready"
    returned = awaitSymbolVariants("ivas_waitbar_ready.png", "ivas_waitbar_ready_variant.png", timeout=timeout)
    if returned == None:
        raise ErrorInAutoIvas('waited for waitbar to show "ready" but timeout occured')

def awaitSymbol (symbol, presstab = False, mousemove = False, sleeptime = 0.5, timeout = 60) :
    #wait until a certain symbol shows up on the screen
    #returns the position when found
    #sometimes, the buttions is active or the mouse hovers it. in these cases, it will not be detected. Solution: presstab=true and mousemove=true will move mouse and press tab to hopefully bring the button back to a normal state
    waitingsince = time.time() 
    symbolonscreen = None
    while symbolonscreen == None:
        symbolonscreen = pyautogui.locateOnScreen(symbol) #wait until this symbol turns up
        if presstab:
            check_ivas_foreground(timeout = 5)
            pyautogui.press('\t')
        if mousemove:
            pyautogui.move(1,1,0.2)
        if (time.time() - waitingsince) > timeout:
            raise ErrorInAutoIvas('waited for a Symbol but timeout occured')
        time.sleep(sleeptime)
    return symbolonscreen

def awaitSymbolVariants(symbol1, symbol2,  presstab = False, mousemove = False, sleeptime = 0.2, timeout = 60):
    # wait until one of the given symbols shows up on the screen. Return position or none if timeout occurs
    waitingsince = time.time()    
    symbolonscreen = None
    while symbolonscreen == None:
        symbolonscreen = pyautogui.locateOnScreen(symbol1) #search for the first symbol
        if symbolonscreen == None:
            symbolonscreen = pyautogui.locateOnScreen(symbol2) # not found? look for the other symbol
        if presstab:
            check_ivas_foreground(timeout = 5)
            pyautogui.press('\t')
        if mousemove:
            pyautogui.move(1,1,0.2)        
        if (time.time() - waitingsince) > timeout:
            raise ErrorInAutoIvas('waited for a Symbol but timeout occured')
        time.sleep(sleeptime)
    return symbolonscreen


def awaitQuestionDialog(mousemove = False, sleeptime = 0.2, timeout = 60):
    # wait antil the question mark from the dialog box turns up. It seems like the question mark size varies so check two different screenshotted symbols!
    # return none if timeout occurs
    symbolonscreen =  awaitSymbolVariants("IVAS_dialog_question_small.png", "IVAS_dialog_question_large.png", presstab=False, mousemove=mousemove, sleeptime=sleeptime, timeout=timeout)
    return symbolonscreen

def awaitInfoDialog(mousemove = False, sleeptime = 0.2, timeout = 60):
    # wait antil the info from the dialog box turns up. It seems like the info symbol size varies so check two different screenshotted symbols!
    # wait antil the question mark from the dialog box turns up. It seems like the question mark size varies so check two different screenshotted symbols!
    # return none if timeout occurs
    symbolonscreen =  awaitSymbolVariants("IVAS_dialog_info_small.png", "IVAS_dialog_info_large.png", presstab=False, mousemove=mousemove, sleeptime=sleeptime, timeout=timeout)
    return symbolonscreen


def Launch_IVAS (ivaslocation, ivasdirectory, ivas_javaproc_name):
    IVASprocess = subprocess.Popen(ivaslocation, cwd=ivasdirectory) #launch ivas
    awaitSymbol("IVAS_mainWindow_NewProject.png") # The new project symbol is a good indicator for that the main window is now open
    time.sleep(4)
    if pyautogui.locateOnScreen("IVAS_nolicense_errorsymbol.png") != None: # Check for license error dialog
         raise GeneralIvasError("it seems like the no license key has been found!")

    #following will set the main window handle
    def callback (hwnd, hwnds):
        if win32gui.IsWindowVisible (hwnd) and win32gui.IsWindowEnabled (hwnd):            
            _, found_pid = win32process.GetWindowThreadProcessId (hwnd)
            ivaspid = find_procID_by_name(ivas_javaproc_name)
            if (found_pid == ivaspid[0]):
                hwnds.append (hwnd)
        return True
    hwnds = list()
    win32gui.EnumWindows (callback, hwnds)
    if len(hwnds) > 1:
        raise GeneralIvasError("Several possible handles to main Window found. Cannot continue!")
    global ivas_MainWin_Handle 
    ivas_MainWin_Handle= hwnds[0]
    return IVASprocess



def loadDummyRanges(dummyRangeFilePath):
    check_ivas_foreground()
    clickpos = awaitSymbol("IVAS_mainWindow_RangeFileManager.png", timeout=20) #hit the range file manager symbol
    pyautogui.click(clickpos)
    clickpos = awaitSymbol("IVAS_RangeFileManager_RootSymbol.png", timeout=20) # open a new range file
    pyautogui.rightClick(clickpos) #context menu
    pyautogui.press('down')
    pyautogui.press('enter')
    pyautogui.typewrite(dummyRangeFilePath) # enter the filename
    pyautogui.press('enter') #confirm

def createNewProject(rhitPath, projectName):
    check_ivas_foreground()
    clickpos = awaitSymbol("IVAS_mainWindow_NewProject.png", presstab=False, mousemove=False) # open new peoject dialog
    pyautogui.click(clickpos)
    pyautogui.press('enter')  # Go to second page
    pyautogui.press('\t') 
    pyautogui.press('enter') # this opens and fills io the RHIT//HITS file directory dialog
    time.sleep(1)
    pyautogui.typewrite(rhitPath)
    pyautogui.press('enter')
    pyautogui.press('\t') # This will fill in the project name
    pyautogui.hotkey('ctrl', 'a')
    pyautogui.typewrite(projectName)
    pyautogui.press('\t', presses = 3, interval=0.2) # this opens and fills in the project folder dialog window
    pyautogui.press('enter') 
    time.sleep(1)
        #pyautogui.typewrite(projectfolder) disabled - don't change the project folder. juset esape instead(see next line)
        #pyautogui.press('enter') #confirm
    pyautogui.press('escape') 
    pyautogui.press('\t')
    pyautogui.press('enter')
    time.sleep(1)

def exportEpos():
    check_ivas_foreground()
    clickpos = awaitSymbol("IVAS_mainWindow_ProjectsTab.png") # We click on the "Projects" tab. the text recognition does not recognise this text, which is really bad. We have to go for sumbol based recognition instead.
    pyautogui.click(clickpos) 
    menuopen = pyautogui.locateOnScreen("IVAS_projectsBrowser_OpenProjectTree.png") # We need to open the project in the project tree wirw window.
    clickpos = [menuopen.left + 0.2*menuopen.width, menuopen.top + 0.5*menuopen.height] # To this end,  we need to click the + symbo next to the Project symbol,  which is at about 1/3 of the symbol in the supplied png
    pyautogui.click(clickpos) 
    clickpos = pyautogui.locateCenterOnScreen("IVAS_projectsBrowser_ReconSymbol.png") #Finding the recon symbol is easiyer than finding the text. we can also clock on the symbol, so that's alright.
    pyautogui.rightClick(clickpos) #open the contect menu
    pyautogui.press('down', presses = 6, interval=0.1) #scroll down to the "create epos" item
    pyautogui.press('enter')  # save epos!
    awaitInfoDialog()
    pyautogui.press('enter') # confirm with enter

def deleteProject():
    check_ivas_foreground()
    clickpos = awaitSymbol("IVAS_projectsBrowser_ProjectSymbol.png") # right click project symbol
    pyautogui.rightClick(clickpos) 
    pyautogui.press('down', presses=7, interval=0.1) #scroll to the "delete from disk" button
    pyautogui.press('enter')
    pyautogui.press('enter') #popup asks if we really want to delete the project. YES!
    pyautogui.press('\t') #popup asks if we want to save the analysis state. (bc the project is closed before it is deleted. select "no" and confirm)
    pyautogui.press('enter')
    pyautogui.press('enter')#popup says "successfully removed." hit the "OK" button


def check_ivas_foreground(timeout = 20):
    # check if the ivas Window is in the foreground. a failsafe function that should be called regularly.
    # if it is not, the check will be repeated antil a timeout occurs. then, an error os thrown.
    firstcheck = time.time()
    activeWindow = win32gui.GetForegroundWindow()
    while (activeWindow != ivas_MainWin_Handle):
        if (time.time() - firstcheck > timeout):
            raise GeneralIvasError("Ivas Window not in Foreground, and timeout reached.")
        time.sleep(0.2)
        activeWindow = win32gui.GetForegroundWindow()    
    
    activeWindow = win32gui.GetForegroundWindow()
    if activeWindow != ivas_MainWin_Handle:
        raise GeneralIvasError("IVAS Window is not in Foreground. Thir is probably a problem. Abort.")


def find_procID_by_name(name): # from similar to something i found somewhere on the internet 
    # Iterate over all running process
    processpidlist = list()
    for proc in psutil.process_iter():
        try:
            # Get process name & pid from process object.
            processName = proc.name()
            if processName == name:
                processpidlist.append(proc.pid)
        except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
            pass
    if len(processpidlist) != 1:
        raise UserWarning("none or more than one processes with name " + name + " found. This is probably a problem!")
    return processpidlist


def Close_IVAS(): # Just send a close message to the windoe. does not check wether ivas actually terminates.
    check_ivas_foreground()
    global ivas_MainWin_Handle
    win32gui.PostMessage(ivas_MainWin_Handle ,win32con.WM_CLOSE,0,0)
    ivas_MainWin_Handle = None





