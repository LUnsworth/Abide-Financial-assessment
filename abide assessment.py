# Abide financial technical assessment - 28/07/15
# 1. How many surgeries in London.
# 2. Average cost of all peppermint oil prescriptions.
# 3. 5 Postcodes have the highest actual spend.
# 4. a) What was the average spend per capita in each postcode district?
# 4. b) Is there an appreciable difference between the N/E/S/W of England?
#
import csv
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
    #IMPROVE THIS WITH STRING SLICING.
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
        if(len(topfive) < 5):
            topfive.append([spend, postcode])
        else:
            #Iterate over each postcode, placing each new one in position 6
            #sorting the list afterwards. That way the top 5 is always preserved.
            topfive.append([spend, postcode])

            #Sort the list in descending order.
            topfive.sort(reverse=True)                

            #Clear out the 6th position used in the sorting method.
            topfive.pop()
        
    return topfive

#MAIN. Start of the program flow.
print("Please ensure that CSV's are in the same directory as the .py file.")
input("Press Enter to continue.")
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

total_units = 0
cost = 0
postcode = ''
unknown_id = []
temp = 0
previd = ''
prevpost = ''

inp = input("1 for full, 2 for test:")
if(inp == '1'):
    filestring = 'T201109PDP IEXT.csv'
else:
    filestring = 'testledg1.csv'
    
print("Loading and analysing purchase ledgers, I'd pop the kettle on...")
with open(filestring) as csvfile:
    reader = csv.DictReader(csvfile)

    for row in reader:
        #Check the incoming for peppermint oil code.
        if(row['BNF CODE'] == '0102000T0'):
            total_units += int(row['ITEMS  '])
            cost += (float(row['ACT COST   ']))

        if(row['PRACTICE'] != previd):
            #Get the Practice ID's postcode from the list.
            postcode = postcode_finder(surgery_list, row['PRACTICE'])
    
        if(postcode != ''):
            #If the postcode grab was successful, increment the spending.
            temp = postcode_spend[postcode] + float(row['ACT COST   '])
            postcode_spend[postcode] = temp
        else:
            #Otherwise keep track of unknown practice IDs.
            if((row['PRACTICE'] in unknown_id) == False):
                unknown_id.append(row['PRACTICE'])

        #Set current Practice ID for the next pass.
        previd = row['PRACTICE']
        prevpost = postcode

top_postcodes = []
#Extract the top 5 spending postcodes.
top_postcodes = extract_top(postcode_spend)

print("Complete.\n")
print("Answers to questions can be found in /answers.txt.\n")

with open('answers.txt',mode='w') as outfile:
    #Answer to Q1 output.
    outfile.write("1. Surgeries in London: %d\n" % london_counter)

    #Answer to Q2 output.
    outfile.write("2. Average actual cost of peppermint oil prescriptions: £%.2f\n"
                  % (cost/total_units))

    #Answer to Q3 output, with bonus information.
    outfile.write("3. Top 5 spending postcodes:\n")
    for i in top_postcodes:
        outfile.write("%s with a spend of £%.2f\n" % (i[1],i[0]))

    #Answer to Q4 output.
    #blahblahblah.


if(len(unknown_id) != 0):
    print("Number of unknown Practice IDs:", len(unknown_id),
          "\nFull list output to unknownid.txt.")
    
    outfile = open('unknownid.txt',mode='w',)
    for i in unknown_id:
        outfile.write(i+"\n")
    outfile.close()
'''
replist.sort()
print("Average repeat:", (sum(replist) / len(replist)))
print("Range:", (replist[len(replist)-1] - replist[0]))
'''

#For tracking purpose, output time taken in decimal hours.
print("Time taken:", (time()-t0))#/3600)
