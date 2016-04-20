'''
This script calculates the enrollment differences between the current semester and the semester 
last year and generates a spreadsheet that aggregates this data by major, school, and count type. 
The script is currently static, meaning it only compares the current date to last years, 
rather than all dates in the registration period.

The input spread sheet needs to be named 'baruch_school_data.csv` and requires the following columns:

    STRM (a code denoting the year registration)
    MAJORSCHOOLS (school attended by student)
    ACAD_CAREER (grad or undergrad)
    UNT_BILLING (credit hours)
    MAJOR1 (student's major)
    FILEDATE (date the data was obtained)

The output is a csv file with the following columns:

    Date
    School
    Count
    Academic_Level
    Major
    2014
    2015
    Diffs
'''
import pandas as pd
import numpy as np
from datetime import date, datetime, timedelta
import time
import json

# In[12]:

# function to calculate fte
# for undergrads fte = total credits/15
# for grads fte = total credits/12
def generate_fte(credits, level):
    if level == 'UGRD':
        return credits / 15.0
    elif level == 'GRAD':
        return credits / 12.0
    else:
        return "Level is not valid"

def edit_school_names(school):
    '''Convert school abbreviation to full name'''
    if school == 'ZSB':
        return 'Zicklin'
    elif school == 'WSAS':
        return 'Weissman'
    elif school == 'SPAF':
        return 'Public Affairs'
    else:
        return 'Baruch'

def perdelta(start, end, delta):
    curr = start
    while curr < end:
        yield curr
        curr += delta

def generate_full_mask(date_mask,mask_level,school_mask,major_mask):
    m1 = np.logical_and(date_mask,mask_level)
    m2 = np.logical_and(m1,school_mask)
    full_mask = np.logical_and(m2,major_mask)
    return full_mask


#open config file and get parameters
with open('config.json') as f:
    config = json.load(f)["school_csv_static"]

data_location = config["location"]
strm_present = config["strm_present"]
strm_past = config["strm_past"]
outfile = config["output"]

# open file and get shape of data
baruch_csv = pd.read_csv(data_location)

# Get header names and unique values in each column
column_names = baruch_csv.columns


#mask rows where no majors are defined
blank_mask = baruch_csv['MAJORSCHOOLS'] != ' '
baruch_csv = baruch_csv[blank_mask]


enroll_dates_present = []
enroll_dates_past = []


today = datetime.strptime(time.strftime("%m/%d/%Y"),"%m/%d/%Y") 
present_year  = str(today.year)
past_year = str(today.year-1)

"""
#get 2015 dates and separate by weeks
for result in perdelta(date(2015, 11, 9), date(today.year,today.month,today.day), timedelta(days=7)):
    enroll_dates_2015.append(result)

#get 2014 dates that match with 2015
for date in enroll_dates_2015:
    #dt = datetime.strptime(date,"%m/%d/%Y")
    prev_dt = datetime(date.year-1,date.month,date.day)
    enroll_dates_2014.append(prev_dt)
"""
#set row to date time for easy comparison
baruch_csv['LAST_ENRL_ADD_DT'] = pd.to_datetime(baruch_csv['LAST_ENRL_ADD_DT'])


#set up lists necessary for iteration
majors = {}
schools = pd.unique(baruch_csv['MAJORSCHOOLS'])
levels = pd.unique(baruch_csv['ACAD_CAREER'])
for school in schools:
    majors[school] = {}
    for level in levels:
        school_mask = baruch_csv['MAJORSCHOOLS'] == school
        level_mask = baruch_csv['ACAD_CAREER'] == level
        total_mask = np.logical_and(school_mask,level_mask)
        school_frame = baruch_csv[total_mask]
        majors[school][level] = pd.unique(school_frame['MAJOR1'])


# initiate dictionary needed to create dataframe
columns = ['Date','School','Count','Academic_Level','Major',past_year,present_year,'Diffs']
counts = ['head_count','credits','fte']
enroll_dict = {}
count_dict = {}
for col in columns:
    enroll_dict[col]= []
for count in counts:
    count_dict[count] ={'past_year': 0,
                        'present_year': 0}
start_date_2015 = '10/10/2015'
start_date_2014 = '10/10/2014'

read_date = pd.unique(baruch_csv['FILEDATE'])[0]
#iterate through lists making rows in the form  
# Date | School | Count | Level | Major | 2014 | 2015 | Diffs
# Count is headcount, FTE, CREDITS
for level in levels:
    for school in schools:
        for major in majors[school][level]:

            # first mask by date
            mask_present = baruch_csv['STRM'] == strm_present
            mask_past = baruch_csv['STRM'] == strm_past

            # mask by level
            mask_level = baruch_csv['ACAD_CAREER'] == level

            #mask by school
            school_mask = baruch_csv['MAJORSCHOOLS'] == school

            #mask by major
            major_mask = baruch_csv['MAJOR1'] == major

            # Combine masks
            full_mask_past = generate_full_mask(mask_past,mask_level,school_mask,major_mask)
            full_mask_present = generate_full_mask(mask_present,mask_level,school_mask,major_mask)

            #calculate counts
            for year,mask in zip([past_year,present_year],[full_mask_past,full_mask_present]):
                head_count = baruch_csv[mask].shape[0]
                credits = baruch_csv[mask]['UNT_BILLING'].sum()
                fte = generate_fte(float(credits), level)
                count_dict['head_count'][year] = head_count
                count_dict['credits'][year] = credits
                count_dict['fte'][year] = fte


            #generate rows
            for count in counts:
                enroll_dict['Date'].append(read_date)
                enroll_dict['School'].append(edit_school_names(school))
                enroll_dict['Count'].append(count)
                enroll_dict['Academic_Level'].append(level)
                enroll_dict['Major'].append(major)

                count_past = count_dict[count][past_year]
                count_present = count_dict[count][present_year]
                enroll_dict[past_year].append(count_past)
                enroll_dict[present_year].append(count_present)
                enroll_dict['Diffs'].append(count_present - count_past)                    


# generate new dataframe
idash_frame = pd.DataFrame(enroll_dict)
idash_frame = idash_frame.reindex(columns=columns)

# for idashboard
idash_frame.to_csv(outfile,index=False, header=True,mode='w')

