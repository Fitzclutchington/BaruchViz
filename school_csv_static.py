###########################################
#                                         #
# python school_csv_static.py <filename>  #
#                                         #
###########################################

import pandas as pd
import numpy as np
from datetime import date, datetime, timedelta
import time

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
# In[13]:

def generate_full_mask(date_mask,mask_level,school_mask,major_mask):
    m1 = np.logical_and(date_mask,mask_level)
    m2 = np.logical_and(m1,school_mask)
    full_mask = np.logical_and(m2,major_mask)
    return full_mask


# In[14]:

# open file and get shape of data
baruch_csv = pd.read_csv('../data/baruch_school_data.csv')
#baruch_csv['LAST_ENRL_ADD_DT'] = pd.to_datetime(baruch_csv['LAST_ENRL_ADD_DT'])
print baruch_csv.shape


# In[15]:

# Get header names and unique values in each column
column_names = baruch_csv.columns
#print ', '.join(column_names)


#mask weird row
blank_mask = baruch_csv['MAJORSCHOOLS'] != ' '
baruch_csv = baruch_csv[blank_mask]


# In[16]:

#get dates and save

enroll_dates_2015 = []
enroll_dates_2014 = []
#get 2015 dates
today = datetime.strptime(time.strftime("%m/%d/%Y"),"%m/%d/%Y") 
for result in perdelta(date(2015, 11, 9), date(today.year,today.month,today.day), timedelta(days=7)):
    enroll_dates_2015.append(result)

print enroll_dates_2015
#get 2014 dates that match with 2015
for date in enroll_dates_2015:
    #dt = datetime.strptime(date,"%m/%d/%Y")
    prev_dt = datetime(date.year-1,date.month,date.day)
    enroll_dates_2014.append(prev_dt)

#set row to date time for easy comparison
baruch_csv['LAST_ENRL_ADD_DT'] = pd.to_datetime(baruch_csv['LAST_ENRL_ADD_DT'])


# In[17]:

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


# In[18]:

# initiate dictionary needed to create dataframe
columns = ['Date','School','Count','Academic_Level','Major','2014','2015','Diffs']
counts = ['head_count','credits','fte']
enroll_dict = {}
count_dict = {}
for col in columns:
    enroll_dict[col]= []
for count in counts:
    count_dict[count] ={'2014': 0,
                        '2015': 0}
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
            mask_2015 = baruch_csv['STRM'] == 1162
            mask_2014 = baruch_csv['STRM'] == 1152

            # mask by level
            mask_level = baruch_csv['ACAD_CAREER'] == level

            #mask by school
            school_mask = baruch_csv['MAJORSCHOOLS'] == school

            #mask by major
            major_mask = baruch_csv['MAJOR1'] == major

            # Combine masks
            full_mask_2014 = generate_full_mask(mask_2014,mask_level,school_mask,major_mask)
            full_mask_2015 = generate_full_mask(mask_2015,mask_level,school_mask,major_mask)

            #calculate counts
            for year,mask in zip(['2014','2015'],[full_mask_2014,full_mask_2015]):
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

                count_2014 = count_dict[count]['2014']
                count_2015 = count_dict[count]['2015']
                enroll_dict['2014'].append(count_2014)
                enroll_dict['2015'].append(count_2015)
                enroll_dict['Diffs'].append(count_2015-count_2014)                    


# In[19]:

# generate new dataframe
idash_frame = pd.DataFrame(enroll_dict)
idash_frame = idash_frame.reindex(columns=columns)
print idash_frame.shape
idash_frame.to_csv('../data/static_school_major_script.csv',index=False, header=True,mode='w')
