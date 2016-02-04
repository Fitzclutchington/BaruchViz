###########################################
#                                         #
# python Enrollment_status.py <filename>  #
#                                         #
###########################################

import pandas as pd
import numpy as np
from datetime import datetime


# In[213]:

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
    if semester == '2/1/2016':
        return 'Spring 2016'
    else:
        return 'Winter 2015'
     
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
                            


# In[216]:

#open file and examine columns
csv_filename = '../data/baruch_enrollment_status.csv'
baruch_csv = pd.read_csv(csv_filename)
column_names = baruch_csv.columns
for col in column_names:
    print col,
    print pd.unique(baruch_csv[col]).shape
print pd.unique(baruch_csv['IRAdmissionCategoryDesc'])
print pd.unique(baruch_csv['LINE'])
print pd.unique(baruch_csv['IRAdmissionTypeDesc'])

baruch_csv['IRHeadcountSUM'] = pd.to_numeric(baruch_csv['IRHeadcountSUM'], errors='coerce')
baruch_csv['IRFTESemesterTotalSUMSUM'] = pd.to_numeric(baruch_csv['IRFTESemesterTotalSUMSUM'], errors='coerce')
baruch_csv['IrCrdHrsSemTotalSUM'] = pd.to_numeric(baruch_csv['IrCrdHrsSemTotalSUM'], errors='coerce')



# In[217]:

levels = np.sort(pd.unique(baruch_csv['IRClassLevelDesc']))
semester_dates = pd.unique(baruch_csv['IRTermEnrolledDate'])
student_categories =  pd.unique(baruch_csv['LINE'])
schools = pd.unique(baruch_csv['SCHOOL'])
print semester_dates


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

filenames = ['../data/baruch_enrollment_status_grad_script.csv','../data/baruch_enrollment_status_undergrad_script.csv']
for level,filename in zip(levels,filenames):
    level_mask = baruch_csv['IRClassLevelDesc'] == level
    print level
    level_csv = baruch_csv[level_mask]
    
    data_columns = list(pd.unique(level_csv['LINE']))
    total_columns = first_columns + data_columns
    
    enroll_dict = {}
    for col in total_columns:
        enroll_dict[col]= []

    generate_enrollment_dict(level_csv,semester_dates,schools,majors,level,count_dict,enroll_dict, data_columns)
    idash_frame = pd.DataFrame(enroll_dict)
    idash_frame = idash_frame.reindex(columns=total_columns)
    idash_frame.to_csv(filename,index=False, header=True,mode='w')


# In[143]:




# In[ ]:




# In[ ]:



