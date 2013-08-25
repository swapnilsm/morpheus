import argparse
import sys
import glob
import string
import subprocess
import os
from os.path import splitext
from random import randint
from operator import itemgetter

AV_CONV = "avconv"
AUDIO_FMT = "_.wav"
MFC_FMT = "_.mfc"
HCOPY = "HCopy"
HCOPY_CONFIG = "hcopyConfig"
HLIST = "HList"
UDL = "youtube-dl"
windowSize = 50
maxDiff = 20
LOG_FILE = "ha.log"

def parseArgs():
    parser = argparse.ArgumentParser()
    group = parser.add_mutually_exclusive_group()
    group.add_argument('-f', '--file', help='input video filename' )
    group.add_argument('-u', '--url', help='youtube video url' )        
    parser.add_argument('-q', '--quality', help='output video quality', type=int )
    parser.add_argument('-l', '--length', help='max highlights length', type=int )
    args = parser.parse_args()
    return args

def v2a(inFilename, quality):
    outFilename = splitext(inFilename)[0]+AUDIO_FMT
    status = subprocess.call([AV_CONV, '-y', '-i', inFilename, outFilename] )
    if ( 0 != status ):
        raise Exception("V2A Failed !!!")        
    return outFilename

def a2mfc(inFilename):
    outFilename = splitext(inFilename)[0]+MFC_FMT
    status = subprocess.call([HCOPY, '-C', HCOPY_CONFIG, inFilename, outFilename])
    if ( 0 != status ):
        raise Exception("HCopy failed !!!")
    return outFilename

def mfc2energy(inFilename):
    data = subprocess.check_output([HLIST, '-r' ,'-i', '13', inFilename])
    return data

def downloadVdo(url):
    outFilename = str(randint(0, 100000))+".mp4"
    status = subprocess.call([UDL, '-q', '-f', '18', '-o', outFilename, url ])
    if ( 0 != status ):
        raise Exception("File download from url failed !!!")    
    return outFilename

def avg(seq):
    return round(sum(seq)/len(seq),3)

def getEvents(data):
    energyList = [float(line.split()[-1]) for line in data.splitlines()]
    avgEnergy = avg(energyList)
    aboveAvg = []

    for index, value in enumerate(energyList):
        if value > avgEnergy:
            aboveAvg.append(value)
        
    avgAboveAvg = avg(aboveAvg)
    
    highPoints = []
    for index, value in enumerate(energyList):
        if value > avgAboveAvg:
            highPoints.append([index, value])
    highPoints = highPoints[len(highPoints)/10:]	
    lastPoint = startPoint = highPoints[0][0]
    eventSize = 0
    eventEnergy = 0
    events = []
    for highPoint, energy  in highPoints:
        if (highPoint - lastPoint) < maxDiff:
            eventSize+= highPoint - lastPoint
            eventEnergy += energy            
            lastPoint = highPoint
        else:
            if (eventSize > windowSize):
                events.append([startPoint/10, lastPoint/10, eventSize/10,  round(eventEnergy/eventSize,3)])
            startPoint = lastPoint= highPoint
            eventSize = 0
            eventEnergy = 0
    lastEvent = events[0]
    for event in events:
    	event.append(lastEvent[0])
	event.append(lastEvent[1])
	event.append(0.225*event[2]+120*event[3])
	lastEvent = event
    return events

def trimEvents(events, length):
    trimmedEvents = []
    sortedEvents = sorted(events, key=itemgetter(6), reverse=True)
    currentLength = 0
    while (length > currentLength and events):
        event = sortedEvents.pop(0)
        trimmedEvents.append(event)
        currentLength+= event[2]
    trimmedEvents=sorted(trimmedEvents, key=itemgetter(0))
    lastEvent = trimmedEvents[0]
    for event in trimmedEvents:
	if(event[4]!=lastEvent[4]):
		event[0]= event[4]+(event[5]-event[4])/4
		event[2]= event[2]+(event[5]-event[4])/4
	lastEvent = event
    return trimmedEvents

def cutAndStitch(events, inFilename):
    i = 0
    partFilename, ext = splitext(inFilename)
    cat = "concat:"
    for start, end, duration, energy, laststart, lastend, combo in events:
        currPartFileName = partFilename + '_' + str(i) + ext
        subprocess.call([AV_CONV, '-y', '-ss', str(start), '-i', inFilename, '-t', str(duration), '-codec', 'copy', currPartFileName])
        subprocess.call([AV_CONV, '-i', currPartFileName, '-y','-map', '0', '-c', 'copy', '-f', 'mpegts', '-bsf', 'h264_mp4toannexb', partFilename+'_'+str(i)+'.ts'])
        cat += partFilename+'_'+str(i)+'.ts|'
        i+=1
    subprocess.call([AV_CONV, '-y', '-i', cat, '-c', 'copy', partFilename+'o.mp4'])
    return 

def cleanKachara(filename):
    files = glob.glob(splitext(filename)[0]+'_*')
    for f in files:
        os.remove(f)
    return
    
def main():
    args = parseArgs()
    try:    
        if ( args.url ) :
            filename = downloadVdo(args.url)
        else :
            filename = args.file
        if (args.length) :
	   cutAndStitch(trimEvents(getEvents(mfc2energy(a2mfc(v2a(filename, 1)))), args.length), filename)
        else:
            cutAndStitch(getEvents(mfc2energy(a2mfc(v2a(filename, 1)))), filename)
        cleanKachara(filename)
        print splitext(filename)[0]+'o.mp4'
    except :
            return 1
    return 0

main()
