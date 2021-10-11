# -*- coding: utf-8 -*-
"""
Created on Wed Feb 21 17:46:18 2018
Updated 10/11/2021

@author: Alex Waters

This file contains helper code for a Bruker ParaVision 6 MRI data parameter 
generator. It defines regular expressions to identify common text structures
in the parameter files.

"""

import re

numInParentheses='\(\s\d+\s\)'
numsInParentheses='\(\s(?:\d+\,*\s*)+\s\)'
text='(\w*)'
textInAngles='<([\w\.\+\-]+)>'
commentTextInAngles='<.*>'
#textInAngleArray='((<(\w*\s)+\w*>)\s)+'
textInAngleArray='((?:(<(?:\w*\s)+\w*>)\s)+)'
textArray='([\w\s\n]+)'
listOfFloats='((?:-*\d+\.*\d*[\s\n]*)+)'
oneFloat='(-*\d+\.*\d*)'

# These are helper functions to create regular expressions for standard 
# patterns we see in the ACQP and method files
def regExOneLineAngleText(paramName):
    return re.escape(paramName)+'='+textInAngles

def regExAngleTextArray(paramName):
    return re.escape(paramName)+'='+numsInParentheses+'\s'+textInAngleArray

def regExOneLineText (paramName):
    return re.escape(paramName)+'='+text

def regExAngleText(paramName):
    return re.escape(paramName)+'='+numsInParentheses+'\s'+textInAngles

def regExTextArray(paramName):
    return re.escape(paramName)+'='+numsInParentheses+'\s'+textArray

def regExFloatArray(paramName):
    return re.escape(paramName)+'='+numsInParentheses+'\s'+listOfFloats

def regExOneFloat(paramName):
    return re.escape(paramName)+'='+oneFloat

def regExNextLine(paramName):
    return re.escape(paramName)+'='+text+'\n'+text 

def regExComment(paramName):
    return re.escape(paramName)+'='+numsInParentheses+'\n'+commentTextInAngles