import pandas as pd
import numpy as np 
import json

def addRow(enroll_dict,category,actual,target,cat):
    enroll_dict['category'].append(category)
    enroll_dict['actual'].append(actual)
    enroll_dict['target'].append(target)
    enroll_dict['cat'].append(cat)

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
               'target':[],
               'cat':[]}

fall_mask = csv['IRSemesterEnrolledDesc'] == 'Fall' 
csv_fall = csv[fall_mask]
csv_fall['IRHeadcountSUM'] = pd.to_numeric(csv_fall['IRHeadcountSUM'], errors='coerce')

total_enrollment = int(csv_fall['IRHeadcountSUM'].sum())
total_target = targets["total"]
addRow(enroll_dict,'Total Students',total_enrollment,total_target,'total')

#create mask for continuing students
continuing_mask = getContinuingMask(csv_fall)
continuing_total = int(csv_fall['IRHeadcountSUM'][continuing_mask].sum())
continuing_target = targets['continuing']
addRow(enroll_dict,'Continuing Students',continuing_total,continuing_target,'continue')

#mask for new students is just the opposite of continuing
new_total = int(csv_fall['IRHeadcountSUM'][~continuing_mask].sum())
new_target = targets['new']
addRow(enroll_dict,'New Students',new_total,new_target,'new')

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

ucontinuing_mask = getContinuingMask(csv_fall_undergrad)
continuing_utotal = int(csv_fall_undergrad['IRHeadcountSUM'][ucontinuing_mask].sum())
continuing_utarget = targets['continuing_ugrad']
new_utotal = int(csv_fall_undergrad['IRHeadcountSUM'][~ucontinuing_mask].sum())
new_utarget = targets['new_ugrad']

gcontinuing_mask = getContinuingMask(csv_fall_grad)
continuing_gtotal = int(csv_fall_grad['IRHeadcountSUM'][gcontinuing_mask].sum())
continuing_gtarget = targets['continuing_grad']
new_gtotal = int(csv_fall_grad['IRHeadcountSUM'][~gcontinuing_mask].sum())
new_gtarget = targets['new_grad']

addRowDrilldown(enroll_dict,'Continuing Students',continuing_utotal,continuing_utarget,\
                continuing_gtotal,continuing_gtarget)


addRowDrilldown(enroll_dict,'New Students',new_utotal,new_utarget,new_gtotal,new_gtarget)

savefile = 'data/baruch_targets_drill.csv'
idash_frame = pd.DataFrame(enroll_dict)
idash_frame.to_csv(savefile,index=False, header=True,mode='w')

# drill down to lowest level
enroll_dict = {'category':[],
               'actual':[],
               'target':[],
               'cat':[]
               }

#necessary masks
seek_mask =  csv_fall_undergrad['IRSEEKCDDesc'] == 'SEEK'
unondeg_mask = csv_fall_undergrad['IRAdmissionTypeDesc'] == 'Continuing Nondegree'

# CONTINUING DRILL DOWN
#regular continuing
full_mask = np.logical_and(ucontinuing_mask,~seek_mask)
uregcontinue = csv_fall_undergrad[full_mask]
uregcont_actual = uregcontinue['IRHeadcountSUM'].sum()
uregcont_target = targets['regcontinue_ugrad']
addRow(enroll_dict,'Regular Degree Undergrad',uregcont_actual,uregcont_target,'Continuing Students')

#continuing SEEK 
full_mask = np.logical_and(ucontinuing_mask,seek_mask)
seekcontinue = csv_fall_undergrad[full_mask]
seekcont_actual = seekcontinue['IRHeadcountSUM'].sum()
seekcont_target = targets['seekcontinue_ugrad']
addRow(enroll_dict,'SEEK/CD Undergrad', seekcont_actual,seekcont_target,'Continuing Students')

#Nondegree undergrad
unondeg = csv_fall_undergrad[unondeg_mask]
unondeg_actual = unondeg['IRHeadcountSUM'].sum()
unondeg_target = targets['nondeg_ugrad']
addRow(enroll_dict,'Nondegree Undergrad', unondeg_actual,unondeg_target,'Continuing Students')

#continuing degree grad
gdeg_mask = csv_fall_grad['IRAdmissionTypeDesc'] == 'Continuing Degree'
gdeg = csv_fall_grad[gdeg_mask]
gdeg_actual = gdeg['IRHeadcountSUM'].sum()
gdeg_target = targets['deg_grad']
addRow(enroll_dict,'Continuing Degree Graduate', gdeg_actual,gdeg_target,'Continuing Students')

#continuing nondegree grad
gnondeg_mask = csv_fall_grad['IRAdmissionTypeDesc'] == 'Continuing Nondegree'
gnondeg = csv_fall_grad[gnondeg_mask]
gnondeg_actual = gnondeg['IRHeadcountSUM'].sum()
gnondeg_target = targets['nondeg_grad']
addRow(enroll_dict,'Continuing Nondegree Graduate', gnondeg_actual,gnondeg_target,'Continuing Students')

# NEW STUDENTS DRILLDOWN
frosh_mask = csv_fall_undergrad['IRAdmissionTypeDesc'] == 'First-time Freshman'
seek_frosh_mask = np.logical_and(frosh_mask,seek_mask)
nonseek_frosh_mask = np.logical_and(frosh_mask,~seek_mask)

# first time freshmen
newfresh = csv_fall_undergrad[nonseek_frosh_mask]
newfresh_actual = newfresh['IRHeadcountSUM'].sum()
newfresh_target = targets['newfresh']
addRow(enroll_dict,'First-Time Freshmen', newfresh_actual,newfresh_target,'New Students')

# first time seek freshmen
seekfresh = csv_fall_undergrad[seek_frosh_mask]
seekfresh_actual = seekfresh['IRHeadcountSUM'].sum()
seekfresh_target = targets['seekfresh']
addRow(enroll_dict,'SEEK/CD First-Time Freshmen', seekfresh_actual,seekfresh_target,'New Students')

# undergrad readmit
readmit_mask = csv_fall_undergrad['IRAdmissionTypeDesc'] == 'Undergraduate Readmit'
full_mask = np.logical_and(readmit_mask,~seek_mask)
ureadmits = csv_fall_undergrad[full_mask]
readmits_actual = ureadmits['IRHeadcountSUM'].sum()
readmits_target = targets['ureadmits']
addRow(enroll_dict,'Regular Undergraduate Re-admits', readmits_actual,readmits_target,'New Students')

# undergrad seek readmit
full_mask = np.logical_and(readmit_mask,seek_mask)
seekreadmits = csv_fall_undergrad[full_mask]
seekreadmits_actual = seekreadmits['IRHeadcountSUM'].sum()
seekreadmits_target = targets['seekreadmits']
addRow(enroll_dict,'SEEK/CD Undergraduate Re-admits', seekreadmits_actual,seekreadmits_target,'New Students')

# regular undergrad transfer
regtransfer_mask = csv_fall_undergrad['IRAdmissionTypeDesc'] == 'Undergraduate Advanced Standing Transfers'
full_mask = np.logical_and(regtransfer_mask,~seek_mask)
regtransfer = csv_fall_undergrad[full_mask]
regtransfer_actual = regtransfer['IRHeadcountSUM'].sum()
regtransfer_target = targets['regtransfer']
addRow(enroll_dict,'Regular Transfers', regtransfer_actual,regtransfer_target,'New Students')

# seek transfer
full_mask = np.logical_and(regtransfer_mask,seek_mask)
seektransfer = csv_fall_undergrad[full_mask]
seektransfer_actual = seektransfer['IRHeadcountSUM'].sum()
seektransfer_target = targets['seektransfer']
addRow(enroll_dict,'SEEK/CD Transfers', seektransfer_actual,seektransfer_target,'New Students')

# new nondegree undergrad
nondegree_mask = csv_fall_undergrad['IRAdmissionTypeDesc'] == 'First-time Nondegree'
nondeg = csv_fall_undergrad[nondegree_mask]
nondeg_actual = nondeg['IRHeadcountSUM'].sum()
nondeg_target = targets['unewnondeg']
addRow(enroll_dict,'New Nondegree Undergraduates', nondeg_actual,nondeg_target,'New Students')

# new grads
newgrad_mask = csv_fall_grad['IRAdmissionTypeDesc'] == 'First-time Graduate Matriculant'
newgrad = csv_fall_grad[newgrad_mask]
newgrad_actual = newgrad['IRHeadcountSUM'].sum()
newgrad_target = targets['newgrad']
addRow(enroll_dict,'New Graduate Students', newgrad_actual,newgrad_target,'New Students')

# grad readmits
gradreadmit_mask = csv_fall_grad['IRAdmissionTypeDesc'] == 'Graduate Readmit'
gradreadmit =  csv_fall_grad[gradreadmit_mask]
gradreadmit_actual = gradreadmit['IRHeadcountSUM'].sum()
gradreadmit_target = targets['gradreadmit']
addRow(enroll_dict,'Graduate Re-admit', gradreadmit_actual,gradreadmit_target,'New Students')

# Nondegree
gradnondeg_mask = csv_fall_grad['IRAdmissionTypeDesc'] == 'First-time Nondegree'
gradnondeg =  csv_fall_grad[gradnondeg_mask]
gradnondeg_actual = gradnondeg['IRHeadcountSUM'].sum()
gradnondeg_target = targets['gradnondeg']
addRow(enroll_dict,'New Graduate Nondegree', gradnondeg_actual,gradnondeg_target,'New Students')

# TOTALS

#regular degree undergraduates
continuing_mask = getContinuingMask(csv_fall_undergrad)
m1 = np.logical_or(continuing_mask,frosh_mask)
m2 = np.logical_or(m1,readmit_mask)
m3 = np.logical_or(m2,regtransfer_mask)
full_mask = np.logical_and(m3,~seek_mask)
continuing =  csv_fall_undergrad[full_mask]
continuing_actual = continuing['IRHeadcountSUM'].sum()
continuing_target = targets['continue_total']
addRow(enroll_dict,'Regular Degree Undergraduates', continuing_actual,continuing_target,'Total Students')

full_mask = np.logical_and(m3,seek_mask)
seek =  csv_fall_undergrad[full_mask]
seek_actual = seek['IRHeadcountSUM'].sum()
seek_target = targets['seek_total']
addRow(enroll_dict,'SEEK/CD Degree Undergraduates', seek_actual,seek_target,'Total Students')

full_mask = np.logical_or(unondeg_mask,nondegree_mask)
nondeg_ugrad = csv_fall_undergrad[full_mask]
nondeg_actual = nondeg_ugrad['IRHeadcountSUM'].sum()
nondeg_target = targets['unondeg_total']
addRow(enroll_dict,'Nondegree Undergraduates', nondeg_actual,nondeg_target,'Total Students')

m1 = np.logical_or(newgrad_mask,gdeg_mask)
m2 = np.logical_or(m1,gradreadmit_mask)
deg_grad = csv_fall_grad[m2]
gdeg_actual = deg_grad['IRHeadcountSUM'].sum()
gdeg_target = targets['gdeg_total']
addRow(enroll_dict,'Degree Graduate Students', gdeg_actual,gdeg_target,'Total Students')

full_mask = np.logical_or(gradnondeg_mask,gnondeg_mask)
nondeg_grad = csv_fall_grad[full_mask]
nondeg_actual = nondeg_grad['IRHeadcountSUM'].sum()
nondeg_target = targets['gnondeg_total']
addRow(enroll_dict,'Nondegree Graduate Students', nondeg_actual,nondeg_target,'Total Students')

savefile = 'data/baruch_targets_split.csv'
idash_frame = pd.DataFrame(enroll_dict)
idash_frame.to_csv(savefile,index=False, header=True,mode='w')