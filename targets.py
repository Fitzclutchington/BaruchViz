import pandas as pd
import numpy as np 
import json

def addRow(enroll_dict,category,actual,target):
    enroll_dict['category'].append(category)
    enroll_dict['actual'].append(actual)
    enroll_dict['target'].append(target)

def addRowDrilldown(enroll_dict,category,uactual,utarget,gactual,gtarget):
    enroll_dict['category'].append(category)
    enroll_dict['undergrad_actual'].append(uactual)
    enroll_dict['undergrad_target'].append(utarget)
    enroll_dict['grad_actual'].append(gactual)
    enroll_dict['grad_target'].append(gtarget)

def getContinuingMask(csv):
    m1 = csv['IRAdmissionTypeDesc'] == 'Continuing Degree'
    m2 = csv['IRAdmissionTypeDesc'] == 'Continuing Nondegree'
    continuing_mask = np.logical_or(m1,m2)
    return continuing_mask

#targets
with open('targets.json') as f:
    targets = json.load(f)
 
#uses CIBL data
datafile = 'data/baruch_enrollment_status.csv'
csv = pd.read_csv(datafile)
enroll_dict = {'category':[],
               'actual':[],
               'target':[]}

fall_mask = csv['IRSemesterEnrolledDesc'] == 'Fall' 
csv_fall = csv[fall_mask]
csv_fall['IRHeadcountSUM'] = pd.to_numeric(csv_fall['IRHeadcountSUM'], errors='coerce')

total_enrollment = int(csv_fall['IRHeadcountSUM'].sum())
total_target = targets["total"]
addRow(enroll_dict,'Total Students',total_enrollment,total_target)

#create mask for continuing students
continuing_mask = getContinuingMask(csv_fall)
continuing_total = int(csv_fall['IRHeadcountSUM'][continuing_mask].sum())
continuing_target = targets['continuing']
addRow(enroll_dict,'Continuing Students',continuing_total,continuing_target)

#mask for new students is just the opposite of continuing
new_total = int(csv_fall['IRHeadcountSUM'][~continuing_mask].sum())
new_target = targets['new']
addRow(enroll_dict,'New Students',new_total,new_target)

savefile = 'data/baruch_targets_total.csv'
idash_frame = pd.DataFrame(enroll_dict)
idash_frame.to_csv(savefile,index=False, header=True,mode='w')

# Form drilldown csv
enroll_dict = {'category':[],
               'undergrad_actual':[],
               'undergrad_target':[],
               'grad_actual':[],
               'grad_target':[]
               }

csv_fall_undergrad = csv_fall[csv_fall['IRClassLevelDesc']=='UNDERGRADUATE']
csv_fall_grad = csv_fall[csv_fall['IRClassLevelDesc']=='GRADUATE']

# total enrollment grad/ugrad
total_uenrollment = int(csv_fall_undergrad['IRHeadcountSUM'].sum())
total_utarget = targets["total_ugrad"]
total_genrollment = int(csv_fall_grad['IRHeadcountSUM'].sum())
total_gtarget = targets["total_grad"]
addRowDrilldown(enroll_dict,'Total Students',total_uenrollment,total_utarget,total_genrollment,total_gtarget)

continuing_mask = getContinuingMask(csv_fall_undergrad)
continuing_utotal = int(csv_fall_undergrad['IRHeadcountSUM'][continuing_mask].sum())
continuing_utarget = targets['continuing_ugrad']
new_utotal = int(csv_fall_undergrad['IRHeadcountSUM'][~continuing_mask].sum())
new_utarget = targets['new_ugrad']

continuing_mask = getContinuingMask(csv_fall_grad)
continuing_gtotal = int(csv_fall_grad['IRHeadcountSUM'][continuing_mask].sum())
continuing_gtarget = targets['continuing_grad']
new_gtotal = int(csv_fall_grad['IRHeadcountSUM'][~continuing_mask].sum())
new_gtarget = targets['new_grad']

addRowDrilldown(enroll_dict,'Continuing Students',continuing_utotal,continuing_utarget,\
                continuing_gtotal,continuing_gtarget)


addRowDrilldown(enroll_dict,'New Students',new_utotal,new_utarget,new_gtotal,new_gtarget)

savefile = 'data/baruch_targets_drill.csv'
idash_frame = pd.DataFrame(enroll_dict)
idash_frame.to_csv(savefile,index=False, header=True,mode='w')
