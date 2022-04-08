import logging #import exception
import shutil
import datetime
import json
import sys
import os
import re               #Regular Expression

# Class of different styles
class textStyle():
    RESET = '\033[0m'
    BRIGHTWHITEonBLACK = '\033[1m'
    UNDERLINE = '\033[4m'
    GRAYonWHITE = '\033[7m'
    BLACKonBLACK = '\033[30m'
    REDonBLACK = '\033[31m'
    GREENonBLACK = '\033[32m'
    YELLOWonBLACK = '\033[33m'
    BLUEonBLACK = '\033[34m'
    MAGENTAonBLACK = '\033[35m'
    CYANonBLACK = '\033[36m'
    WHITEonBLACK = '\033[37m'
    WHITEonRED = '\033[41m'
    WHITEonGREEN = '\033[42m'
    WHITEonYELLOW = '\033[43m'
    WHITEonBLUE = '\033[44m'
    WHITEonMAGENTA = '\033[45m'
    WHITEonCYAN = '\033[46m'
    GRAYonWHITE = '\033[47m'
    GRAYonBLACK = '\033[90m'
    GRAYonLtGRAY = '\033[100m'
    GRAYonLtRED = '\033[101m'
    GRAYonLtGREEN = '\033[102m'
    GRAYonLtYELLOW = '\033[103m'
    GRAYonLtBLUE = '\033[104m'
    GRAYonLtMAGENTA = '\033[105m'
    GRAYonLtCYAN = '\033[106m'

coreCmd835 = ("ST[*]835[*][0-9][0-9][0-9][0-9]"
                ,"N1[*]PR"
                ,"N1[*]PE"
                ,"SE[*]"
                ,"GE[*]")
coreColor835 = (textStyle.GREENonBLACK
            ,textStyle.GRAYonBLACK
            ,textStyle.CYANonBLACK
            ,textStyle.REDonBLACK
            ,textStyle.BRIGHTWHITEonBLACK)
coreDisplay835 = (1,1,1,1,1)
coreAction835 = (1,0,2,4,3)

typeSearch = ("ST[*]277","ST[*]835","ST[*]837")
typeReturn = ("277","835","837")

extractedPayee = "N1[*]PE[*]MIDWEST RADIOLOGY AND IMAGING"


clearScreen = lambda: os.system('CLS')      #Windows
clearScreenVS = lambda: os.system('clear')  #specific to VS Code and linux

bDebug = False
bVerbose = False
logDateTimeFormat = "%Y-%m-%d %H:%M:%S"    

os.chdir(os.path.dirname(__file__))

currentAppPath = sys.argv[0]
currentAppName = os.path.basename(__file__)
curentAppBasePath = currentAppPath.replace(currentAppName,"")
currentAppName = currentAppName.replace(".py","")

#*******************************************************************************
def clearConsole():
    try:
        clearScreen()
        #clearScreenVS()
    except:
        pass

#*******************************************************************************
def VerifyAndCreateDirectory(dirNew):
  if (dirNew != ""):
      try:
          if not os.path.exists(dirNew):
              try:
                  os.makedirs(dirNew)
              except IOError as e:
                print(textStyle.REDonBLACK + "ERROR creating directory:\t",end='')
                print(textStyle.YELLOWonBLACK + "%s" % dirNew)
                print(textStyle.RESET + "%s" % e)
          else:
              pass
      except IOError as e:
        print(textStyle.REDonBLACK + "ERROR verifying path:\t",end='')
        print(textStyle.YELLOWonBLACK + "%s" % dirNew)
        print(textStyle.RESET + "%s" % e)
  else:
      pass    
  return dirNew      

#*******************************************************************************
def CheckLogFileSize(logName):
    try:
        maxFileSize = 10000
        maxNumberOfBackups = 10
        logFileSize = os.stat(logName)
        if (logFileSize.st_size > maxFileSize):
            fileNameCorePath,fileNameExtension = os.path.splitext(logName)
            newLogNameCore = fileNameCorePath + "$$" + fileNameExtension
            for x in range(maxNumberOfBackups,0,-1):
                newLogName = newLogNameCore.replace("$$","-" + str(x))
                if (x==10)and(os.path.exists(newLogName)):
                    os.remove(newLogName)
                newLogSubName = newLogNameCore.replace("$$","-" + str(x-1))
                if (x>1)and(os.path.exists(newLogSubName)):
                    os.rename(newLogSubName,newLogName)  
            os.rename(logName,newLogName)
        else:
            pass
    except Exception as e:
        logging.error("CheckLogFileSize %s" % logName)
    finally:
        return logName    

#*******************************************************************************
#******** DetermineFileFormat **************************************************
#*******************************************************************************
def DetermineFileFormat(sourceFileName):
    
    if (bVerbose):
        logging.debug("DetermineFileFormat sourceFileName: " + sourceFileName) 
    try:
        with open(sourceFileName,'r') as file:
            try:
                docType = "unknown"
                iLineCount = 0
                currentDateTime = str(datetime.datetime.now().strftime(logDateTimeFormat))
                print(textStyle.RESET + "%s\t" % currentDateTime,end='')
                print(textStyle.YELLOWonBLACK + "Verifying file type: ",end='')
                print(textStyle.RESET + "%s" % sourceFileName)

                currentFile = file.read()
                currentFileLines = currentFile.split("~")
                currentFileLineCount = len(currentFile.split("~"))
                while iLineCount < currentFileLineCount:
                    currentLine =  currentFileLines[iLineCount]
                    if bVerbose and iLineCount < 10:
                        logging.debug("%s\t%s" % (iLineCount,currentLine))
                    iLoop = 0
                    while iLoop < 3: 
                        try:
                            match = re.search(typeSearch[iLoop],currentLine)
                            if match:
                                docType = typeReturn[iLoop]
                                break
                        except Exception as e:
                            print(textStyle.REDonBLACK + "ERROR:\t",end='')
                            print(textStyle.RESET + "iLineCount: %s %s" % (iLineCount,e))
                        iLoop+=1
                    iLineCount+=1
            finally:
                if not file.closed:        
                    file.close()
    except IOError as e:
        print(textStyle.REDonBLACK + "ERROR opening source file:\t",end='')
        print(textStyle.YELLOWonBLACK + "%s" % sourceFileName)
        print(textStyle.RESET + "%s" % e)

    finally:
        if (bVerbose): 
            logging.debug("Document type: %s" % docType)
        return docType

#*******************************************************************************
#******** ReturnExtractProcess *************************************************
#*******************************************************************************
def ReturnExtractProcess(currentLine):
    returnValue = 1
    match = re.search(extractedPayee,currentLine)
    if match:
        returnValue = 2
    return returnValue

#*******************************************************************************
#******** WriteCurrentList *****************************************************
#*******************************************************************************
def WriteCurrentList(extractProcessed,txnCountTuple,currentLineCount):
    try:
        txnProcessed,txnExtracted = txnCountTuple
        extractedFile = open(extractedFullPath,'a')
        processedFile = open(processedFullPath,'a')
        currentLine = 0
        while currentLine < len(currentTransationSet):
            if not currentTransationSet[currentLine] == "":
                writeLine = currentTransationSet[currentLine] + "~\n"
                loopWrite = 0
                while loopWrite < len(coreCmd835): 
                    match = re.search(coreCmd835[loopWrite],writeLine)
                    if match and match.start() == 0:
                        if coreAction835[loopWrite] == 1:       #ST*835*    beginning of a transaction set
                            writeLine = "ST*835*%s~\n" % str(1000 + int(txnExtracted)+1)
                        elif coreAction835[loopWrite] == 4:     #SE*835     end oftransaction set 
                            writeLine = "SE*%s*%s~\n" % (str(currentLineCount),str(1000 + int(txnExtracted)+1))
                        elif coreAction835[loopWrite] == 3:     #GE*        end of the group set
                            writeLine = "GE*%s*1~\n" % str(int(txnExtracted))
                    loopWrite+=1
                if extractProcessed in (0,2):
                    extractedFile.write(writeLine)

                loopWrite = 0
                while loopWrite < len(coreCmd835): 
                    match = re.search(coreCmd835[loopWrite],writeLine)
                    if match and match.start() == 0:
                        if coreAction835[loopWrite] == 1:       #ST*835*    beginning of a transaction set
                             writeLine = "ST*835*%s~\n" % str(1000 + int(txnExtracted)+1)
                        elif coreAction835[loopWrite] == 4:     #SE*835     end oftransaction set 
                            writeLine = "SE*%s*%s~\n" % (str(currentLineCount),str(1000 + int(txnExtracted)+1))
                        elif coreAction835[loopWrite] == 3:     #GE*        end of the group set
                            writeLine = "GE*%s*1~\n" % str(int(txnExtracted))
                    loopWrite+=1
                if extractProcessed in (0,1):
                    processedFile.write(writeLine)

            currentLine += 1
        extractedFile.close()
        processedFile.close()

        if extractProcessed == 1:
            txnProcessed +=1
        if extractProcessed == 2:
            txnExtracted +=1

        currentTransationSet.clear()       

    except Exception as e:
        print(textStyle.REDonBLACK + " WriteCurrentList ERROR:\t",end='')
        print(textStyle.RESET + "extractProcessed: %s \n%s" % (extractProcessed,e))
    finally:
        return (txnProcessed,txnExtracted) 

#*******************************************************************************
#******** process835DataCORE ***************************************************
#*******************************************************************************
def process835DataCORE(sourceFileName):

    try:
        with open(sourceFileName,'r') as file:
            currentDateTime = str(datetime.datetime.now().strftime(logDateTimeFormat))
            print(textStyle.RESET + "%s\t" % currentDateTime,end='')
            print(textStyle.YELLOWonBLACK + "Splitting 835 data: ",end='')
            print(textStyle.RESET + "%s" % sourceFileName)
            logging.info("Splitting 835 data: %s" % sourceFileName)

            currentFile = file.read()
            currentFileLines = currentFile.split("~")
            currentFileLineCount = len(currentFile.split("~"))
            iLineCount = 0
            currentTxnTuple = 0,0
            txnLineCount = 0
            writeExtractProcessed = 0
            try:
                while iLineCount < currentFileLineCount:
                    currentLine =  currentFileLines[iLineCount].replace("\n","")
                    iLoop = 0
                    bAppended = False                    
                    while iLoop < len(coreCmd835): 
                        match = re.search(coreCmd835[iLoop],currentLine)
                        if match and match.start() == 0:
                            if (coreDisplay835[iLoop] == 1):
                                print(textStyle.GREENonBLACK + "835 ",end='')
                                print(textStyle.RESET + "[",end='')
                                print(textStyle.CYANonBLACK + "%s" % iLineCount,end='')
                                print(textStyle.RESET + "]\t",end='')
                                print(coreColor835[iLoop] + "%s" % coreCmd835[iLoop],end='')

                            if coreAction835[iLoop] == 1:       #ST*835*    beginning of a transaction set
                                currentTxnTuple = WriteCurrentList(writeExtractProcessed,currentTxnTuple,txnLineCount)
                                writeExtractProcessed = 0
                                txnLineCount = 0
                            elif coreAction835[iLoop] == 2:     #N1*PE      payee indicator
                                writeExtractProcessed = ReturnExtractProcess(currentLine)
                            elif coreAction835[iLoop] == 3:     #GE*        end of the group set
                                currentTxnTuple = WriteCurrentList(writeExtractProcessed,currentTxnTuple,txnLineCount)
                                writeExtractProcessed = 0

                            if writeExtractProcessed == 2:
                                print(textStyle.MAGENTAonBLACK + "\t%s" % currentLine)
                            else:
                                print(textStyle.RESET + "\t%s" % currentLine)
                        iLoop+=1
                    if not bAppended:
                        currentTransationSet.append(currentLine)
                    iLineCount+=1
                    txnLineCount += 1
                writeExtractProcessed = 0
                writeExtractProcessed = WriteCurrentList(writeExtractProcessed,currentTxnTuple,txnLineCount)
            except Exception as e:
                print(textStyle.REDonBLACK + "ERROR:\t",end='')
                print(textStyle.RESET + "iLineCount: %s %s" % (iLineCount,e))
               
            currentDateTime = str(datetime.datetime.now().strftime(logDateTimeFormat))
            print(textStyle.RESET + "%s\t" % currentDateTime,end='')
            print(textStyle.YELLOWonBLACK + "Completed processing of : ",end='') 
            print(textStyle.RESET + "%s" % sourceFileName)
            if not file.closed:        
                file.close()
    except IOError as e:
        print(textStyle.REDonBLACK + "ERROR opening 835 source file:\t",end='')
        print(textStyle.YELLOWonBLACK + "%s" % sourceFileName)
        print(textStyle.RESET + "%s" % e)

    
#*******************************************************************************
#***** START OF MAIN LOOP ******************************************************
#*******************************************************************************

extractedFullPath = ""
processedFullPath = ""
archivedFullPath = ""
currentTransationSetNumber = 0
writeExtractProcessed = 0
currentTransationSet = list()

if (len(sys.argv) == 1):
    configRequest = "PMI"      #"835Test"      #"PMI"
    
if (len(sys.argv) >= 2):
    configRequest = sys.argv[1]

if (len(sys.argv) == 3):
    interactiveMode = sys.argv[2]
else:
    interactiveMode = "X"

debugSearch = ("VERBOSE","DEBUG","INFO","WARNING","ERROR","CRITICAL")
debugReturn = (logging.DEBUG,logging.DEBUG,logging.INFO,logging.WARNING,logging.ERROR,logging.CRITICAL)
debugVerbose = (True,False,False,False,False,False)

#clearConsole()

try:
    configFilename = os.getcwd() + "\\" + currentAppName + ".json"
    with open(configFilename) as config_data:
        d = json.load(config_data)
        sourcePath = (d[configRequest]['sourcePath'])
        extractedPayee = (d[configRequest]['extractedPayee'])
        archivedSuffix = (d[configRequest]['archivedSuffix'])
        processedSuffix = (d[configRequest]['processedSuffix'])
        extractedSuffix = (d[configRequest]['extractedSuffix'])
        archivedPath = ((d[configRequest]['archivedPath']))
        processedPath = ((d[configRequest]['processedPath']))
        extractedPath = ((d[configRequest]['extractedPath']))
        bArchive = bool((d[configRequest]['archiveSource']))
        debugMode = (d[configRequest]['debugMode'])
        

    archivedPath = VerifyAndCreateDirectory((d[configRequest]['archivedPath']))
    processedPath = VerifyAndCreateDirectory((d[configRequest]['processedPath']))
    extractedPath = VerifyAndCreateDirectory((d[configRequest]['extractedPath']))

except Exception as e:
    print(textStyle.REDonBLACK + "ERROR opening config file:\t",end='')
    print(textStyle.YELLOWonBLACK + "%s" % configFilename)
    print(textStyle.RESET + "%s" % e)
    
#***** Configure Logging *****
localLogPath = VerifyAndCreateDirectory(os.getcwd() + "\\log")              #verify directory structure exists
localLogPath = os.path.join(localLogPath, configRequest + ".log")           #append logname to log directory
localLogPath = CheckLogFileSize(localLogPath)                               #maintain size and count of log files

logLevel = logging.INFO
bVerbose = False
debugLoop = 0
while debugLoop < len(debugSearch):
    match = re.search(debugSearch[debugLoop],debugMode)
    if match:
        logLevel = debugReturn[debugLoop]
        bVerbose = debugVerbose[debugLoop]
    debugLoop += 1

logging.basicConfig(filename=localLogPath, encoding='utf-8', level=logLevel,format='%(asctime)s\t%(levelname)s\t%(message)s', datefmt='%Y-%m-%d %H:%M')

logging.info("********** Beginning of process **********")

logging.debug("configFilename: %s" % configFilename)
logging.debug("configRequest: %s" % configRequest)
logging.debug("sourcePath: %s" % sourcePath)
logging.debug("extractedPayee: %s" % extractedPayee)
logging.debug("archivedSuffix: %s" % archivedSuffix)
logging.debug("processedSuffix: %s" % processedSuffix)
logging.debug("extractedSuffix: %s" % extractedSuffix)
logging.debug("archivedPath: %s" % archivedPath)
logging.debug("processedPath: %s" % processedPath)
logging.debug("extractedPath: %s" % extractedPath)
logging.debug("archiveSource: %s" % str(bArchive))
logging.debug("debugMode: %s" % debugMode)

#***** If a valid local path exists *****
if (sourcePath != ""):
    fileNames = os.listdir(sourcePath)                         #return list of file names
    for fileName in fileNames:
        fileDateTime = datetime.datetime.now().strftime("%Y-%m-%d%H%M")           
        sourceFilePath = os.path.join(sourcePath, fileName)
        if (os.path.isfile(sourceFilePath)==True):                  #determine this is a file and fits the filter pattern and not a directory

            fileTypeReturned = DetermineFileFormat(sourceFilePath)

            extractedFileName = os.path.basename(fileName).split('.')[0] + extractedSuffix.replace("<#DATETIME#>",fileDateTime) 
            extractedFileName += "." + fileTypeReturned
            processedFileName = os.path.basename(fileName).split('.')[0] + processedSuffix.replace("<#DATETIME#>",fileDateTime) 
            processedFileName += "." + fileTypeReturned
            archivedFileName = os.path.basename(fileName).split('.')[0] + archivedSuffix.replace("<#DATETIME#>",fileDateTime)
            if len(os.path.basename(fileName).split('.')) == 2:
                archivedFileName += "." + os.path.basename(fileName).split('.')[1]
            
            if bVerbose:
                logging.debug("archivedFileName: %s" % str(archivedFileName))

            extractedFullPath = os.path.join(extractedPath, extractedFileName)
            processedFullPath = os.path.join(processedPath, processedFileName)
            archivedFullPath = os.path.join(archivedPath, archivedFileName)

            logging.info("Document type: %s %s" % (fileTypeReturned,sourceFilePath))

            if fileTypeReturned == "835":
                print(textStyle.RESET + "\t%s is an " % sourceFilePath,end='')
                print(textStyle.YELLOWonBLACK + fileTypeReturned,end='')
                print(textStyle.RESET + " file format.")
                try:
                    extractedFile = open(extractedFullPath,'w')
                    extractedFile.close()
                    processedFile = open(processedFullPath,'w')
                    processedFile.close()
                except Exception as e:
                    print(textStyle.REDonBLACK + "File creation ERROR:\t",end='')
                    print(textStyle.RESET + "%s" % e)
                    break
                else:
                    process835DataCORE(sourceFilePath)
                    
            else:
                print(textStyle.RESET + "\t%s is a " % sourceFilePath,end='')
                print(textStyle.YELLOWonBLACK + fileTypeReturned,end='')
                print(textStyle.RESET + " file format and not configured for processing.")
                logging.warning("%s file format is not configured for processing: %s" %(fileTypeReturned,sourceFilePath))

            #****** archive if path specified                
            if(archivedFullPath != "") and (bArchive):                  #move source file to archive destination if path specified 
                try:  
                    shutil.move(sourceFilePath,archivedFullPath)
                except IOError as e:
                    logging.error("Failed file archival of %s\n\tto %s" % (sourceFilePath,archivedFullPath))
                else:
                    logging.info("Archived %s to \n\t%s" % (sourceFilePath,archivedFullPath)) 
                    pass
            else:
                pass
else:
    pass
if interactiveMode == "I":
    input("Press enter to exit...")

