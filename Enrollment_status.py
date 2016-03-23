"""
This script converts a spreadsheet containing students'
enrollment statuses into a csv file used to generate a 
bar chart in iDashboards.
"""

import pandas as pd
import numpy as np
from datetime import date, datetime, timedelta
import time
import json


def edit_school_names(school):
    if school == 'Z':
        return 'Zicklin'
    elif school == 'W':
        return 'Weissman'
    elif school == 'S':
        return 'Public Affairs'
    elif school == 'BAR':
        return 'Baruch'
    else:
        return 'Non-classified'

def edit_semester_names(semester):
    if semester == '6/1/2016':
        return 'Summer 2016'
    else:
        return 'Fall 2016'
     
def edit_major_names(major):
    if major == ' ':
        return 'Non-classified'
    else:
        return major


# In[214]:

def generate_full_mask(date_mask,school_mask,major_mask):
    m1 = np.logical_and(date_mask,school_mask)
    full_mask = np.logical_and(m1,major_mask)
    return full_mask


# In[215]:

def generate_enrollment_dict(level_csv,semester_dates,schools,majors,level,count_dict,enroll_dict, data_columns):
    #iterate through lists making rows in the form  
    # Date | School | Count | Level | Major | 2014 | 2015 | Diffs
    # Count is headcount, FTE, CREDITS
    for semester in semester_dates:
        for school in schools:
            for major in majors[school][level]:
                

                mask_term = baruch_csv['IRTermEnrolledDate'] == semester
                
                #mask by school
                school_mask = baruch_csv['SCHOOL'] == school
               
                #mask by major
                major_mask = baruch_csv['ACAD_PLAN'] == major
        
                
                # Combine masks
                full_mask = generate_full_mask(mask_term,school_mask,major_mask)
              
                head_count_list = []
                credit_count_list = []
                fte_count_list = []

                for col in data_columns:
                    status_mask = baruch_csv['LINE'] == col
                    new_mask = np.logical_and(full_mask,status_mask)

                    head_count = baruch_csv[new_mask]['IRHeadcountSUM'].sum()
                    credits = baruch_csv[new_mask]['IrCrdHrsSemTotalSUM'].sum()
                    fte = baruch_csv[new_mask]['IRFTESemesterTotalSUMSUM'].sum()

                    head_count_list.append(head_count)
                    credit_count_list.append(credits)
                    fte_count_list.append(fte)

                count_dict['head_count'] = head_count_list
                count_dict['credits'] = credit_count_list
                count_dict['fte'] = fte_count_list


                #generate rows
                for count in counts:
                    enroll_dict['Semester'].append(edit_semester_names(semester))
                    enroll_dict['School'].append(edit_school_names(school))
                    enroll_dict['Count'].append(count)
                    enroll_dict['Major'].append(edit_major_names(major))

                    for i,col in enumerate(data_columns):
                        enroll_dict[col].append(count_dict[count][i])
                            

# open config and get parameters
with open('config.json') as f:
    config = json.load(f)["enrollment_status"]

data_location = config["location"]
outdir = config["outdir"]
backup_dir = config["backup_dir"]
grad_outfile = config["grad_output"]
undergrad_outfile = config["undergrad_output"]

semester_list = config["semester"]

#open file and examine columns
csv_filename = data_location
baruch_csv = pd.read_csv(csv_filename)
column_names = baruch_csv.columns
"""
for col in column_names:
    print col,
    print pd.unique(baruch_csv[col]).shape
print pd.unique(baruch_csv['IRAdmissionCategoryDesc'])
print pd.unique(baruch_csv['LINE'])
print pd.unique(baruch_csv['IRAdmissionTypeDesc'])
"""
baruch_csv['IRHeadcountSUM'] = pd.to_numeric(baruch_csv['IRHeadcountSUM'], errors='coerce')
baruch_csv['IRFTESemesterTotalSUMSUM'] = pd.to_numeric(baruch_csv['IRFTESemesterTotalSUMSUM'], errors='coerce')
baruch_csv['IrCrdHrsSemTotalSUM'] = pd.to_numeric(baruch_csv['IrCrdHrsSemTotalSUM'], errors='coerce')

# date setup for file names
today = datetime.strptime(time.strftime("%m/%d/%Y"),"%m/%d/%Y")
backup_date = '_' + str(today.month) + '_' + str(today.day) + '_' + str(today.year)

# set up column iterators
levels = np.sort(pd.unique(baruch_csv['IRClassLevelDesc']))
semester_dates = pd.unique(baruch_csv['IRTermEnrolledDate'])
student_categories =  pd.unique(baruch_csv['LINE'])
schools = pd.unique(baruch_csv['SCHOOL'])

data_columns = {'GRADUATE': ['GRAD Continuing Degree', 'GRAD New Nondegree', 
                             'GRAD Permit-in', 'GRAD Re-admits', 'GRAD New Graduate'],
                'UNDERGRADUATE': ['UG New Regular Transfers', 'UG Continuing Regular Degree', 
                                  'UG Regular Re-admits', 'UG Continuing SEEK/CD', 'UG New Nondegree', 
                                  'UG Continuing Nondegree', 'UG Permit-in', 'GRAD New Graduate', 
                                  'UG SEEK/CD Re-admits', 'UG Senior Citizens']}

# In[218]:

#set up lists necessary for iteration
majors = {}
statuses = {}
for school in schools:
    majors[school] = {}
    for level in levels:
        school_mask = baruch_csv['SCHOOL'] == school
        level_mask = baruch_csv['IRClassLevelDesc'] == level
        total_mask = np.logical_and(school_mask,level_mask)
        school_frame = baruch_csv[total_mask]
        majors[school][level] = pd.unique(school_frame['ACAD_PLAN'])
        
for level in levels:
    level_mask = baruch_csv['IRClassLevelDesc'] == level
    school_frame = baruch_csv[level_mask]
    statuses[level] = pd.unique(baruch_csv['LINE'])


# In[219]:

first_columns = ['Semester','School','Count','Major']

counts = ['head_count','credits','fte']
count_dict = {}
for count in counts:
    count_dict[count] = []


# In[220]:

filenames = [grad_outfile, undergrad_outfile]
for level,filename in zip(levels,filenames):
    level_mask = baruch_csv['IRClassLevelDesc'] == level
    level_csv = baruch_csv[level_mask]

    total_columns = first_columns + data_columns[level]

    enroll_dict = {}
    for col in total_columns:
        enroll_dict[col]= []

    generate_enrollment_dict(level_csv,semester_dates,schools,majors,level,count_dict,enroll_dict, data_columns[level])
    idash_frame = pd.DataFrame(enroll_dict)
    idash_frame = idash_frame.reindex(columns=total_columns)

    #set up location to save
    dashboard_csv = outdir + '/' + filename + '.csv'
    backup_csv = backup_dir + '/' + filename + backup_date + '.csv'

    idash_frame.to_csv(dashboard_csv,index=False, header=True,mode='w')
    idash_frame.to_csv(backup_csv,index=False, header=True,mode='w')
    
