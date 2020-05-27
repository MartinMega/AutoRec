
import os
import shutil
from datetime import datetime


import autoIVAS
from ivas_controlfunctions import ErrorInAutoIvas
from ivas_controlfunctions import GeneralIvasError
            

#Parameters IVAS
IVASlocation = "C://Program Files//CAMECA Instruments//ivas-3.8.4//bin//ivas.bat"
IVASdirectory = "C://Program Files//CAMECA Instruments//ivas-3.8.4//bin"  #not sure wether these weird path separators are necessary
ivas_javaproc_name = "javaw.exe"
ivas_config_path = "C:\\Users\\Martin\\AppData\\Roaming\\ivas-3.8.4"

#Dummy range file
dummyRangeFilePath = "C:/Users/Martin/Documents/Spyder/IVAS_autorec/AutoRec/autorec_dummy.rrng" #upward slash for ivas!



#Folder with rhit files
rhitfolder = "C:/Users/Martin/Documents/Spyder/IVAS_autorec/rhits" #upward slash for ivas!

#IVAS output directory
ivasoutputdir = "C:\\Users\\Martin\\Documents\\NetBeansProjects"

#results dir for copying the resulting files
outputdir = "C:\\Users\\Martin\\Documents\\Spyder\\IVAS_autorec\\output"

#protocol file
protocolFile = "C:\\Users\\Martin\\Documents\\Spyder\\IVAS_autorec\\protocolFile.txt" # will be created, but never overwritten - text is only appended

#maxAttemptsPerFile and the list of bad rhits
#maxAttemptsPerFile = 3
#badRhitsFile = "C:\\Users\\Martin\\Documents\\Spyder\\IVAS_autorec\\badRHITS.txt" # rhits that fail more than maxAttemptsPerFile and therefore are attempted to reconstruct again
#TODO: need to add functionality for this table

def filesOnPath(path):
    for file in os.listdir(path):
        if os.path.isfile(os.path.join(path, file)):
            yield file

def protocolWrite(text):
    now = datetime.now()
    dt_string = now.strftime("%d/%m/%Y %H:%M:%S")
    with open(protocolFile, "a+") as fid:
        fid.write(dt_string + " | " + text)



protocolWrite("IVAS_batch reconstruction script started.")
for rhitFile in filesOnPath(rhitfolder):

    rhitPath= rhitfolder + "/" + rhitFile
    projectName = rhitFile[:-5] + "_AUTOREC"
    print("The next reconstruction will be " + projectName + " from file " + rhitPath)

    #This is where the files will be copied to on success:
    copyOutputTo = os.path.join(outputdir, projectName)
    if os.path.exists(copyOutputTo):
        print("There is already a folder (or file?) for " + projectName + " in the output folder. Skip!")
        continue

    #Reconstruct
    print ("Reconstruct...")
    protocolWrite("Next reconstruction: " + projectName + " from file " + rhitPath)

    try:
        autoIVAS.IVAS_FullReconstruction(IVASlocation, IVASdirectory, ivas_javaproc_name, dummyRangeFilePath, rhitPath, projectName)
    except GeneralIvasError:
        print(" \n Generl IVAS Error. Cannot continue \n")
        raise 
    except ErrorInAutoIvas as errormsg:
        print( "encountered Error. Will Reset Ivas, delete eventually existing output project and try again. Error was: ")
        print(errormsg)
        autoIVAS.IVAS_KillAndReset(ivas_javaproc_name, ivas_config_path)
        try:
            ivasoutputfolder = os.path.join(ivasoutputdir , projectName)
            shutil.rmtree(ivasoutputfolder)
        except Exception as errormsg2:
            print("Error deleting output directory. It might not exist? Error message is: ")
            print(errormsg2)
        print("...will continue with next file")
    else:
        successful = True      
        protocolWrite("Reconstruction successful. Will copy files... ")

        print ("...done")

        #Make output directory, copy the epos and csv files  
        print ("Copy output files...")    
        os.mkdir(copyOutputTo)
        ivasoutputproject = os.path.join(ivasoutputdir , projectName) # the folder where ivas will output the project

        for root, dirs, files in os.walk(ivasoutputproject):
            for file in files:
                if (file.lower()).endswith(".csv") or (file.lower()).endswith(".epos"): # make filename lowercase -> function becomes case insensitive
                    fileToCopy = os.path.join(root, file)
                    print("copying" + file)
                    shutil.copy2(src=fileToCopy, dst=copyOutputTo)
        print ("...done")
        protocolWrite("...done")

        #tidy up
        print ("Tidy up...")
        autoIVAS.IVAS_TidyUp(ivas_javaproc_name)
        print ("...done")



   
    











## Parameters for the project; rhit file and project name
#rhitPath = "C:/Users//Martin/Documents/Spyder/IVAS_autorec/R14_28149.RHIT"
#projectName =  "R14_28149_AUTOREC"


