
import os
import shutil
import configparser
import time
from json import loads
from datetime import datetime


import autoIVAS
from ivas_controlfunctions import ErrorInAutoIvas
from ivas_controlfunctions import GeneralIvasError
            

#Parameters IVAS
IVASlocation = "empty" #"C://Program Files//CAMECA Instruments//ivas-3.8.4//bin//ivas.bat"
IVASdirectory = "empty" #"C://Program Files//CAMECA Instruments//ivas-3.8.4//bin"  #not sure wether these weird path separators are necessary
ivas_javaproc_names = "empty" #["java.exe", "javaw.exe"]
ivas_config_path = "empty" #"C:\\Users\\Martin\\AppData\\Roaming\\ivas-3.8.4"

#Dummy range file
dummyRangeFilePath = "empty" #"C:/Users/Martin/Documents/Spyder/IVAS_autorec/AutoRec/autorec_dummy.rrng" #upward slash for ivas!

#click image folder
clickImageFolder = "empty" #"C:\\Users\\Martin\\Documents\\Spyder\\IVAS_autorec\\IVASClickimages"

#Folder with rhit files
rhitfolder = "empty" #"C:/Users/Martin/Documents/Spyder/IVAS_autorec/rhits" #upward slash for ivas!

#IVAS output directory
ivasoutputdir = "empty" #"C:\\Users\\Martin\\Documents\\NetBeansProjects"

#results dir for copying the resulting files
outputdir = "empty" #"C:\\Users\\Martin\\Documents\\Spyder\\IVAS_autorec\\output"

#protocol file
protocolFile = "empty" #"C:\\Users\\Martin\\Documents\\Spyder\\IVAS_autorec\\protocolFile.txt" # will be created, but never overwritten - text is only appended

#maxAttemptsPerFile and the list of bad rhits
#maxAttemptsPerFile = 3
#badRhitsFile = "C:\\Users\\Martin\\Documents\\Spyder\\IVAS_autorec\\badRHITS.txt" # rhits that fail more than maxAttemptsPerFile and therefore are attempted to reconstruct again
#TODO: need to add functionality for this table

configFilePath = os.path.expanduser("~/Desktop/config_VM.ini")


def getConfigFromFile(pathToConfigFile):

    config = configparser.ConfigParser(inline_comment_prefixes=('#'))
    try:
        readfiles = config.read(pathToConfigFile)
    except:
        print("\n Error while reading configuration File. \n")
        raise 
    if len(readfiles) == 0:
        raise Exception("Could not read config File " + pathToConfigFile + " . Does the File exist?")
 

    global IVASlocation, IVASdirectory, ivas_javaproc_names, ivas_config_path, dummyRangeFilePath
    global clickImageFolder, rhitfolder, ivasoutputdir, outputdir, protocolFile
    IVASlocation = config["IVASparameters"]["IVASlocation"]
    IVASdirectory = config["IVASparameters"]["IVASdirectory"]
    ivas_javaproc_names = loads(config["IVASparameters"]["ivas_javaproc_names"]) # the result is a list of strings, not a single string!
    ivas_config_path = config["IVASparameters"]["ivas_config_path"]
    dummyRangeFilePath = config["reconstructorScript"]["dummyRangeFilePath"]
    clickImageFolder = config["reconstructorScript"]["clickImageFolder"]
    rhitfolder = config["reconstructorScript"]["rhitfolder"]
    ivasoutputdir = config["reconstructorScript"]["ivasoutputdir"]
    outputdir = config["reconstructorScript"]["outputdir"]
    protocolFile = config["reconstructorScript"]["protocolFile"]








def filesOnPath(path):
    for file in os.listdir(path):
        if os.path.isfile(os.path.join(path, file)):
            yield file

def protocolWrite(text):
    now = datetime.now()
    dt_string = now.strftime("%d/%m/%Y %H:%M:%S")
    with open(protocolFile, "a+") as fid:
        fid.write(dt_string + " | " + text + os.linesep)






getConfigFromFile(configFilePath)

protocolWrite("IVAS_batch reconstruction script started.")
for rhitFile in filesOnPath(rhitfolder):

    rec_starttime = time.time()

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
        autoIVAS.AutoIVAS_setClickImageFolder(clickImageFolder)
        autoIVAS.IVAS_FullReconstruction(IVASlocation, IVASdirectory, ivas_javaproc_names, dummyRangeFilePath, rhitPath, projectName)
    except GeneralIvasError:
        print(" \n Generl IVAS Error. Cannot continue \n")
        raise 
    except ErrorInAutoIvas as errormsg:
        print( "encountered Error. Will Reset Ivas, delete eventually existing output project and try again. Error was: ")
        print(errormsg)
        autoIVAS.IVAS_KillAndReset(ivas_javaproc_names, ivas_config_path)
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
        autoIVAS.IVAS_TidyUp(ivas_javaproc_names)
        print ("...done")

        elapsed = time.time() - rec_starttime
        protocolWrite("Reconstruction " + projectName + " took " + str(elapsed) + " seconds")









