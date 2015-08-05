# Abide financial technical assessment - 28/07/15
# 1. How many surgeries in London.
# 2. Average cost of all peppermint oil prescriptions.
# 3. 5 Postcodes have the highest actual spend.
# 4. a) What was the average spend per capita for the country?
# 4. b) What is the range, and is there a location based difference?
#
import csv
from time import time


def surgery_reader():
    '''Function to read in surgery list csv and build the list
       and dictionary used later.'''

    
    #For easy testing purposes, have the file path as a variable.
    filestring = 'T201202ADD REXT.csv'
    #filestring = 'testsurg1.csv'
    
    surgery_list = []
    postcode_spend = {}
    
    with open(filestring) as csvfile:
        reader = csv.DictReader(csvfile, fieldnames =
                            ("List code","UID","Add1","Add2","Add3",
                             "City","County","Postcode"))
        for row in reader:
            surgery_list.append([row['UID'], row['Postcode']])
            #Append this postcode to the unique list if its, uh, unique.
            postcode_spend = unique_postcode_builder(postcode_spend, row['Postcode'])

    return (surgery_list,postcode_spend)


def get_london(postcode_list):
    '''Function to check if the incoming postcode is part of the London
    postcode area.'''
    
    #Set up the london counter.
    is_london = 0
    
    #Not particularly elegant, but a list of all inner and outer london postcodes.
    london_single = ['E','N','W']
    london_double = ['BR','CR','DA','EC','EN','GU','HA','IG','KT','NW',
                     'RM','SE','SL','SM','SW','TN','TW','UB','WC','WD']

    #Loop across unique postcode key and extract the london postcodes.
    for postcode in postcode_list:
        if(postcode[1][1].isnumeric() == True):
            for string in london_single:
                if(postcode[1].startswith(string) == True):
                    is_london += 1
        else:
            for string in london_double:
                if(postcode[1].startswith(string) == True):
                    is_london += 1
            
    return is_london


def unique_postcode_builder(postcode_dict, input_postcode):
    '''Function to check and add a postcode to the the spend list
       if it currently isn't there.'''
    
    #strip out trailing whitespace from postcode.
    input_postcode.rstrip()

    if((input_postcode in postcode_dict) == False):
        #Append new postcode to the list.
        postcode_dict.update({input_postcode:0.0})
                 
    return postcode_dict


def district_builder():
    '''Function to create a dictionary for postcode districts,
       and assign each the list of [population,spending].'''

    dist_dict = {}
    postal = ''
    prevpost = ''
    population = 0

    #Read and use census data.
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


def area_spending(district_spending):
    '''Function to extract the mean and range of spending per capita for
    a postal area. It also segregates postal areas into areas of England.'''

    tot_pop = 0
    tot_spend = 0
    av_mean = 0
    av_range = 0
    
    dataless_postcode = []

    #Holder for the area of the country a postcode is in.
    area = ''

    #Dictionary for splitting areas of the country.
    area_spend = {'North-West':[0.0, 0], 'North-East':[0.0, 0],
                  'West-Midlands':[0.0, 0], 'East-Midlands':[0.0, 0],
                  'South-West':[0.0, 0], 'South-East':[0.0, 0],
                  'London':[0.0, 0]}
    
    #Temporary list for sorting into ascending spend order.
    distlist = []

    #Remove Welsh areas LD and SY, as I'm only dealing with England for Q4.
    del district_spend['LD']
    del district_spend['SY']

    #Tidy up postcodes that are dataless to avoid DIV0 errors.
    for post_area, data in district_spend.items():
        if(data[1] == 0.0):
            dataless_postcode.append(post_area)
        else:
            #Assign to easy-to-use variables.
            pop = data[0]
            spend = data[1]

            #Increment average totals.
            tot_pop += pop
            tot_spend += spend

            #Append district list for range calculation.
            distlist.append([spend/pop,post_area])

            area = get_area(post_area)
            if(area != ''):
                templist = area_spend[area]
                templist[0] += spend
                templist[1] += pop
                area_spend[area] = templist

    #Remove dataless postcodes from the dictionary.
    for i in dataless_postcode:
            del district_spend[i]

    #Sort the list into ascending order by spend, for neatness.
    distlist.sort()

    av_mean = tot_spend/tot_pop
    av_range = distlist[len(distlist)-1][0] - distlist[0][0]


    return (av_mean, av_range, area_spend)


def get_area(postal):
    '''Function to determine and return a postcodes' area in the UK.'''

    area = ''

    northwest = ['BB', 'BD', 'BL', 'CA', 'CH', 'CW', 'HD', 'HX',
                 'L', 'LA', 'M', 'OL', 'PR', 'SK', 'WA', 'WN']
    northeast = ['DH', 'DL', 'DN', 'HG', 'HU', 'LS',
                 'NE', 'TS', 'S', 'WF', 'YO']
    westmids = ['B', 'CV', 'DE', 'DY', 'GL', 'HR', 'LE', 'MK',
                'NN', 'OX', 'ST', 'TF', 'WR', 'WS', 'WV']
    eastmids = ['AL', 'CB', 'CM', 'CO', 'IP', 'LN', 'LU',
                'NG', 'NR', 'PE', 'RM', 'SG', 'SS']
    london = ['BR', 'CR', 'DA', 'E', 'EC', 'EN', 'GU', 'HA', 'IG',
              'KT', 'N', 'NW', 'RM', 'SE', 'SL', 'SM', 'SW', 'TN',
              'TW', 'UB', 'W', 'WC','WD']
    southwest = ['BA', 'BH', 'BS', 'DT', 'EX', 'PL', 'SN'
                 'SP', 'TA', 'TQ', 'TR']
    southeast = ['BN', 'CT', 'GU', 'HP', 'ME', 'PO',
                 'RG', 'RH', 'SL', 'SO', 'TN']

    if((postal in northwest) == True):
        area = 'North-West'
    elif((postal in northeast) == True):
        area = 'North-East'
    elif((postal in westmids) == True):
        area = 'West-Midlands'
    elif((postal in eastmids) == True):
        area = 'East-Midlands'
    elif((postal in london) == True):
        area = 'London'
    elif((postal in southwest) == True):
        area = 'South-West'
    elif((postal in southeast) == True):
        area = 'South-East'

    return area


#MAIN. Start of the program flow.
print("Please ensure that CSV's are in the same directory as the .py file.")
input("Press Enter to continue.")

t0 = time()

london_counter = 0
total_units = 0
peppermint_cost = 0
cost = 0
average_spend = 0
range_spend = 0

postcode = ''
prev_id = ''
district = ''

surgery_list = []
unknown_id = []
templist = []

postcode_spend = {}
district_spend = district_builder()
area_spend = {}
    
print("Loading and analysing surgery file.")

#Populate Surgery-postcode list and spending dictionary.
surgery_list, postcode_spend = surgery_reader()

#Function for Q1.
london_counter = get_london(surgery_list)

print("Complete.")

#For testing purposes.
filestring = 'T201109PDP IEXT.csv'
#filestring = 'testledg1.csv'
    
print("Loading and analysing purchase ledgers, I'd pop the kettle on...")
with open(filestring) as csvfile:
    reader = csv.DictReader(csvfile)

    for row in reader:

        #Grab values for ease of use.
        cost = float(row['ACT COST   '])
        units = int(row['ITEMS  '])
        practice_id = row['PRACTICE']
        
        #Q2! Check the incoming for peppermint oil code.
        if(row['BNF CODE'] == '0102000T0'):
            total_units += units
            peppermint_cost += cost

        if(practice_id != prev_id):
            #Get the Practice ID's postcode from the list.
            postcode = postcode_finder(surgery_list, practice_id)
    
        if(postcode != ''):
            #Q3. If the postcode grab was successful, increment the spending.
            temp = postcode_spend[postcode] + cost
            postcode_spend[postcode] = temp

            #Q4. Builds the district spending dictionary.
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

#Q3. Extract the top 5 spending postcodes.
top_postcodes = extract_top(postcode_spend)

#Q4. Get the statistics from district spending.
average_spend, range_spend, area_spend = area_spending(district_spend)


print("Complete.\n")
print("Answers to questions can be found in /answers.txt.\n")


#Finally, output the answers to a text file.
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
    outfile.write("4. Average spend per capita: £%.2f\n" % (average_spend))
    outfile.write("   Range of spend per capita:£%.2f\n\n" % (range_spend))

    outfile.write("Spending per capita per area of the country below:\n")
    for area, data in area_spend.items():
        #Mainly for testing, but also the dict has keys hard assigned
        #which could stay as 0. No DIV0 errors here...
        if(data[1] != 0):
            outfile.write("%s - £%.2f\n" % (area, data[0]/data[1]))

        
if(len(unknown_id) != 0):
    print("Number of unknown Practice IDs:", len(unknown_id),
          "\nFull list output to unknownid.txt.")
    
    with open('unknownid.txt',mode='w') as outfile:
        for i in unknown_id:
            outfile.write(i+"\n")


#For tracking purpose, output time taken in seconds.
print("Time taken:", (time()-t0))
