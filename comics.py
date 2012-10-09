#^([^"]+)" to replace all before the first "
#[^"a]*$ to replace everything after the last "

#Let's retrieve the filename passed as argument
#!/usr/bin/python

#importing regular expression
import re, os, errno, shutil


#print 'Number of arguments:', len(sys.argv), 'arguments.'
#print 'Argument List:', str(sys.argv)
#filename = sys.argv[1]
#print 'Filename:', str(filename)
#print 'Filename without extension:', filename.split('.', 1)[0]


#
#DEAL WITH MULTIPLE SAME NAME
#

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
#(0[1-9]|1[012])[ -/.](0[1-9]|[12][0-9]|3[01])[ -/.](0[0-9]|1[0-9]) find date
dateRemove = re.compile('(0[1-9]|1[012])[ -/.](0[1-9]|[12][0-9]|3[01])[ -/.](0[0-9]|1[0-9])')
#remove 'v' at end of file's name for 'volume'
volumeVersion = re.compile('[ ]v$')

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
    g.write('\nInitial filename: ' + line)
    #Remove first set of parentheses if the line start with them
    lineNoStartParentheses = lineStartParentheses.sub('', fileNameNoExtension.strip(' \t\n\r'))
    g.write('\nInitial filename: ' + lineNoStartParentheses)
    #Replace underscores by spaces
    noUnderscores = underscores.sub(' ', lineNoStartParentheses.strip(' \t\n\r'))
    g.write('\nnoUnderscores filename: ' + noUnderscores)
    
    #Search for year between parenthesis
    year = yearBetweenParenthesis.search(noUnderscores)
    if year:
        yearValue = ' - Year ' + year.group(1)
        g.write('\nyear filename: ' + yearValue)
    
    #Remove all parenthesis
    fileNameNoParenthesis = parenthesis.sub('', noUnderscores).strip(' \t\n\r')
    g.write('\nfileNameNoParenthesis filename: ' + fileNameNoParenthesis)
    
    #if we cannot find the year, maybe it's not within parenthesis?
    year = years.search(fileNameNoParenthesis)
    if year:
        yearValue = ' - Year ' + year.group(1)
        g.write('\nyear filename: ' + yearValue)
        
    #Remove year
    fileNameNoParenthesis = dateRemove.sub('', years.sub('', fileNameNoParenthesis).strip(' \t\n\r'))
    g.write('\nfileNameNoParenthesis filename: ' + fileNameNoParenthesis)
    
    #Search for issue numbers
    #And remove leading 0s. Once done, check format so that
    # 1 ==> 001, 10 ==> 010 and 100 ==> 100
    issue = afterNumbers.search(fileNameNoParenthesis)
    if issue:
        issueValue = ' - Issue ' + zeros.sub('', issue.group(0)).zfill(3) 
        #g.write('\nCleaned issue number: ' + issueValue + ' and year: ' + yearValue)
        g.write('\nissueValue filename: ' + issueValue)
    
    #Remove numbers
    fileNameNoNumbers = multipleSpaces.sub(' ', afterNumbers.sub('', fileNameNoParenthesis).strip(' \t\n\r'))
    g.write('\nfileNameNoNumbers filename: ' + fileNameNoNumbers)
    
    #Clean filename
    fileNameFinal1 = fileNameNoNumbers.replace('Digital Zone Empire', '').strip(' \t\n\r')
    fileNameFinal2 = fileNameFinal1.replace('by Nook', '').strip(' \t\n\r')
    fileNameFinal3 = fileNameFinal2.replace('Minutemen DTs', '').strip(' \t\n\r')
    fileNameFinal4 = fileNameFinal2.replace('digital Empire', '').strip(' \t\n\r')
    fileNameFinal = fileNameFinal2.replace('Minutemen-DTs', '').strip(' \t\n\r')
    
    #Create directories
    try:
        os.makedirs('final/' + fileNameFinal)
        g.write('\nDirectory created: ' + fileNameFinal)
    except OSError, e:
        g.write('\nDirectory already exists: final/' + fileNameFinal)
    
    #Concat all Strings for the log file
    finalFileName = fileNameFinal.strip(' \t\n\r') + issueValue + yearValue
    g.write('\n' + fileNameFinal + '/' + finalFileName + fileExtension)
    g.write('\n')
    
    #Move file
    if(os.path.exists(fileNameFinal + '/' + finalFileName + fileExtension)):
        g.write('\nFile already exists: ' + fileNameFinal + '/' + finalFileName + fileExtension)
    else:
        #g.write('comics_to_rename/' + fileNameNoExtension + fileExtension + ' AND ' + 'final/' + fileNameFinal + '/' + finalFileName + fileExtension)
        shutil.move('comics_to_rename/' + fileNameNoExtension + fileExtension, 'final/' + fileNameFinal + '/' + finalFileName + fileExtension)
    
g.close()