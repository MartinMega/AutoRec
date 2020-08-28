import time
import pyautogui
import psutil
import shutil
import win32gui
import win32con
import win32process
import subprocess
import os
import signal
import warnings


try: # if package opencv-python is missing,  the locateOnScreen() function from pyautogy will be very slow.
    import cv2 
except:
    warnings.warn("Package opencv-python missing. Image recognition from library pyautogui will be awfully slow")




ivas_clickimage_folder = None # if set, this is ther place where clickimages are sought

ivas_MainWin_Handle = None # Will on launch be set to the Main Window handle and back to None on close


class ErrorInAutoIvas(Exception): # an error during the automated usage of ivas
    pass

class GeneralIvasError(Exception): # an error that is definitely not due to the dataset, like ivas complaining about having no license
    pass


def waitBar_awaitReady(timeout = 60):
    #wait until the waitbar in the Reconstruction Wizard shows "Ready"
    returned = awaitSymbolVariants("ivas_waitbar_ready_VM.png", "ivas_waitbar_ready_variant.png", timeout=timeout)
    if returned == None:
        raise ErrorInAutoIvas('waited for waitbar to show "ready" but timeout occured')

def awaitSymbol (symbol, presstab = False, mousemove = False, sleeptime = 0.5, timeout = 60, allow_timeout = False) :
    #wait until a certain symbol shows up on the screen
    #returns the position when found
    #sometimes, the buttions is active or the mouse hovers it. in these cases, it will not be detected. Solution: presstab=true and mousemove=true will move mouse and press tab to hopefully bring the button back to a normal state
    if ivas_clickimage_folder != None:
        symbol = os.path.join(ivas_clickimage_folder, symbol)
    waitingsince = time.time() 
    symbolonscreen = None
    while symbolonscreen == None:
        symbolonscreen = pyautogui.locateOnScreen(symbol) #wait until this symbol turns up
        if presstab:
            check_ivas_foreground_and_OK(timeout = 10, bringToFg=True)
            pyautogui.press('\t')
        if mousemove:
            pyautogui.move(1,1,0.2)
        if (time.time() - waitingsince) > timeout:
            if allow_timeout == False:
                raise ErrorInAutoIvas('waited for a Symbol ' + symbol + ' but timeout occured')
            else:
                return None
        time.sleep(sleeptime)
    return symbolonscreen

def awaitSymbolVariants(symbol1, symbol2,  presstab = False, mousemove = False, sleeptime = 0.2, timeout = 60, allow_timeout = False):
    # wait until one of the given symbols shows up on the screen. Return position or raise error if timeout occurs. allow_timeout = true will change this behaviour such that none is returned if nothign is found
    if ivas_clickimage_folder != None:
        symbol1 = os.path.join(ivas_clickimage_folder, symbol1)
        symbol2 = os.path.join(ivas_clickimage_folder, symbol2)
    waitingsince = time.time()    
    symbolonscreen = None
    while symbolonscreen == None:
        symbolonscreen = pyautogui.locateOnScreen(symbol1) #search for the first symbol
        if symbolonscreen == None:
            symbolonscreen = pyautogui.locateOnScreen(symbol2) # not found? look for the other symbol
        if presstab:
            check_ivas_foreground_and_OK(timeout = 10, bringToFg=True)
            pyautogui.press('\t')
        if mousemove:
            pyautogui.move(1,1,0.2)        
        if (time.time() - waitingsince) > timeout:
            if allow_timeout == False:
                raise ErrorInAutoIvas('waited for Symbol variants but timeout occured. Symbol1: ' + symbol1)
            else:
                return None
        time.sleep(sleeptime)
    return symbolonscreen


def awaitQuestionDialog(mousemove = False, sleeptime = 0.2, timeout = 60, allow_timeout = True):
    # wait antil the question mark from the dialog box turns up. It seems like the question mark size varies so check two different screenshotted symbols!
    # return none if timeout occurs
    symbolonscreen =  awaitSymbolVariants("IVAS_dialog_question_small.png", "IVAS_dialog_question_large.png", presstab=False, mousemove=mousemove, sleeptime=sleeptime, timeout=timeout, allow_timeout=allow_timeout)
    return symbolonscreen

def awaitInfoDialog(mousemove = False, sleeptime = 0.2, timeout = 60):
    # wait antil the info from the dialog box turns up. It seems like the info symbol size varies so check two different screenshotted symbols!
    # wait antil the question mark from the dialog box turns up. It seems like the question mark size varies so check two different screenshotted symbols!
    # return none if timeout occurs
    symbolonscreen =  awaitSymbolVariants("IVAS_dialog_info_small.png", "IVAS_dialog_info_large.png", presstab=False, mousemove=mousemove, sleeptime=sleeptime, timeout=timeout)
    return symbolonscreen



def Launch_IVAS (ivaslocation, ivasdirectory, ivas_javaproc_names):
    IVASprocess = subprocess.Popen(ivaslocation, cwd=ivasdirectory) #launch ivas
    awaitSymbol("IVAS_mainWindow_NewProject.png") # The new project symbol is a good indicator for that the main window is now open
    time.sleep(4)
    #following will set the main window handle. 
    # If a license error window pops up,  several window handles might be found. This is no problem bc we'll throw an error in that case.
    def callback (hwnd, hwnds):
        if win32gui.IsWindowVisible (hwnd) and win32gui.IsWindowEnabled (hwnd):            
            _, found_pid = win32process.GetWindowThreadProcessId (hwnd)
            ivaspid = find_procID_by_name(ivas_javaproc_names)
            if (found_pid == ivaspid[0]):
                hwnds.append (hwnd)
        return True
    hwnds = list()
    win32gui.EnumWindows (callback, hwnds)
    if len(hwnds) > 1:
        raise GeneralIvasError("Several possible handles to main Window found. Is a license error window open? Cannot continue!")
    global ivas_MainWin_Handle 
    ivas_MainWin_Handle= hwnds[0]
    check_ivas_foreground_and_OK(bringToFg=True)
    return IVASprocess




def terminateIVASprocess(ivas_javaproc_names):
    # Find javaprocess,  send terminate signal,  wait if it is gone within 10 sec.
    # if still not gone,  error
    javapids = find_procID_by_name(ivas_javaproc_names)
    if len(javapids) > 1:
        raise GeneralIvasError("Several possible ids for ivas java process found. Cannot continue!")
    elif len(javapids) == 1:
        os.kill(javapids[0], signal.SIGTERM)

    starttime = time.time()
    javapids = find_procID_by_name(ivas_javaproc_names, noexception = True)
    while len(javapids) != 0:
        if (time.time() - starttime < 10):
            break
        javapids = find_procID_by_name(ivas_javaproc_names, noexception=True)
        

def isErrorWindowOpen():
    #Check if an the ivas process has opened an error window   
    errorWinTitles = ["Error", "Unexpected Exception"]
    return isIVASWindowWithTitleOpen(errorWinTitles)
    # return isIVASWindowWithTitleOpen()
    # global ivas_MainWin_Handle
    # javapid = win32process.GetWindowThreadProcessId(ivas_MainWin_Handle)      
    # javapid = javapid[1]
    # def callback_SearchError(hwnd, errorWinsFound):
    #     errornames = ["Error", "Unexpected Exception"] # possible titles of error windows
    #     pid = win32process.GetWindowThreadProcessId(hwnd)
    #     if pid[1] == javapid:
    #         windowtxt = win32gui.GetWindowText(hwnd)
    #         if (windowtxt in errornames):
    #             errorWinsFound.append(windowtxt)
    # errorWinsFound = list()            
    # win32gui.EnumWindows (callback_SearchError, errorWinsFound)
    # return (len(errorWinsFound) > 0)


def isLicenseWindowOpen():
    #check if the Window with the licensing error is open
    return isIVASWindowWithTitleOpen(["Licensing"])


def isIVASWindowWithTitleOpen(windowTitles: list) -> bool:
    #Check if an the ivas process has opened a window with one of the titles given in windowTitles 
    global ivas_MainWin_Handle
    javapid = win32process.GetWindowThreadProcessId(ivas_MainWin_Handle)      
    javapid = javapid[1]
    def callback_SearchWin(hwnd, lparam): #Loop through all windows. If one of them belongs to the java process id and has the correct title, we found a match!
        winnames = lparam[1] # possible titles of error windows
        pid = win32process.GetWindowThreadProcessId(hwnd)
        if pid[1] == javapid:
            windowtxt = win32gui.GetWindowText(hwnd)
            if (windowtxt in winnames):
                lparam[0].append(windowtxt) 
    WinsFound = list()         
    lparam = [WinsFound, windowTitles] # we need to give two arguments to our callback fun: the counterfor the found windows (errorWinsFound)
                                            # and the list of window titles to search for. We can however only hand one parameter over when calling the fune
                                            # therefore we pack both of them in a list and call the function with it.
                                            # so: lparam[0] is a list that will be filled up as out callback fun finds matching windows, lparam[1] is a list of window names to search for. lparam is therefore a list of lists.
    win32gui.EnumWindows (callback_SearchWin, lparam)
    return (len(lparam[0]) > 0)




def Reset_IVAS (ivas_javaproc_names, ivas_config_path):
    # terminate ivas process, delete ivas configuration. You might also want to delete any incomplete files on the output path if you use this function.
    terminateIVASprocess(ivas_javaproc_names)
    time.sleep(0.2)
    Attempts = 0
    while True:
        try:
            shutil.rmtree(path=ivas_config_path) # Try 5 times to delete the ivas config folder. Sometimes windows does not immediately give us permission to delete this folder if IVAS which accesses the files has just been terminated.
        except Exception as err:
            warnings.warn("Failed to delete IVAS config folder. Error was: " + str(err))
            Attempts = Attempts+1
            time.sleep(0.5)
        else:
            break
        if Attempts > 5:
            raise GeneralIvasError("cannot delete ivas configuration folder. provided path:" + ivas_config_path)





def loadDummyRanges(dummyRangeFilePath):
    check_ivas_foreground_and_OK(bringToFg=True)
    clickpos = awaitSymbol("IVAS_mainWindow_RangeFileManager.png", timeout=20) #hit the range file manager symbol
    pyautogui.click(clickpos)
    clickpos = awaitSymbol("IVAS_RangeFileManager_RootSymbol.png", timeout=20) # open a new range file
    time.sleep(0.2)
    pyautogui.rightClick(clickpos) #context menu
    pyautogui.press('down')
    pyautogui.press('enter')
    time.sleep(0.2)
    awaitSymbol("IVAS_fileBrowser_Controls.png",sleeptime=0.2, presstab=False, mousemove=True)
    pyautogui.typewrite(dummyRangeFilePath) # enter the filename
    time.sleep(0.2)
    pyautogui.press('enter') #confirm
    time.sleep(1)

def createNewProject(rhitPath, projectName):
    check_ivas_foreground_and_OK(bringToFg=True)
    clickpos = awaitSymbol("IVAS_mainWindow_NewProject.png", presstab=False, mousemove=False) # open new peoject dialog
    pyautogui.click(clickpos)
    while not isIVASWindowWithTitleOpen(["New Project"]):
        time.sleep(0.3)
    time.sleep(1)
    pyautogui.press('enter')  # Go to second page
    awaitSymbol("IVAS_newProject_BrowseButton.png", presstab=False)
    time.sleep(1)
    pyautogui.press('\t') 
    pyautogui.press('enter') # this opens and fills io the RHIT//HITS file directory dialog
    clickpos = awaitSymbol("IVAS_fileBrowser_Controls.png", presstab=False, mousemove=True)
    time.sleep(1)     
    pyautogui.typewrite(rhitPath)
    pyautogui.press('enter')
    time.sleep(2)
    pyautogui.press('\t') # This will fill in the project name
    pyautogui.hotkey('ctrl', 'a')
    pyautogui.typewrite(projectName)
    pyautogui.press('\t', presses = 3, interval=0.2) # this opens and fills in the project folder dialog window
    #pyautogui.press('enter') 
    #time.sleep(2)
    #clickpos = awaitSymbol("IVAS_fileBrowser_Controls.png", presstab=False, mousemove=True) 
        #pyautogui.typewrite(projectfolder) disabled - don't change the project folder. juset esape instead(see next line)
        #pyautogui.press('enter') #confirm
    #pyautogui.press('escape') 
    #time.sleep(1)
    pyautogui.press('\t')
    pyautogui.press('enter')
    time.sleep(2)

def exportEpos():
    check_ivas_foreground_and_OK(bringToFg=True)
    clickpos = awaitSymbol("IVAS_mainWindow_ProjectsTab.png") # We click on the "Projects" tab. the text recognition does not recognise this text, which is really bad. We have to go for sumbol based recognition instead.
    pyautogui.click(clickpos) 
    menuopen = awaitSymbol("IVAS_projectsBrowser_OpenProjectTree.png") # We need to open the project in the project tree wirw window.
    clickpos = [menuopen.left + 0.2*menuopen.width, menuopen.top + 0.5*menuopen.height] # To this end,  we need to click the + symbo next to the Project symbol,  which is at about 1/3 of the symbol in the supplied png
    pyautogui.click(clickpos) 
    clickpos = awaitSymbol("IVAS_projectsBrowser_ReconSymbol.png") #Finding the recon symbol is easiyer than finding the text. we can also clock on the symbol, so that's alright.
    pyautogui.rightClick(clickpos) #open the contect menu
    pyautogui.press('down', presses = 6, interval=0.1) #scroll down to the "create epos" item
    pyautogui.press('enter')  # save epos!
    awaitInfoDialog(timeout=900)
    pyautogui.press('enter') # confirm with enter

def deleteProject():
    check_ivas_foreground_and_OK(bringToFg=True)
    clickpos = awaitSymbol("IVAS_projectsBrowser_ProjectSymbol.png") # right click project symbol
    pyautogui.rightClick(clickpos) 
    pyautogui.press('down', presses=7, interval=0.1) #scroll to the "delete from disk" button
    pyautogui.press('enter')
    awaitQuestionDialog()
    pyautogui.press('enter') #popup asks if we really want to delete the project. YES!
    pyautogui.press('\t') #popup asks if we want to save the analysis state. (bc the project is closed before it is deleted. select "no" and confirm)
    pyautogui.press('enter')
    awaitInfoDialog(timeout=120)
    time.sleep(1)
    pyautogui.press('enter')#popup says "successfully removed." hit the "OK" button


def getIVASWindowPosition():
    check_ivas_foreground_and_OK(bringToFg = True)
    time.sleep(0.2)
    rect = win32gui.GetWindowRect(ivas_MainWin_Handle)
    res = list(rect)
    return res


def bringIVAStoForeGround():
    #bring ivas window if it exists to the forground
    if isErrorWindowOpen():
        raise ErrorInAutoIvas("Detected IVAS Error window.")
    if isLicenseWindowOpen():
        raise GeneralIvasError("License window is open. Cannot continue")
    global ivas_MainWin_Handle
    if win32gui.IsWindow(ivas_MainWin_Handle):
        win32gui.ShowWindow(ivas_MainWin_Handle, win32con.SW_RESTORE)
        win32gui.SetForegroundWindow(ivas_MainWin_Handle)
        time.sleep(1)
    else:
        raise ErrorInAutoIvas("Attempted to bring IVAS window to Foreground, but Windows seems to not exist any more")


def check_ivas_foreground_and_OK(timeout = 20, bringToFg = False):
    # check if the ivas Window is in the foreground and no error window is open. a failsafe function that should be called regularly.
    # if window is not in fireground, the check will be repeated antil a timeout occurs. then, an error os thrown.
    # Also throws error if error window is open
    if isErrorWindowOpen():
        raise ErrorInAutoIvas("Detected IVAS Error window.")
    if isLicenseWindowOpen():
        raise GeneralIvasError("License window is open. Cannot continue")
    firstcheck = time.time()
    activeWindow = win32gui.GetForegroundWindow()
    while (activeWindow != ivas_MainWin_Handle):
        if (time.time() - firstcheck > timeout):
            raise ErrorInAutoIvas("Ivas Window not in Foreground, and timeout reached.")
        if bringToFg:
            bringIVAStoForeGround()
        time.sleep(0.2)
        activeWindow = win32gui.GetForegroundWindow()    
    
    activeWindow = win32gui.GetForegroundWindow()
    if activeWindow != ivas_MainWin_Handle:
        raise ErrorInAutoIvas("IVAS Window is not in Foreground. This is probably a problem. Abort.")


def find_procID_by_name(names, noexception=False): # from similar to something i found somewhere on the internet 
    #also works for a list of names, provided only one name is the name of a valid process
    #will not throw an exception of noexception=True
    # Iterate over all running process
    processpidlist = list()
    for proc in psutil.process_iter():
        try:
            # Get process name & pid from process object.
            processName = proc.name()
            if processName in names:
                processpidlist.append(proc.pid)
        except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
            pass
    if len(processpidlist) != 1 and (noexception==False):
        raise UserWarning("none or more than one processes with name " + str(names) + " found. This is probably a problem!")
    return processpidlist


def Close_IVAS(): # Just send a close message to the windoe. does not check wether ivas actually terminates.
    check_ivas_foreground_and_OK()
    global ivas_MainWin_Handle
    win32gui.PostMessage(ivas_MainWin_Handle ,win32con.WM_CLOSE,0,0)
    ivas_MainWin_Handle = None





