import logging 
import shutil
import datetime
import json
import sys
import os
import re
#from tkinter import E               


coreCmd835 = ("ST[*]835[*][0-9][0-9][0-9][0-9]"
                ,"N1[*]PR"
                ,"N1[*]PE"
                ,"SE[*]"
                ,"GE[*]")

coreDisplay835 = (1,1,1,1,1)
coreAction835 = (1,0,2,4,3)

typeSearch = ("ST[*]277","ST[*]835","ST[*]837")
typeReturn = ("277","835","837")

extractedPayee = ""

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
                logging.error("ERROR creating directory:\t%s\n\t%s" % (dirNew,e))
          else:
              pass
      except IOError as e:
        logging.error("ERROR verifying path:\t%s\n\t%s" % (dirNew,e))
  else:
      pass    
  return dirNew      

#*******************************************************************************
def CheckLogFileSize(logName):
    try:
        maxFileSize = 10000
        maxNumberOfBackups = 10
        if os.path.exists(logName):
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
        else:
            logFile = open(logName,'w')
            logFile.close()
            pass
    except Exception as e:
        logging.error("CheckLogFileSize %s\n\t%s" % (logName,e))
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
                print("%s\tVerifying file type: %s" % (currentDateTime,sourceFileName))

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
                            logging.error("Error iLineCount: %s\n\t%s" % (iLineCount,e))
                        iLoop+=1
                    iLineCount+=1
            finally:
                if not file.closed:        
                    file.close()
    except IOError as e:
        logging.error("ERROR opening source file:\t%s\n%s" % (sourceFileName,e))
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
#******** DeleteEmptyExtractedFile *********************************************
#*******************************************************************************
def DeleteEmptyExtractedFile():
    try:
        os.remove(extractedFullPath)
    except Exception as e:
        logging.error("Removing empty Extracted file ERROR:\t%s\n\t%s" % (extractedFullPath,e))

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
        logging.error("WriteCurrentList ERROR:\t%s\n\t%s" % (extractProcessed,e))
    finally:
        return (txnProcessed,txnExtracted) 

#*******************************************************************************
#******** process835DataCORE ***************************************************
#*******************************************************************************
def process835DataCORE(sourceFileName):

    try:
        with open(sourceFileName,'r') as file:
            currentDateTime = str(datetime.datetime.now().strftime(logDateTimeFormat))
            print("%s\tSplitting 835 data: %s" % (currentDateTime,sourceFileName))
            logging.info("Splitting 835 data: %s" % sourceFileName)

            currentFile = file.read()
            currentFileLines = currentFile.split("~")
            currentFileLineCount = len(currentFile.split("~"))
            iLineCount = 0
            currentTxnTuple = 0,0
            txnLineCount = 0
            writeExtractProcessed = 0
            extractedFileAccessed = 0
            try:
                while iLineCount < currentFileLineCount:
                    currentLine =  currentFileLines[iLineCount].replace("\n","")
                    iLoop = 0
                    bAppended = False                    
                    while iLoop < len(coreCmd835): 
                        match = re.search(coreCmd835[iLoop],currentLine)
                        if match and match.start() == 0:
                            if (coreDisplay835[iLoop] == 1):
                                print("835 [%s]\t%s" % (iLineCount,currentLine))

                            if coreAction835[iLoop] == 1:       #ST*835*    beginning of a transaction set
                                currentTxnTuple = WriteCurrentList(writeExtractProcessed,currentTxnTuple,txnLineCount)
                                writeExtractProcessed = 0
                                txnLineCount = 0
                            elif coreAction835[iLoop] == 2:     #N1*PE      payee indicator
                                writeExtractProcessed = ReturnExtractProcess(currentLine)
                                if writeExtractProcessed == 2:
                                    extractedFileAccessed += 1 
                            elif coreAction835[iLoop] == 3:     #GE*        end of the group set
                                currentTxnTuple = WriteCurrentList(writeExtractProcessed,currentTxnTuple,txnLineCount)
                                writeExtractProcessed = 0
                        iLoop+=1
                    if not bAppended:
                        currentTransationSet.append(currentLine)
                    iLineCount+=1
                    txnLineCount += 1
                writeExtractProcessed = 0
                writeExtractProcessed = WriteCurrentList(writeExtractProcessed,currentTxnTuple,txnLineCount)
            except Exception as e:
                logging.error("Error iLineCount: %s\n\t%s" % (iLineCount,e))
               
            currentDateTime = str(datetime.datetime.now().strftime(logDateTimeFormat))
            print("%s\tCompleted processing of : %s" % (currentDateTime,sourceFileName))
            if not file.closed:        
                file.close()
            if extractedFileAccessed == 0:
                DeleteEmptyExtractedFile()
    except IOError as e:
        logging.error("Error opening 835 source file:\t%s\n\t%s" % (sourceFileName,e))

    
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
    logging.error("Error opening config file:\t%s\n\t%s" % (configFilename,e))
    
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
try:
    logging.basicConfig(filename=localLogPath, encoding='utf-8', level=logLevel,format='%(asctime)s\t%(levelname)s\t%(message)s', datefmt='%Y-%m-%d %H:%M')
except Exception as e:
    print("Init logging ERROR: %s" % e)

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
        fileDateTime = datetime.datetime.now().strftime("%Y_%m_%d%H%M")           
        sourceFilePath = os.path.join(sourcePath, fileName)
        if (os.path.isfile(sourceFilePath)==True):                  #determine this is a file and fits the filter pattern and not a directory

            fileTypeReturned = DetermineFileFormat(sourceFilePath)

            extractedFileName = ""
            processedFileName = ""
            archivedFileName = ""

            fileNamePartCount = len(os.path.basename(fileName).split('.'))
            curPartCount = 0
            if fileNamePartCount > 1:
                while curPartCount < (fileNamePartCount-1):
                    extractedFileName += os.path.basename(fileName).split('.')[curPartCount]
                    processedFileName += os.path.basename(fileName).split('.')[curPartCount]
                    archivedFileName += os.path.basename(fileName).split('.')[curPartCount]
                    if fileNamePartCount-curPartCount > 2:
                        extractedFileName += '_'
                        processedFileName += '_'
                        archivedFileName += '_'
                    curPartCount += 1
            else:
                extractedFileName = fileName
                processedFileName = fileName
                archivedFileName = fileName

            extractedFileName += extractedSuffix.replace("<#DATETIME#>",fileDateTime) 
            processedFileName += processedSuffix.replace("<#DATETIME#>",fileDateTime)
            archivedFileName += archivedSuffix.replace("<#DATETIME#>",fileDateTime)

            extractedFileName += "." + fileTypeReturned
            processedFileName += "." + fileTypeReturned
            if fileNamePartCount > 1:
                 archivedFileName += "." + os.path.basename(fileName).split('.')[fileNamePartCount-1]
            
            logging.info("extractedFileName[%s]: %s from: %s" % (fileNamePartCount,extractedFileName,fileName))
            logging.info("processedFileName[%s]: %s from: %s" % (fileNamePartCount,processedFileName,fileName))
            logging.info("archivedFileName[%s]: %s from: %s" % (fileNamePartCount,archivedFileName,fileName))


            if bVerbose:
                logging.debug("archivedFileName: %s" % str(archivedFileName))

            extractedFullPath = os.path.join(extractedPath, extractedFileName)
            processedFullPath = os.path.join(processedPath, processedFileName)
            archivedFullPath = os.path.join(archivedPath, archivedFileName)

            logging.info("Document type: %s %s" % (fileTypeReturned,sourceFilePath))

            if fileTypeReturned == "835":
                print("\t%s is an %s file format." % (sourceFilePath,fileTypeReturned))
                try:
                    extractedFile = open(extractedFullPath,'w')
                    extractedFile.close()
                    processedFile = open(processedFullPath,'w')
                    processedFile.close()
                except Exception as e:
                    logging.error("Extracted/processed file creation ERROR:\t%s\t%s\n\t%s" % (extractedFullPath,processedFullPath,e))
                    break
                else:
                    process835DataCORE(sourceFilePath)
                    
            else:
                print("\t%s is a %s file format and not configured for processing." % (sourceFilePath,fileTypeReturned))
                logging.warning("%s file format is not configured for processing: %s" %(fileTypeReturned,sourceFilePath))

            #****** archive if path specified                
            if(archivedFullPath != "") and (bArchive):                  #move source file to archive destination if path specified 
                try:  
                    shutil.move(sourceFilePath,archivedFullPath)
                except IOError as e:
                    logging.error("Failed file archival of %s to %s" % (sourceFilePath,archivedFullPath))
                else:
                    logging.info("Archived %s to %s" % (sourceFilePath,archivedFullPath)) 
                    pass
            else:
                pass
else:
    pass
if interactiveMode == "I":
    input("Press enter to exit...")

