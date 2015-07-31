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
    #Not particularly elegant, but a list of all inner and outer london postcodes.
    london_postcodes = ['BR','CR','DA','E0','E1','E2','E3','E4','E5',
                        'E6','E7','E8','E9','EC','EN','GU','HA','IG',
                        'KT','N0','N1','N2','N3','N4','N5','N6','N7',
                        'N8','N9','NW','RM','SE','SL','SM','SW','TN',
                        'TW','UB','W0','W1','W2','W3','W4','W5','W6',
                        'W7','W8','W9','WC','WD']
    
    for string in london_postcodes:
        if(postcode_input.startswith(string) == True):
            is_london = 1
            
    return is_london


def unique_postcode_builder(postcode_list, input_postcode):

    #strip out trailing whitespace from postcode.
    input_postcode.rstrip()

    if((input_postcode in postcode_list) == False):
        #Append new postcode to the list.
        postcode_list.update({input_postcode:0.0})
                 
    return postcode_list


def postcode_finder(surgery_list, practice_code):
    '''Finds postcode from Practice code from ledger csv'''
    postcode = ''
    for i in range(0,len(surgery_list)):
        if(practice_code == surgery_list[i][0]):
            postcode = surgery_list[i][1]

    return postcode


def extract_top(spend_list):
    '''Extracts top 5 spend postcodes and returns them in a list.'''
    topfive = []
    for postcode, spend in spend_list.items():
        if(len(topfive) < 6):
            topfive.append([spend, postcode])
        else:
            #Iterate over each postcode, placing each new one in position 6
            #sorting the list afterwards. That way the top 5 is always preserved.
            topfive[5] = [spend, postcode]

        topfive.sort(reverse=True)                

    return topfive

#MAIN. Start of the program flow.
print("Please ensure that CSV's are in the same directory as the .py file.")
input("Press any key to continue.")
t0 = time()
london_counter = 0
surgery_list = []
postcode_spend = {}
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

        #Get the Practice IDs postcode from the list.
        postcode = postcode_finder(surgery_list, row['PRACTICE'])
    
        if(postcode != ''):
            #If the postcode grab was successful, increment the spending.
            temp = postcode_spend[postcode] + float(row['ACT COST   '])
            postcode_spend[postcode] = temp
        else:
            #Otherwise keep track of unknown practice IDs.
            unknown_id += 1

top_postcodes = []
#Extract the top 5 spending postcodes.
top_postcodes = extract_top(postcode_spend)

print("Complete.")
print("Number of peppermint prescriptions: ", total_units,
      " Total cost: £%.2f Average unit cost: £%.2f"% (cost, (cost/total_units)))
print("Number of unknown Practice IDs:", unknown_id)
print("Top 5 spending postcodes")
for i in range(0,len(top_postcodes) - 1):
    print(top_postcodes[i][1],"with a spend of £%.2f" % (top_postcodes[i][0]))
print("Time taken:", time()-t0)
