#^([^"]+)" to replace all before the first "
#[^"a]*$ to replace everything after the last "

#Let's retrieve the filename passed as argument
#!/usr/bin/python
#import sys, re


#print 'Number of arguments:', len(sys.argv), 'arguments.'
#print 'Argument List:', str(sys.argv)
#filename = sys.argv[1]
#print 'Filename:', str(filename)
#print 'Filename without extension:', filename.split('.', 1)[0]

#importing regular expression
import re, os, errno, shutil

#Reading file
#f = open('list.txt', 'r')
g = open('log.txt', 'w')

#^\([^()]*\) Line starting by parentheses
lineStartParentheses = re.compile('^\([^()]*\)')
#_+ underscores
underscores = re.compile('_+')
#\.[^.]*$ Everything after last point
#lastPoint = re.compile('\.[^.]*$')
#\(.*?\) Everything between parenthesis
parenthesis = re.compile('\(.*?\)')
#WRONG \([0-9]*\) Year between parenthesis
#WRONG yearBetweenParenthesis = re.compile('\(([0-9]*)\)')
#\((19[0-9]{2}|20[0-9]{2})\) Year between parenthesis
yearBetweenParenthesis = re.compile('\((19[0-9]{2}|20[0-9]{2})\)')
#([0-9]+).* Numbers
numbers = re.compile('([0-9]+).*')
#(19[0-9]{2}|20[0-9]{2}) Year
years = re.compile('(19[0-9]{2}|20[0-9]{2})')
#^0+ Leading 0s
zeros = re.compile('^0+')
#[^0-9].*$ all after the first numbers
afterNumbers = re.compile('[^0-9].*$')

#Directory to store all errors
try:
    os.makedirs('final/errors')
except OSError, e:
    if e.errno != errno.EEXIST:
        raise
    else:
        g.write('\nDirectory already exist: final/errors')
    
#For each file
#for line in f:
dirList=os.listdir('comics_to_rename/')
for line in dirList:
    yearValue = ''
    issueValue = ''
    
    #Remove extension
    #fileNameNoExtension = lastPoint.sub('', line.strip(' \t\n\r'))
    fileNameNoExtension, fileExtension = os.path.splitext(line.strip(' \t\n\r'))
    #Remove first set of parentheses if the line start with them
    lineNoStartParentheses = lineStartParentheses.sub('', fileNameNoExtension.strip(' \t\n\r'))
    g.write('\nInitial filename: ' + lineNoStartParentheses)
    #Replace underscores by spaces
    noUnderscores = underscores.sub('rrrrr', lineNoStartParentheses.strip(' \t\n\r'))
    
    #Search for year between parenthesis
    year = yearBetweenParenthesis.search(noUnderscores)
    if year:
        yearValue = ' - Year ' + year.group(1)
    
    #Remove all parenthesis
    fileNameNoParenthesis = parenthesis.sub('', fileNameNoExtension).strip(' \t\n\r')
    
    #if we cannot find the year, maybe it's not within parenthesis?
    year = years.search(fileNameNoParenthesis)
    if year:
        yearValue = ' - Year ' + year.group(1)
        
    #Remove year
    fileNameNoParenthesis = years.sub('', fileNameNoParenthesis).strip(' \t\n\r')
    
    #Search for issue numbers
    #And remove leading 0s
    issue = numbers.search(fileNameNoParenthesis)
    if issue:
        cleanedIssueNumber = afterNumbers.sub('', issue.group(0))
        issueValue = ' - Issue ' + zeros.sub('', cleanedIssueNumber)
        #issueValue = ' - Issue ' + zeros.sub('', issue.group(0))
    
    #Remove numbers
    fileNameNoNumbers = numbers.sub('', fileNameNoParenthesis).strip(' \t\n\r')
    
    #Create directories
    try:
        os.makedirs('final/' + fileNameNoNumbers)
        g.write('\nCreated directory: ' + fileNameNoNumbers)
    except OSError, e:
        if e.errno != errno.EEXIST:
            raise
        else:
            g.write('\nDirectory already exist: final/' + fileNameNoNumbers)
    
    #Concat all Strings for the log file
    finalFileName = fileNameNoNumbers.strip(' \t\n\r') + issueValue + yearValue
    g.write('\n' + fileNameNoNumbers + '/' + finalFileName + fileExtension)
    g.write('\n')
    
    #Move file
    #try:
    if(os.path.exists(fileNameNoNumbers + '/' + finalFileName + fileExtension)):
        g.write('\nFile already exist: ' + fileNameNoNumbers + '/' + finalFileName + fileExtension)
    else:
        shutil.move('comics_to_rename/' + fileNameNoExtension + fileExtension, 'final/' + fileNameNoNumbers + '/' + finalFileName + fileExtension)
    #except OSError, e:
    
#f.close()
g.close()