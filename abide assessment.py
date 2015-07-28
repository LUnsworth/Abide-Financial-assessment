# Abide financial technical assessment - 28/07/15
#
#
import csv
import re

def get_london(postcode_input):
    '''Function to check if the incoming postcode is part of the London postcode area.
    '''
    #Assumed that postcode is not in London. This value is added to counter in main.
    is_london = 0
    #Disgusting way of doing it until regex's get sorted.
    london_single = ['E0','E1','E2','E3','E4','E5','E6','E7','E8','E9',
                     'N0','N1','N2','N3','N4','N5','N6','N7','N8','N9',
                     'W0','W1','W2','W3','W4','W5','W6','W7','W8','W9',]
    #The easy one...
    london_double = ['EC','NW','SE','SW','WC']
    
    for string in london_single:
        if(postcode_input.startswith(string) == True):
            is_london = 1
    for string in london_double:
        if(postcode_input.startswith(string) == True):
            is_london = 1
            
    return is_london


print("Please ensure that CSV's are in the same directory as the .py file.")
input("Press any key to continue.")

london_counter = 0
surgery_list = []
#For easy testing purposes, have the file path as a variable.
filestring = 'T201202ADD REXT.csv'
#filestring = 'testsurg1.csv'

with open(filestring) as csvfile:
    reader = csv.DictReader(csvfile, fieldnames = ("List code","UID","Add1","Add2","Add3","City","County","Postcode"))
    for row in reader:
        surgery_list.append([row['UID'], row['Postcode']])
        london_counter += get_london(row['Postcode'])

#print("Surgery details: " + str(surgery_list))
print(london_counter)

