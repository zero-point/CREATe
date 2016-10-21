import time
import os
import io
import requests
from bs4 import BeautifulSoup
import re

print "This script was started " + time.ctime()

ProgressCounter = 1

dir = ".\parse"
dir_input = dir + "\Input"
dir_output = dir + "\Output"
InputDataName = 'http://www.moddb.com/'
OutputDataName = "OutputResults.txt"

os.chdir(dir_input)
RawInputs = io.open(InputDataName, 'r', encoding='utf-8').read().splitlines()

TotalCount = len(RawInputs)
print RawInputs

break
os.chdir(dir_output)

with open(OutputDataName, 'w') as TargetData:
    TargetData.write("ID\tURL\tWikipediaHeaders\n")


for RawInput in RawInputs:
    print "We are at number " + str(ProgressCounter) + " of " + str(TotalCount) + "!"
    
    TotalInfoperEntry = RawInput.split('#')
    ID, URL = TotalInfoperEntry[0:2]
    
    with open(OutputDataName, 'a') as TargetData:
        TargetData.write(ID.encode('utf-8') + '\t')
        TargetData.write(URL.encode('utf-8') + '\t')
    r = requests.get(URL)
    r.encode = "utf-8"
    html_raw = r.text
    SourceCode = BeautifulSoup(html_raw)
    
    for entry in SourceCode.find_all('h1', {'id':'firstHeading'}):
        with open(OutputDataName, 'a') as TargetData:
            TargetData.write(entry.getText().encode('utf-8'))

    ProgressCounter = int(ProgressCounter) + 1
    with open(OutputDataName, 'a') as TargetData:
        TargetData.write('\n')

