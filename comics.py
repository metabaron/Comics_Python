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

#Log file
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
#[ ]([0-9]+).* Numbers
numbers = re.compile('[ ]([0-9]+).')
#(19[0-9]{2}|20[0-9]{2}) Year
years = re.compile('(19[0-9]{2}|20[0-9]{2})')
#^0+ Leading 0s
zeros = re.compile('^0+')
#(\d+)(?!.*\d) last numbers
afterNumbers = re.compile('(\d+)(?!.*\d)')
#[ ]{2,} multiple spaces characters
multipleSpaces = re.compile('[ ]{2,}')
#[01][0-9][ -/.][01][0-9][ -/.][01][0-9] find date
dateRemove = re.compile('[01][0-9][ -/.][01][0-9][ -/.][01][0-9]')

#Directory to store all errors
try:
    os.makedirs('final/errors')
except OSError, e:
    if e.errno != errno.EEXIST:
        raise
    else:
        g.write('\nDirectory already exist: final/errors\n')
    
#For each file
#for line in f:
dirList=os.listdir('comics_to_rename/')
for line in dirList:
    yearValue = ''
    issueValue = ''
    
    #Remove extension
    fileNameNoExtension, fileExtension = os.path.splitext(line.strip(' \t\n\r'))
    #Remove first set of parentheses if the line start with them
    lineNoStartParentheses = lineStartParentheses.sub('', fileNameNoExtension.strip(' \t\n\r'))
    g.write('\nInitial filename: ' + lineNoStartParentheses)
    #Replace underscores by spaces
    noUnderscores = underscores.sub(' ', lineNoStartParentheses.strip(' \t\n\r'))
    
    #Search for year between parenthesis
    year = yearBetweenParenthesis.search(noUnderscores)
    if year:
        yearValue = ' - Year ' + year.group(1)
    
    #Remove all parenthesis
    fileNameNoParenthesis = parenthesis.sub('', noUnderscores).strip(' \t\n\r')
    
    #if we cannot find the year, maybe it's not within parenthesis?
    year = years.search(fileNameNoParenthesis)
    if year:
        yearValue = ' - Year ' + year.group(1)
        
    #Remove year
    fileNameNoParenthesis = dateRemove.sub('', years.sub('', fileNameNoParenthesis).strip(' \t\n\r'))
    g.write('\nJust filename: ' + fileNameNoParenthesis)
    
    #Search for issue numbers
    #And remove leading 0s. Once done, check format so that
    # 1 ==> 001, 10 ==> 010 and 100 ==> 100
    issue = afterNumbers.search(fileNameNoParenthesis)
    if issue:
        issueValue = ' - Issue ' + zeros.sub('', issue.group(0)).zfill(3) 
        g.write('\nCleaned issue number: ' + issueValue + ' and year: ' + yearValue)
    
    #Remove numbers
    fileNameNoNumbers = multipleSpaces.sub(' ', afterNumbers.sub('', fileNameNoParenthesis).strip(' \t\n\r'))
    
    #Create directories
    try:
        os.makedirs('final/' + fileNameNoNumbers)
        g.write('\nDirectory created: ' + fileNameNoNumbers)
    except OSError, e:
        g.write('\nDirectory already exist: final/' + fileNameNoNumbers)
    
    #Concat all Strings for the log file
    finalFileName = fileNameNoNumbers.strip(' \t\n\r') + issueValue + yearValue
    g.write('\n' + fileNameNoNumbers + '/' + finalFileName + fileExtension)
    g.write('\n')
    
    #Move file
    if(os.path.exists(fileNameNoNumbers + '/' + finalFileName + fileExtension)):
        g.write('\nFile already exist: ' + fileNameNoNumbers + '/' + finalFileName + fileExtension)
    else:
        shutil.move('comics_to_rename/' + fileNameNoExtension + fileExtension, 'final/' + fileNameNoNumbers + '/' + finalFileName + fileExtension)
    
g.close()