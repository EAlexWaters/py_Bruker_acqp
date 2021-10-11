# py_Bruker_acqp
Generates a csv file summarizing key parameters from a Bruker MRI study (Paravision 6)

When run, the script opens a directory dialog and allows the user to select multiple study directories.

The current version assumes that data is organized in the following directory structure:
    [study directory] named for study name
        [subdirectory] 'Raw_Data'
            [sub-subdirectory] Bruker raw data folder and .study text file as 
                               unzipped from the .PVDatasets file exported from the scanner

It creates a .csv file in each study directory listing basic parameter information about each scan, 
sorted by scan time.

Also includes study information such as start time, stop time, and study/patient comments.
