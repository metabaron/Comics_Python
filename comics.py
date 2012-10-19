#!/usr/bin/python

#importing regular expression
import re, os, errno, shutil, sys, getopt


#print 'Number of arguments:', len(sys.argv), 'arguments.'
#print 'Argument List:', str(sys.argv)
#filename = sys.argv[0]

dryRun = False
helpInfo = True
sourceDirectory = 'comics_to_rename'

#options, remainder = getopt.getopt(sys.argv[1:], 'd:', ['dry-run='])
options, remainder = getopt.getopt(sys.argv[1:], 'dh', ['dry-run', 'help'])
#print 'OPTIONS   :', options
#print 'REMAINDER :', remainder

if len(remainder) > 0:
    sourceDirectory = remainder[0]
    helpInfo = False

for opt, arg in options:
    if opt in ('-d', '--dry-run'):
        dryRun = True
    if opt in ('-h', '--help'):
        helpInfo = True

if helpInfo == True:
    print ''
    print 'Rename and move your comics to directory \'final\''
    print 'Will create one sub directory by serie'
    print ''
    print 'Coded by Metabaron'
    print ''
    print 'Usage: python comics.py [-d | -h] source'
    print 'Will read files from \'source\', rename and move them to \'final\''
    print 'Per default, source directory is \'comics_to_rename\''
    print ''
    print '-h\t--help   \tThis help screen'
    print '-d\t--dry-run\tDry run. Same as normal run but no delete'
    sys.exit()
        
#sys.exit()

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
##(19[0-9]{2}|20[0-9]{2}) Year
#years = re.compile('19[0-9]{2}|20[0-9]{2}')
#(19[0-9]{2}|20[0-9]{2})([-.]\d\d)?([-.]\d\d)? Year
years = re.compile('(19[0-9]{2}|20[0-9]{2})([-.]\d\d)?([-.]\d\d)?')
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
#[\d]*[ ]of[ ][\d]* look for 'xx of xx' in filename
xxOfxx  = re.compile('[\d]+[ ]of[ ][\d]+')
#v[\d]+ c[\d]+ looking for 'cxx' kind of issue version
cxx = re.compile('v[\d]+ c[\d]+')
# '#|v\d+!$|\.| v | - $' Deal with version issues linked to filename
extra = re.compile('#|v\d+!$|\.| v | - $')
#[ ][\d]+-[\d]+($| ) multiple episodes in one file
multipleEpisode = re.compile('[ ][\d]+-[\d]+($| )')
#(\d+) (of|Of|OF) extract first xx of 'xx of xx'
firstXxOf = re.compile('(\d+) (of|Of|OF)')
#\d+ extract numbers
numbersExtract = re.compile('\d+')


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
dirList=os.listdir(sourceDirectory)
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
    
    g.write('\nfileNameNoParenthesis no year filename: ' + fileNameNoParenthesis)
    #Search for issue numbers
    #And remove leading 0s. Once done, check format so that
    # 1 ==> 001, 10 ==> 010 and 100 ==> 100
    issue = multipleEpisode.search(fileNameNoParenthesis)
    fileNameNoNumbers = fileNameNoParenthesis
    if issue != None:
        g.write('\nMultiple episodes?:' + issue.group(0).strip(' '))
        issueValue = ' - Issue ' + zeros.sub('', issue.group(0).strip(' '))
        #fileNameNoNumbers = multipleSpaces.sub(' ', xxOfxx.sub('', cxx.sub('', extra.sub('', multipleEpisode.sub('', fileNameNoParenthesis)))).strip(' \t\n\r'))
        fileNameNoNumbers = multipleSpaces.sub(' ', cxx.sub('', extra.sub('', multipleEpisode.sub('', xxOfxx.sub('', fileNameNoParenthesis)))).strip(' \t\n\r'))
        g.write('\nfileNameNoNumbers filename: ' + fileNameNoNumbers)
    else:
        if xxOfxx.search(fileNameNoNumbers) != None:
            #If we are in 'xx of xx' we extract it and extract issue number from it
            xOFx = firstXxOf.search(fileNameNoNumbers).group(0)
            issueValue = ' - Issue ' + zeros.sub('', numbersExtract.search(xOFx).group(0)).zfill(3)
            g.write('\nissueValue filename: ' + issueValue)
            fileNameNoNumbers = multipleSpaces.sub(' ', cxx.sub('', extra.sub('', afterNumbers.sub('', xxOfxx.sub('', fileNameNoParenthesis)))).strip(' \t\n\r'))
        else:
            issue = afterNumbers.search(fileNameNoParenthesis)
            if issue:
                issueValue = ' - Issue ' + zeros.sub('', issue.group(0)).zfill(3)
                g.write('\nissueValue filename: ' + issueValue)
                #fileNameNoNumbers = multipleSpaces.sub(' ', xxOfxx.sub('', cxx.sub('', extra.sub('', afterNumbers.sub('', fileNameNoParenthesis)))).strip(' \t\n\r'))
                fileNameNoNumbers = multipleSpaces.sub(' ', cxx.sub('', extra.sub('', afterNumbers.sub('', xxOfxx.sub('', fileNameNoParenthesis)))).strip(' \t\n\r'))
                g.write('\nfileNameNoNumbers filename: ' + fileNameNoNumbers)
    #Remove numbers
    #fileNameNoNumbers = multipleSpaces.sub(' ', afterNumbers.sub('', xxOfxx.sub('', cxx.sub('', extra.sub('', fileNameNoParenthesis)))).strip(' \t\n\r'))
    ##fileNameNoNumbers = multipleSpaces.sub(' ', xxOfxx.sub('', cxx.sub('', extra.sub('', afterNumbers.sub('', fileNameNoParenthesis)))).strip(' \t\n\r'))
    #g.write('\n' + afterNumbers.sub('', fileNameNoParenthesis))
    #g.write('\n' + extra.sub('', afterNumbers.sub('', fileNameNoParenthesis)))
    #g.write('\n' + cxx.sub('', extra.sub('', afterNumbers.sub('', fileNameNoParenthesis))))
    #g.write('\n' + multipleSpaces.sub(' ', xxOfxx.sub('', cxx.sub('', extra.sub('', afterNumbers.sub('', fileNameNoParenthesis))))))
    #g.write('\nfileNameNoNumbers filename: ' + fileNameNoNumbers)
    
    #Clean filename of release teams
    #Dirty - case sensitive - but would do the trick (we can use "compile" as previously in this file)
    fileNameFinal1 = fileNameNoNumbers.replace('Digital Zone Empire', '').strip(' \t\n\r')
    fileNameFinal2 = fileNameFinal1.replace('by Nook', '').strip(' \t\n\r')
    fileNameFinal3 = fileNameFinal2.replace('Minutemen DTs', '').strip(' \t\n\r')
    fileNameFinal4 = fileNameFinal3.replace('digital Empire', '').strip(' \t\n\r')
    fileNameFinal = fileNameFinal4.replace('Minutemen-DTs', '').strip(' \t\n\r')
    fileNameFinal = multipleSpaces.sub(' ', fileNameFinal).strip(' \t\n\r')
    
    #Create directories
    try:
        os.makedirs('final/' + fileNameFinal)
        g.write('\nDirectory created: ' + fileNameFinal)
    except OSError, e:
        g.write('\nDirectory already exists: final/' + fileNameFinal)
    
    #Concat all Strings for the log file
    #finalFileName = multipleSpaces.sub(' ', fileNameFinal).strip(' \t\n\r') + issueValue + yearValue
    finalFileName = fileNameFinal.strip(' \t\n\r') + issueValue + yearValue
    g.write('\n' + fileNameFinal + '/' + finalFileName + fileExtension)
    
    #Move file with correct name
    fileNameFinalVerification = finalFileName
    loop = 1
    while(os.path.isfile('final/' + fileNameFinal + '/' + fileNameFinalVerification + fileExtension)):
        g.write('\nFile already exists: ' + fileNameFinal + '/' + fileNameFinalVerification + fileExtension)
        fileNameFinalVerification = finalFileName + ' - Copy ' + str(loop)
        loop += 1
    if dryRun == False:
        shutil.move(sourceDirectory + '/' + fileNameNoExtension + fileExtension, 'final/' + fileNameFinal + '/' + fileNameFinalVerification + fileExtension)
    else:
        file = open('final/' + fileNameFinal + '/' + fileNameFinalVerification + fileExtension, 'w')
        file.write('')
        file.close()
    g.write('\n')
g.close()