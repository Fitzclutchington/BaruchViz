<<<<<<< HEAD
"""
This script converts a spreadsheet containing students'
enrollment statuses into a csv file used to generate a 
bar chart in iDashboards.
"""
=======
'''
This script is responsible for the spread sheet that creates the
student enrollment status charts on iDashboard.

This script requires a csv file with the name baruch_enrollment_status.csv and the following columns:

    IRHeadcountSUM
    IRFTESemesterTotalSUMSUM
    IrCrdHrsSemTotalSUM
    IRClassLevelDesc (grad or undergrad)
    LINE (description of enrollment status eg. first time freshman)
    IRTermEnrolledDate
    SCHOOL
    ACAD_PLAN (major)

Note that each row is an individual student.

This script generates 2 spreadsheets with the following columns:

    for graduate students:
        Semester - The semester enrolled (Winter 2016, Spring 2016) (pivot)
        School - The school attended (pivot)
        Count - Head Count, FTE, Credit Hrs (pivot)
        Major
        GRAD Continuing
        GRAD New Nondegree
        GRAD Permit-in
        GRAD Re-admits
        GRAD New Graduates

    For undergraduate students:
        Semester - The semester enrolled (Winter 2016, Spring 2016) (pivot)
        School - The school attended (pivot)
        Count - Head Count, FTE, Credit Hrs (pivot)
        Major
        UG New Regular Transfers
        UG Continuing Regular Degree
        UG Regular Re-admits
        UG Continuing SEEK/CD
        UG Continuing Nondegree
        UG Permit-in
        GRAD New Graduate
        UG SEEK/CD Re-admits
        UG Senior Citizens

'''
>>>>>>> origin/master

import pandas as pd
import numpy as np
from datetime import datetime


def edit_school_names(school):
    ''' A function to convert the abbreviated school names into full school names'''
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
    ''' A function to convert dates into semester names'''0
    if semester == '2/1/2016':
        return 'Spring 2016'
    else:
        return 'Winter 2015'
     
def edit_major_names(major):
    ''' A function to handle the case where no major is indicated'''
    if major == ' ':
        return 'Non-classified'
    else:
        return major



def generate_full_mask(date_mask,school_mask,major_mask):
    ''' A function to logical and all masks required when generating a column'''
    m1 = np.logical_and(date_mask,school_mask)
    full_mask = np.logical_and(m1,major_mask)
    return full_mask


def generate_enrollment_dict(level_csv,semester_dates,schools,majors,level,count_dict,enroll_dict, data_columns):
    '''This function takes as input
       -level_csv: a pandas dataframe that is masked for only graduate or undergraduate
       -semester_dates: a list of semester dates
       -schools: a list of schools
       -majors: a list of majors
       -level: a string that specifies GRAD or UGRAD
       -count_dict: a dictionary to aid in the process of aggregating count types
       -enroll_dict: a dictionary that will be populated in order to convert into a new dataframe
       -data_columns: a list of the columns being generated

       It then populates enroll_dict with values'''
    #iterate through column values in order to create rows
    for semester in semester_dates:
        for school in schools:
            for major in majors[school][level]:
                
                #mask by semester 
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
                            


#open file and examine columns
csv_filename = '../data/baruch_enrollment_status.csv'
baruch_csv = pd.read_csv(csv_filename)
column_names = baruch_csv.columns
<<<<<<< HEAD
"""
=======
# These print statements were necessary to explore the kind of data in each column
>>>>>>> origin/master
for col in column_names:
    print col,
    print pd.unique(baruch_csv[col]).shape
print pd.unique(baruch_csv['IRAdmissionCategoryDesc'])
print pd.unique(baruch_csv['LINE'])
print pd.unique(baruch_csv['IRAdmissionTypeDesc'])
<<<<<<< HEAD
"""
=======

# Converts head count values, fte values, and credit hour values from strings to integers
>>>>>>> origin/master
baruch_csv['IRHeadcountSUM'] = pd.to_numeric(baruch_csv['IRHeadcountSUM'], errors='coerce')
baruch_csv['IRFTESemesterTotalSUMSUM'] = pd.to_numeric(baruch_csv['IRFTESemesterTotalSUMSUM'], errors='coerce')
baruch_csv['IrCrdHrsSemTotalSUM'] = pd.to_numeric(baruch_csv['IrCrdHrsSemTotalSUM'], errors='coerce')

# these lines create lists that will bbe interated through in generate_enrollment_dict
levels = np.sort(pd.unique(baruch_csv['IRClassLevelDesc']))
semester_dates = pd.unique(baruch_csv['IRTermEnrolledDate'])
student_categories =  pd.unique(baruch_csv['LINE'])
schools = pd.unique(baruch_csv['SCHOOL'])
<<<<<<< HEAD

data_columns = {'GRADUATE': ['GRAD Continuing Degree', 'GRAD New Nondegree', 
                             'GRAD Permit-in', 'GRAD Re-admits', 'GRAD New Graduate'],
                'UNDERGRADUATE': ['UG New Regular Transfers', 'UG Continuing Regular Degree', 
                                  'UG Regular Re-admits', 'UG Continuing SEEK/CD', 'UG New Nondegree', 
                                  'UG Continuing Nondegree', 'UG Permit-in', 'GRAD New Graduate', 
                                  'UG SEEK/CD Re-admits', 'UG Senior Citizens']}
=======
>>>>>>> origin/master


#set up dictionaries that will be used for iteration
#Needs to be refactored
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

first_columns = ['Semester','School','Count','Major']

# creates a dictionary that aids in count aggregation
counts = ['head_count','credits','fte']
count_dict = {}
for count in counts:
    count_dict[count] = []


filenames = ['../data/baruch_enrollment_status_grad_script.csv','../data/baruch_enrollment_status_undergrad_script.csv']
for level,filename in zip(levels,filenames):
    level_mask = baruch_csv['IRClassLevelDesc'] == level
    level_csv = baruch_csv[level_mask]
<<<<<<< HEAD

    total_columns = first_columns + data_columns[level]
=======
    
    data_columns = list(pd.unique(level_csv['LINE']))
    total_columns = first_columns + data_columns
>>>>>>> origin/master

    enroll_dict = {}
    for col in total_columns:
        enroll_dict[col]= []
<<<<<<< HEAD

    generate_enrollment_dict(level_csv,semester_dates,schools,majors,level,count_dict,enroll_dict, data_columns[level])
=======
    
    generate_enrollment_dict(level_csv,semester_dates,schools,majors,level,count_dict,enroll_dict, data_columns)
>>>>>>> origin/master
    idash_frame = pd.DataFrame(enroll_dict)
    idash_frame = idash_frame.reindex(columns=total_columns)
    idash_frame.to_csv(filename,index=False, header=True,mode='w')
    

