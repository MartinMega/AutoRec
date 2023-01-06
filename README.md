# AutoRec
A repository for the IVAS Autorec scripts


# Requirements

- python and the packages pyautogui and wpywin32. pyautogui will run significantly faster if also opencv-python is installed. The easiest way is probably to use anaconda python.
- IVAS installed on your computer and an active license. The script will reset all IVAS settings before starting a reconstruction, therefore you might wish to back up your IVAS configuration before starting the script. 
- You need a folder of .rhit or .hits files on your computer to work on
- These scripts run best on a virtual machine. If you use VirtualBox, have a look at VM_setup_tips.txt for some tricks to the reconstructor scripts run faster


# How to Use

1. Download the files from this repository into a computer on your folder
2. Create a copy of the file config_VM.ini and save it on your Desktop. Edit the paths in the file according to your system.
3. Run the file IVAS_batch_rhitfolder.py

