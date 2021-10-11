# -*- coding: utf-8 -*-
"""
Created on Wed Jan 24 10:44:26 2018
Updated 10/11/2021

@author: Alex Waters

This script creates .csv formatted parameter files for a Bruker PV6 MRI study, for easy reference.

When run, the script opens a directory dialog and allows the user to select multiple directories.

The current version assumes that data is organized in the following directory structure:
    [study directory] named for study name
        [subdirectory] 'Raw_Data'
            [sub-subdirectory] Bruker raw data folder and .study text file as 
                               unzipped from the .PVDatasets file exported from the scanner

It creates a .csv file in the study directory listing basic parameter information about each scan, 
sorted by scan time.

Also includes study information such as start time, stop time, and study/patient comments.

Requires access to the file paramRE, which defines regular expressions for the various
formatting Bruker uses in its parameter files.

"""

import re
import csv
import sys
import os
import os.path
from PyQt5.QtWidgets import (QFileDialog, QAbstractItemView, QListView,
                             QTreeView, QApplication, QDialog)
from PyQt5.QtCore import QCoreApplication
from dateutil import parser
import paramRE as paRE

# File paths for test driving the script. At some point a separate
# testing script should be written and these should be removed.

#acqpPath = 'D:\\Documents\\PythonScripts\\UnitTests\\acqp_multiTR'
#acqpPath = 'D:\\Documents\\PythonScripts\\UnitTests\\acqp_multiTE'
#acqpPath = 'D:\\Documents\\PythonScripts\\UnitTests\\acqp_longTR'

#acqpFile = open(acqpPath)
#acqpText = acqpFile.read()
#acqpFile.close()


#methodPath = 'D:\\Documents\\PythonScripts\\UnitTests\\method1'
##methodPath = 'D:\\Documents\\PythonScripts\\UnitTests\\method_multi_slicePack'
#methodFile = open(methodPath)
#methodText = methodFile.read()
#methodFile.close()


# This is the Acqp class that reads parameters for a single scan and stores them
# in a dictionary.
class Acqp:
    def __init__(self, scanNum):
        # Define the dictionary structures for the apramters we want to read
        self.parameters = {
            'ScanNumber':scanNum,
            'PulseProg':'',
            'acqProtocol':'',
            'refPower':'',
            'ReceiverGain':'',
            'RepTime':'',
            'EchoTime':'',
            'nEchoes':'',
            'RecovTime':'',
            'nSlices':'',
            'nSlicePacks':'',
            'FOV':'',
            'Matrix':'',
            'SliceThick':'',
            'SliceSep':'',
            'SliceList':'',
            'SliceOffset':'',
            'SlicePackOffset':'',
            'ReadOffset':'',
            'PhaseOffset':'',
            'nAverages':'',
            'ImageOrient':'',
            'SlicepackVec':'',
            'nEvolutionCycles':'',
            'nRepetitions':'',
            'EvolutionDelay':'',
            'FlipAngle':'',
            'IdealFAat':'',
            'BasicFreq':'',
            'SpecWidth':'',
            'ExcitationPulse':'',
            'RefocusingPulse':'',
            'PulseShape':'',
            'ReadOutDir':'',
            'RareFactor':'',
            'FatSat':'',
            'Gating':'',
            'wordType':'',
            'rawWordType':'',
            'ByteOrder':'',
            'SaveTime':'',
            'Filename':'',
            'MusWt':'',
            'subjOrientHF':'',
            'subjOrientSP':'',
            'PVver':'',
            'Major PV ver':'',
            'dwiBvals':'',
            'dwiA0':'',
            'FlowDir':'',
            'Venc':'',
        }

        self.csvParameters = {
            'ScanNumber':0,
            'acqProtocol':'',
            'refPower':'',
            'ReceiverGain':'',
            'RepTime':'',
            'EchoTime':'',
            'nEchoes':'',
            'nSlices':'',
            'FOV':'',
            'Matrix':'',
            'SliceThick':'',
            'SliceSep':'',
            'nAverages':'',
            'ImageOrient':'',
            'nEvolutionCycles':'',
            'nRepetitions':'',
            'SlicePackOffset':'',
            'ReadOutDir':'',
            'ReadOffset':'',
            'PhaseOffset':'',
            'RareFactor':'',
            'ExcitationPulse':'',
            'RefocusingPulse':'',
            'SpecWidth':'',
            'FatSat':'',
            'Gating':'',
            'FlipAngle':'',
            'SaveTime':'',
            'FlowDir':'',
            'Venc':'',
        }

    def readParameters(self, acqpText, methodText):
        # Create and search a regular expression for each parameter.
        # Store the value in the parameter dictionary.

        # Pulse Program
        pulseProgRegex = re.compile(paRE.regExAngleText('##$PULPROG'))
        self.parameters['PulseProg'] = pulseProgRegex.search(acqpText).group(1)

        # Repetition time
        pvRepTimeRegex = re.compile(paRE.regExFloatArray('##$ACQ_repetition_time'))
        self.parameters['RepTime'] = pvRepTimeRegex.search(acqpText).group(1).replace('\n', '')

        # nAverages
        nAveragesRegex = re.compile(paRE.regExOneFloat('##$PVM_NAverages'))
        self.parameters['nAverages'] = nAveragesRegex.search(methodText).group(1)

        # Acquisition protocol
        acqProtRegex = re.compile(paRE.regExAngleText('##$ACQ_protocol_name'))
        match = acqProtRegex.search(acqpText)
        if match is not None:
            self.parameters['acqProtocol'] = match.group(1)
        else:
            print('acqProtocol not found, leaving blank')
            self.parameters['acqProtocol'] = ''

         # nRepetitions
        nRepsRegex = re.compile(paRE.regExOneFloat('##$PVM_NRepetitions'))
        match = nRepsRegex.search(methodText)
        if match is not None:
            self.parameters['nRepetitions'] = match.group(1)
        else:
            print('nRepetitions not found, leaving blank')
            self.parameters['nRepetitions'] = ''

        #'SaveTime':'',
        saveTimeRegex = re.compile('\#\#OWNER\=(?:\w+)\s\$\$\s([ -0-9+.-:]+)')
        self.parameters['SaveTime'] = parser.parse(saveTimeRegex.search(methodText).group(1))

        if 'singlepulse' in self.parameters['PulseProg'].lower():
            return

        # Reference power
        refPowerRegex = re.compile(paRE.regExOneFloat('##$PVM_RefPowCh1'))
        match = refPowerRegex.search(methodText)
        if match is not None:
            self.parameters['refPower'] = match.group(1)
        else:
            print('refPower not found, leaving blank')
            self.parameters['refPower'] = ''
            #print('Scan ', self.parameters['ScanNum'], ': refPower not found')

        # Receiver Gain
        refGainRegex = re.compile(paRE.regExOneFloat('##$RG'))
        self.parameters['ReceiverGain'] = refGainRegex.search(acqpText).group(1)

        # Echo time
        #curRegexString=re.escape('##$echo=')+numInParentheses+'\s'+listOfFloats
        pvEchoTimeRegex = re.compile(paRE.regExFloatArray('##$ACQ_echo_time'))
        self.parameters['EchoTime'] = pvEchoTimeRegex.search(acqpText).group(1).replace('\n', '')

        # Recovery time
        pvRecovTimeRegex = re.compile(paRE.regExFloatArray('##$ACQ_recov_time'))
        self.parameters['RecovTime'] = pvRecovTimeRegex.search(acqpText).group(1).replace('\n', '')

        # Number of echoes
        nEchoesRegex = re.compile(paRE.regExOneFloat('##$NECHOES'))
        self.parameters['nEchoes'] = nEchoesRegex.search(acqpText).group(1)

        # Number of slices
        nSlicesRegex = re.compile(paRE.regExFloatArray('##$PVM_SPackArrNSlices'))
        self.parameters['nSlices'] = nSlicesRegex.search(methodText).group(1).replace('\n', '')

        # Number of slice packs
        nSlicePacksRegex = re.compile(paRE.regExOneFloat('##$PVM_NSPacks'))
        self.parameters['nSlicePacks'] = nSlicePacksRegex.search(methodText).group(1)

        # Field of view
        fovRegex = re.compile(paRE.regExFloatArray('##$PVM_Fov'))
        self.parameters['FOV'] = fovRegex.search(methodText).group(1).replace('\n', '')

        # Matrix
        matrixRegex = re.compile(paRE.regExFloatArray('##$PVM_Matrix'))
        self.parameters['Matrix'] = matrixRegex.search(methodText).group(1).replace('\n', '')

        # SliceThick
        sliceThickRegex = re.compile(paRE.regExOneFloat('##$PVM_SliceThick'))
        self.parameters['SliceThick'] = sliceThickRegex.search(methodText).group(1)

        # SliceSep
        sliceSepRegex = re.compile(paRE.regExFloatArray('##$PVM_SPackArrSliceGap'))
        self.parameters['SliceSep'] = sliceSepRegex.search(methodText).group(1).replace('\n', '')

        # SliceList
        sliceListRegex = re.compile(paRE.regExFloatArray('##$PVM_ObjOrderList'))
        self.parameters['SliceList'] = sliceListRegex.search(methodText).group(1).replace('\n', '')

        # SliceOffset
        sliceOffsetRegex = re.compile(paRE.regExFloatArray('##$PVM_SliceOffset'))
        self.parameters['SliceOffset'] = sliceOffsetRegex.search(methodText).group(1).replace('\n', '')

        # SlicePackOffset
        slicePackOffsetRegex = re.compile(paRE.regExFloatArray('##$PVM_SPackArrSliceOffset'))
        self.parameters['SlicePackOffset'] = slicePackOffsetRegex.search(methodText).group(1).replace('\n', '')

        # ReadOffset
        readOffsetRegex = re.compile(paRE.regExFloatArray('##$PVM_ReadOffset'))
        self.parameters['ReadOffset'] = readOffsetRegex.search(methodText).group(1).replace('\n', '')

        # PhaseOffset
        phaseOffsetRegex = re.compile(paRE.regExFloatArray('##$PVM_Phase1Offset'))
        self.parameters['PhaseOffset'] = phaseOffsetRegex.search(methodText).group(1).replace('\n', '')

        # ImageOrient
        imageOrientRegex = re.compile(paRE.regExTextArray('##$PVM_SPackArrSliceOrient'))
        self.parameters['ImageOrient'] = imageOrientRegex.search(methodText).group(1).replace('\n', '')

        #'SlicepackVec':'',

        # nEvolutionCycles
        nEvolCycleRegex = re.compile(paRE.regExOneFloat('##$PVM_NEvolutionCycles'))
        match = nEvolCycleRegex.search(methodText)
        if match is not None:
            self.parameters['nEvolutionCycles'] = match.group(1)
        else:
            print('nEvolutionCycles not found, leaving blank')
            self.parameters['nEvolutionCycles'] = ''

        #'EvolutionDelay':'',

        #'FlipAngle'
        flipAngleRegex = re.compile(paRE.regExOneFloat('##$ACQ_flip_angle'))
        self.parameters['FlipAngle'] = flipAngleRegex.search(acqpText).group(1)

        #'IdealFAat':'',

        #'BasicFreq'
        basicFreqRegex = re.compile(paRE.regExOneFloat('##$BF1'))
        self.parameters['BasicFreq'] = basicFreqRegex.search(acqpText).group(1)

        #'SpecWidth'
        specWidthRegex = re.compile(paRE.regExOneFloat('##$SW_h'))
        self.parameters['SpecWidth'] = specWidthRegex.search(acqpText).group(1)

        #'ExcitationPulse':'',
        excPulseRegex = re.compile(paRE.regExOneLineAngleText('##$ExcPulse1Enum'))
        match = excPulseRegex.search(methodText)
        if match is not None:
            self.parameters['ExcitationPulse'] = match.group(1)
        else:
            self.parameters['ExcitationPulse'] = ''

        #RefocusingPulse
        refPulseRegex = re.compile(paRE.regExOneLineAngleText('##$RefPulse1Enum'))
        match = refPulseRegex.search(methodText)
        if match is not None:
            self.parameters['RefocusingPulse'] = match.group(1)
        else:
            print('RefocusingPulse not found, leaving blank')
            self.parameters['RefocusingPulse'] = ''
        #'PulseShape':'',

        #ReadOutDir
        readOutDirRegex = re.compile(paRE.regExTextArray('##$PVM_SPackArrReadOrient'))
        self.parameters['ReadOutDir'] = readOutDirRegex.search(methodText).group(1).replace('\n', '')

        #RareFactor
        rareFactorRegex = re.compile(paRE.regExOneFloat('##$PVM_RareFactor'))
        match = rareFactorRegex.search(methodText)
        if match is not None:
            self.parameters['RareFactor'] = match.group(1).replace('\n', '')
        else:
            print('nEvolutionCycles not found, leaving blank')
            self.parameters['RareFactor'] = ''

        #FatSat
        fatSatRegex = re.compile(paRE.regExOneLineText('##$PVM_FatSupOnOff'))
        match = fatSatRegex.search(methodText)
        if match is not None:
            self.parameters['FatSat'] = match.group(1).replace('\n', '')
        else:
            print('FatSat not found, leaving blank')
            self.parameters['FatSat'] = ''

        #'Gating':'',
        gatingRegex = re.compile(paRE.regExOneLineText('##$PVM_TriggerModule'))
        match = gatingRegex.search(methodText)
        if match is not None:
            self.parameters['Gating'] = match.group(1).replace('\n', '')
        else:
            print('Gating not found, leaving blank')
            self.parameters['Gating'] = ''
        #'wordType':'',
        #'rawWordType':'',

        #'ByteOrder':'',
        byteOrderRegex = re.compile(paRE.regExOneLineText('##$BYTORDA'))
        self.parameters['ByteOrder'] = byteOrderRegex.search(acqpText).group(1)

        #'Filename':'',
        #'MusWt':'',
        #'subjOrientHF':'',
        #'subjOrientSP':'',

        #'dwiBvals':'',
        #'dwiA0':'',

        #FlowDir
        flowDirRegex = re.compile(paRE.regExOneLineText('##$FlowEncodingDirection'))
        match = flowDirRegex.search(methodText)
        if match is not None:
            self.parameters['FlowDir'] = match.group(1)
        else:
            print('FlowDir not found, leaving blank')
            self.parameters['FlowDir'] = ''

        #Venc
        vEncRegex = re.compile(paRE.regExOneFloat('##$FlowRange'))
        match = vEncRegex.search(methodText)
        if match is not None:
            self.parameters['Venc'] = match.group(1)
        else:
            print('Venc not found, leaving blank')
            self.parameters['Venc'] = ''

        # PV Version
        curRegexString = re.escape('##$ACQ_sw_version = ')+paRE.numInParentheses+'\s'+ '\<(PV (\d+)\.\d+\.*\d*)\>'
        pvVerRegex = re.compile(curRegexString)
        pvVerSearch = pvVerRegex.search(acqpText)
        if pvVerSearch is not None:
            self.parameters['PVver'] = pvVerSearch.group(1)
            self.parameters['Major PV ver'] = pvVerSearch.group(2)
        else:
            print('PVver not found, leaving blank')
            self.parameters['PVver'] = ''
            self.parameters['Major PV ver'] = ''

        for p in self.csvParameters.keys():
            self.csvParameters[p] = self.parameters[p]

# This is where we iterate over directories and compile parameters from all scans i
# in a study into one CSV file

### multi directory chooser code

class GetExistingDirectories(QFileDialog):
    def __init__(self, *args):
        super(GetExistingDirectories, self).__init__(*args)
        self.setOption(self.DontUseNativeDialog, True)
        self.setFileMode(self.Directory)
        self.setOption(self.ShowDirsOnly, True)
        self.findChildren(QListView)[0].setSelectionMode(QAbstractItemView.ExtendedSelection)
        self.findChildren(QTreeView)[0].setSelectionMode(QAbstractItemView.ExtendedSelection)


qapp = QCoreApplication.instance()
if qapp is None:
    qapp = QApplication(sys.argv)
dlg = GetExistingDirectories()
if dlg.exec_() == QDialog.Accepted:
    targetDirs = dlg.selectedFiles()

### end multi directory chooser code

for curDir in targetDirs:
    acqpList = list()
    studyDir_components = os.listdir(os.path.join(curDir, 'Raw_Data'))
    for c in studyDir_components:
        if os.path.isdir(os.path.join(curDir, 'Raw_Data', c)):
            studyDir = os.path.join(curDir, 'Raw_Data', c)
        #if os.path.isfile(os.path.join(curDir, 'Raw_Data', c)):
            #subjectPath = os.path.join(curDir, 'Raw_Data', c)

    scanDirs = os.listdir(studyDir)


    curCsvFile = os.path.join(curDir, os.path.basename(curDir)+'_acqp.csv')
    print(curCsvFile)
    with open(curCsvFile, 'w') as csvfile:
        fieldnames = ['ScanNumber', 'acqProtocol',
                      'RepTime', 'EchoTime', 'FlipAngle', 'RareFactor',
                      'nEchoes', 'FOV', 'Matrix', 'nSlices', 'SliceThick',
                      'SliceSep', 'nAverages', 'nEvolutionCycles', 'nRepetitions',
                      'FatSat', 'Gating', 'ImageOrient', 'SlicePackOffset',
                      'ReadOutDir', 'ReadOffset', 'PhaseOffset', 'ExcitationPulse',
                      'RefocusingPulse', 'SpecWidth', 'refPower', 'ReceiverGain',
                      'SaveTime', 'FlowDir', 'Venc']
        writer = csv.DictWriter(csvfile, lineterminator='\n', fieldnames=fieldnames)
        writer.writeheader()

        for d in scanDirs:
            if d.isnumeric():
                methodPath = os.path.join(studyDir, d, 'method')
                methodFile = open(methodPath)
                methodText = methodFile.read()
                methodFile.close()

                acqpPath = os.path.join(studyDir, d, 'acqp')
                acqpFile = open(acqpPath)
                acqpText = acqpFile.read()
                acqpFile.close()

                curAcqp = Acqp(d)
                curAcqp.readParameters(acqpText, methodText)
                writer.writerow(curAcqp.csvParameters)

                acqpList.append(curAcqp)

        minTime = acqpList[0].parameters['SaveTime']
        maxTime = acqpList[-1].parameters['SaveTime']
        for scan in acqpList:
            if scan.parameters['SaveTime'] < minTime:
                minTime = scan.parameters['SaveTime']
            elif scan.parameters['SaveTime'] > maxTime:
                maxTime = scan.parameters['SaveTime']

        writer2 = csv.writer(csvfile, lineterminator='\n', delimiter=',')
        writer2.writerow('')
        writer2.writerow(['Start date:', minTime.date(), 'Start time:', minTime.strftime('%H:%M')])
        writer2.writerow(['Finish date:', maxTime.date(), 'Finish time:', maxTime.strftime('%H:%M')])
        elapsedTime = (maxTime-minTime).total_seconds()/60
        writer2.writerow(['Elapsed time:', str.format("{0:.1f}", elapsedTime), 'min'])
        writer2.writerow('')
        writer2.writerow('')
        writer2.writerow(['STUDY INFORMATION'])
        writer2.writerow('')

        subjectPath = os.path.join(studyDir, 'subject')
        subjectFile = open(subjectPath)
        subjectText = subjectFile.read()
        subjectFile.close()

        subjectIDRegex = re.compile(paRE.regExAngleText('##$SUBJECT_id'))
        writer2.writerow(['Subject ID:', '', subjectIDRegex.search(subjectText).group(1).replace('\n', '')])

        studyNameRegex = re.compile(paRE.regExAngleText('##$SUBJECT_study_name'))
        writer2.writerow(['Study Name:', '', studyNameRegex.search(subjectText).group(1).replace('\n', '')])

        sexRegex = re.compile(paRE.regExAngleText('##$SUBJECT_sex'))
        match = sexRegex.search(subjectText)
        if match is not None:
            writer2.writerow(['Sex:', '', match.group(1).replace('\n', '')])
        else:
            print('No sex specified\n')
            writer2.writerow('')

        weightRegex = re.compile(paRE.regExOneFloat('##$SUBJECT_weight'))
        match = weightRegex.search(subjectText)
        if match is not None:
            writer2.writerow(['Weight:', '', match.group(1).replace('\n', '')])
        else:
            print('No weight specified\n')

        remarkRegex = re.compile(paRE.regExComment('##$SUBJECT_remarks'))
        match = remarkRegex.search(subjectText)
        if match is not None:
            writer2.writerow(['Subject Comments:', '', match.group(0).replace('\n', '')])
        else:
            print('No subject comments specified\n')
            writer2.writerow(['Subject Comments:'])

        commentRegex = re.compile(paRE.regExComment('##$SUBJECT_comment'))
        match = commentRegex.search(subjectText)
        if match is not None:
            writer2.writerow(['Study Comments:', '', match.group(0).replace('\n', '')])
        else:
            print('No study comments specified\n')
            writer2.writerow(['Study Comments:'])

#pprint.pprint(firstAcqp.parameters)
#pprint.pprint(firstAcqp.csvParameters)
            