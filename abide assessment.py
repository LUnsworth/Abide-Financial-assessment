# Abide financial technical assessment - 28/07/15
# 1. How many surgeries in London.
# 2. Average cost of all peppermint oil prescriptions.
# 3. 5 Postcodes have the highest actual spend.
# 4. a) What was the average spend per capita for the country?
# 4. b) What is the range, and is there a location based difference?
#
import csv
from time import time

def get_london(postcode_input):
    '''Function to check if the incoming postcode is part of the London postcode area.
    '''
    #Assumed that postcode is not in London. This value is added to counter in main.
    is_london = 0
    #Not particularly elegant, but a list of all inner and outer london postcodes.
    london_single = ['E','N','W']
    london_double = ['BR','CR','DA','EC','EN','GU','HA','IG','KT','NW',
                     'RM','SE','SL','SM','SW','TN','TW','UB','WC','WD']
    
    if(postcode_input[1].isnumeric() == True):
        for string in london_single:
            if(postcode_input.startswith(string) == True):
                is_london = 1
    else:
        for string in london_double:
            if(postcode_input.startswith(string) == True):
                is_london = 1
            
    return is_london


def unique_postcode_builder(postcode_list, input_postcode):
    '''Function to check and add a postcode to the the spend list
       if it currently isn't there.'''
    
    #strip out trailing whitespace from postcode.
    input_postcode.rstrip()

    if((input_postcode in postcode_list) == False):
        #Append new postcode to the list.
        postcode_list.update({input_postcode:0.0})
                 
    return postcode_list


def district_builder():
    '''Function to create a dictionary for postcode districts,
       and assign each the list of [population,spending].'''

    dist_dict = {}
    postal = ''
    prevpost = ''
    population = 0
    
    with open('2011census.csv') as csvfile:
        reader = csv.DictReader(csvfile)
        
        for row in reader:
            postal = district_grabber(row['Postcode District'])

            if(postal == prevpost):
                #Sum populations of postal districts e.g. AL1, AL2, AL3
                population += int(row['All usual residents'])
            elif(prevpost == ''):
                #Catches the very first row from being added to dict.
                population += int(row['All usual residents'])
            else:
                #If it's a new postcode, write the previous record.
                dist_dict[prevpost] = [population, 0.0]
                #Set population to new entry.
                population = int(row['All usual residents'])

            #Set previous field for next pass.
            prevpost = postal

    #Last entry will be missed from above, so attach it here.
    dist_dict[prevpost] = [population, 0.0]
    
    return dist_dict

def district_grabber(input_postcode):
    '''Strips postcode district from full postcode'''

    output_postcode = ''
    
    if(input_postcode[1].isnumeric() == True):
       output_postcode = input_postcode[:1]
    else:
       output_postcode = input_postcode[:2]

    return output_postcode
       
    
def postcode_finder(surgery_list, practice_code):
    '''Finds postcode from Practice code in ledger csv'''
    
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
district_spend = district_builder()
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
peppermint_cost = 0
cost = 0
postcode = ''
unknown_id = []
dataless_postcode = {}
temp = 0
prev_id = ''
district = ''
templist = []

inp = input("1 for full, 2 for test:")
if(inp == '1'):
    filestring = 'T201109PDP IEXT.csv'
else:
    filestring = 'testledg1.csv'
    
print("Loading and analysing purchase ledgers, I'd pop the kettle on...")
with open(filestring) as csvfile:
    reader = csv.DictReader(csvfile)

    for row in reader:

        #Grab values for ease of use.
        cost = float(row['ACT COST   '])
        units = int(row['ITEMS  '])
        practice_id = row['PRACTICE']
        
        #Check the incoming for peppermint oil code.
        if(row['BNF CODE'] == '0102000T0'):
            total_units += units
            peppermint_cost += cost

        if(practice_id != prev_id):
            #Get the Practice ID's postcode from the list.
            postcode = postcode_finder(surgery_list, practice_id)
    
        if(postcode != ''):
            #If the postcode grab was successful, increment the spending.
            temp = postcode_spend[postcode] + cost
            postcode_spend[postcode] = temp

            district = district_grabber(postcode)
            templist = district_spend[district]
            templist[1] += cost
            district_spend[district] = templist

        else:
            #Otherwise keep track of unknown practice IDs.
            if((practice_id in unknown_id) == False):
                unknown_id.append(practice_id)

        #Set current Practice ID for the next pass.
        prev_id = practice_id

top_postcodes = []
#Extract the top 5 spending postcodes.
top_postcodes = extract_top(postcode_spend)
tot_pop = 0
tot_spend = 0
distlist = []

#Tidy up postcodes that are dataless to avoid DIV0 errors.
for i, j in district_spend.items():
    if(j[1] == 0.0):
        dataless_postcode[i] = j
    else:
        tot_pop += j[0]
        tot_spend += j[1]
        distlist.append([j[1]/j[0],i])
        
for i in dataless_postcode.keys():
        del district_spend[i]

distlist.sort()

print("Complete.\n")
print("Answers to questions can be found in /answers.txt.\n")

with open('answers.txt',mode='w') as outfile:
    #Answer to Q1 output.
    outfile.write("1. Surgeries in London: %d\n" % london_counter)

    #Answer to Q2 output.
    outfile.write("2. Average actual cost of peppermint oil prescriptions: £%.2f\n"
                  % (peppermint_cost/total_units))

    #Answer to Q3 output, with bonus information.
    outfile.write("3. Top 5 spending postcodes:\n")
    for i in top_postcodes:
        outfile.write("%s with a spend of £%.2f\n" % (i[1],i[0]))

    #Answer to Q4 output.
    outfile.write("4. Average spend per capita: £%.2f\n" % (tot_spend/tot_pop))
    outfile.write("Range of spend per capita:£%.2f\n\n" %
                  (distlist[len(distlist)-1][0] - distlist[0][0]))
    for i in distlist:
        outfile.write("%s - £%.2f\n" % (i[1],i[0]))
        
if(len(unknown_id) != 0):
    print("Number of unknown Practice IDs:", len(unknown_id),
          "\nFull list output to unknownid.txt.")
    
    outfile = open('unknownid.txt',mode='w',)
    for i in unknown_id:
        outfile.write(i+"\n")
    outfile.close()


#For tracking purpose, output time taken in decimal hours.
print("Time taken:", (time()-t0))#/3600)
