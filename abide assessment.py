# Abide financial technical assessment - 28/07/15
# 1. How many surgeries in London.
# 2. Average cost of all peppermint oil prescriptions.
# 3. 5 Postcodes have the highest actual spend.
# 4. Make it up. Possibly look at cost of diabetes treatment.
#
import csv
import re
from time import time

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


def unique_postcode_builder(postcode_list, input_postcode):

    inlist = False
    #strip out trailing whitespace from postcode.
    input_postcode.rstrip()

    for i in postcode_list:
        if(input_postcode == i[1]):
            #Set flag indicating the postcode is already in the list.
            inlist = True

    if(inlist == False):
        #Append new postcode to the list.
        #postcode_list.update({input_postcode:0.0})
        postcode_list.append([0.0, input_postcode])
                 
    return postcode_list


def postcode_finder(surgery_list, practice_code):
    '''Finds postcode from Practice code from ledger csv'''
    postcode = ''
    for i in range(0,len(surgery_list)):
        if(practice_code == surgery_list[i][0]):
            postcode = surgery_list[i][1]

    return postcode


def get_spend(postcode_list, postcode):
    '''Retrieves current spending total for a postcode'''
    current_spend = 0.0
    for i in postcode_list:
        if(postcode == i[1]):
            current_spend = i[0]

    return current_spend


def update_spend(postcode_list, spend, postcode):
    '''Updates the spend of a postcode'''

    for i in postcode_list:
        if(postcode == i[1]):
            i[0] = spend

    return postcode_list


def extract_top(spend_list):
    '''Extracts top 5 spend postcodes and returns them in a list.'''
    topfive = []
    for i in spend_list:
        if(len(topfive) < 6):
            topfive.append(i)

        else:
            #Iterate over each postcode, placing each new one in position 6
            #sorting the list afterwards. That way the top 5 is always preserved.
            topfive[5] = i

        topfive.sort(reverse=True)                

    return topfive

#MAIN. Start of the program flow.
print("Please ensure that CSV's are in the same directory as the .py file.")
input("Press any key to continue.")
t0 = time()
#Loading surgery list and pulling the number of 
london_counter = 0
surgery_list = []
#postcode_spend = {}
postcode_spend = []
inp = ''

#For easy testing purposes, have the file path as a variable.
inp = input("1 for full, 2 for test:")
if(inp == '1'):
    filestring = 'T201202ADD REXT.csv'
else:
    filestring = 'testsurg1.csv'
    
print("Loading and analysing surgery file.")
with open(filestring) as csvfile:
    reader = csv.DictReader(csvfile, fieldnames = ("List code","UID","Add1","Add2"
                                                   ,"Add3","City","County","Postcode"))
    for row in reader:
        surgery_list.append([row['UID'], row['Postcode']])
        london_counter += get_london(row['Postcode'])
        #Append this postcode to the unique list if its, uh, unique.
        postcode_spend = unique_postcode_builder(postcode_spend, row['Postcode'])

print("Complete.")
print("Surgeries in London: ", london_counter)

total_units = 0
cost = 0
postcode = ''
unknown_id = 0
temp = 0

inp = input("1 for full, 2 for test:")
if(inp == '1'):
    filestring = 'T201109PDP IEXT.csv'
else:
    filestring = 'testledg1.csv'
    
print("Loading and analysing purchase ledgers.")
with open(filestring) as csvfile:
    reader = csv.DictReader(csvfile)

    for row in reader:
        #Check the incoming for peppermint oil code.
        if(row['BNF CODE'] == '0102000T0'):
            total_units += int(row['ITEMS  '])
            cost += (float(row['ACT COST   ']))
        postcode = postcode_finder(surgery_list, row['PRACTICE'])
        if(postcode != ''):
            temp = get_spend(postcode_spend, postcode) + float(row['ACT COST   '])
            postcode_spend = update_spend(postcode_spend, temp, postcode)
        else:
            unknown_id += 1

top_postcodes = []
top_postcodes = extract_top(postcode_spend)

print("Complete.")
print("Number of peppermint prescriptions: ", total_units,
      " Total cost: £%.2f Average unit cost: £%.2f"% (cost, (cost/total_units)))
print("Number of unknown Practice IDs:", unknown_id)
print("Top 5 spending postcodes")
for i in range(0,len(top_postcodes) - 1):
    print(top_postcodes[i][1],"with a spend of £%.2f" % (top_postcodes[i][0]))
print("Time taken:", time()-t0)
