# -*- coding: utf-8 -*-
"""
Created on Mon Mar 30 21:37:27 2020

@author: Martin
"""

#important: IVAS MUST be on the primary monitor


import win32gui
import win32con
import regex
import win32process
import psutil


ivasWindowTitleRegex = "(.*IVAS.*)" 


def listOfAllWindowHandles():
    # using code from Pedro Lobito on Stackoverflow:  https://stackoverflow.com/questions/55547940/how-to-get-a-list-of-the-name-of-every-open-window
    # This code snippet is licensed under a CC-BY-SA-4.0 license: https://creativecommons.org/licenses/by-sa/4.0/ 
    allWindows = list()    
    def winEnumHandler( hwnd, ctx ):
        if win32gui.IsWindowVisible( hwnd ):
            allWindows.append(hwnd)
    win32gui.EnumWindows(winEnumHandler, None )
    return allWindows


def getIVASWindowHandle(IVAS_Window_Regex = ivasWindowTitleRegex):    
    allWindows = listOfAllWindowHandles()
    foundWindow = None
    for windowIT in allWindows:
        if (regex.match(IVAS_Window_Regex, win32gui.GetWindowText(windowIT))):
            #print(win32gui.GetWindowText(windowIT))
            if foundWindow == None:
                foundWindow = windowIT
            else:
                raise IOError("several windows with IVAS name found - cannot select the correct one")
    if foundWindow != None:            
        return foundWindow
    else:
        raise IOError("No windows with IVAS name found - is IVAS running?")


def get_hwnds_for_pid (pid): # from http://timgolden.me.uk/python/win32_how_do_i/find-the-window-for-my-subprocess.html
  def callback (hwnd, hwnds):
    if win32gui.IsWindowVisible (hwnd) and win32gui.IsWindowEnabled (hwnd):
      _, found_pid = win32process.GetWindowThreadProcessId (hwnd)
      if found_pid == pid:
        hwnds.append (hwnd)
    return True
    
  hwnds = []
  win32gui.EnumWindows (callback, hwnds)
  return hwnds

def get_Ivas_pid(processname = "javaw.exe"): # similar https://stackoverflow.com/questions/550653/cross-platform-way-to-get-pids-by-process-name-in-python
    processid = None
    for proc in psutil.process_iter():
        if proc.name() == processname:
            if (processid == None):
                processid = proc.pid
            else:
                raise IOError("There are several processes with the name " + processname + " Cannot determine the correct one")
    if processid == None:
        raise IOError("Cannot find process with name " + processname)
    else:
        return processid



def getIVASWindowNumOfChildren(IVAS_Window_Regex = ivasWindowTitleRegex):
    ivaspid = get_Ivas_pid()
    ivasWindows = get_hwnds_for_pid(ivaspid)
    numWindows = len(ivasWindows)
    return numWindows



def closeIVASWindow(IVAS_Window_Regex = ivasWindowTitleRegex):
    ivasWindow = getIVASWindowHandle(IVAS_Window_Regex=IVAS_Window_Regex)
    win32gui.PostMessage(ivasWindow,win32con.WM_CLOSE,0,0)



def minimiseAllButIVAS(IVAS_Window_Name = ivasWindowTitleRegex):
    # close all windows except the one with the provided name and eventual child windows
    #this puts all window handles in a list
    allWindows = listOfAllWindowHandles()

    #it seems like some windows are nonsense, like inactive background stoff.
    #if a window has not title,  we don't minimise it. 
    # also,  if a window has the giben IVAS-title or a parent with this title (like the "license not found" error),  we don't minimise it

    for windowIT in allWindows:
        #check if window has a name
        if (win32gui.GetWindowText(windowIT) == None):
            continue        
        # check if window name has the ivas window name
        if (regex.match(IVAS_Window_Regex, win32gui.GetWindowText(windowIT))):
            continue
        # check if parent window has the ivas window name
        parent = win32gui.GetParent(windowIT)
        if (regex.match(IVAS_Window_Regex, win32gui.GetWindowText(windowIT))):
            continue    
        win32gui.ShowWindow(windowIT,win32con.SW_MINIMIZE)
        
        
        
        
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
    return processpidlist
