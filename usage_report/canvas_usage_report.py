#!/usr/bin/env python
#################################################
#Author: Matt Lewis
#Department: Instructional Technology
#Institution: Eastern Washington University
##################################################
################## DESCRIPTION ###################
##################################################
#This script creates, download, extracts, and opens Canvas Provisioning reports and Unused Courses report by term.
#Summary data about Canvas usage is saved to a csv file as well as course list with enrollment counts
#xlist courses count, and if the course went unused. An unused course is defined as being published but with no
#assignments, announcements, discussions, files, modules, pages, or quizzes.

##################################################
################## DIRECTIONS ####################
##################################################
# DIRECTIONS: Edit the below variables to match your institution domain
domain = "canvas.[name].edu"

##################################################
########## DO NOT EDIT BELOW THIS LINE ###########
##################################################

import argparse
import sys,os
import csv
import pprint
import os
import getpass
import configparser
import canvasConnect as canvas
from timeit import default_timer as timer
import zipfile
import pandas as pd
from collections import defaultdict
start = timer()

###########################################################################   
############################ File Arguments ###############################
###########################################################################  
# Prepare argument parsing
parser = argparse.ArgumentParser()
parser.add_argument('--use_file_name',required=False,help='save data to csv file with this name')
args = parser.parse_args()
use_file_name = args.use_file_name
###########################################################################   
#################### Set Authentication Token #############################
###########################################################################  
try:
  config = configparser.ConfigParser()
  config.read(".canvasConfig")
  token = config['configuration']['token']
except:
  print('The Canvas Config file could not be found, please enter your Canvas token.')
  token = getpass.getpass('Canvas Token:')

confirmToken = canvas.confirm_token(domain, token)

if not token or confirmToken == False:
  token = getpass.getpass('Canvas Token is a required field:')
  confirmToken = canvas.confirm_token(domain, token)

if not token or confirmToken == False:
    print('#########################################################################')
    print('The Canvas Token is a required field.')
    print('Exiting script.')
    print('#########################################################################')
    exit()

#########################################################################
####################### Collect Account ID ##############################
#########################################################################  
root_account_id = canvas.getRootID(domain, token)
if root_account_id == "No Root":
  print('#########################################################################')
  print('ERROR: Could not find the Root ID. Please enter an account id.')
  print('#########################################################################')
  exit()


accountList = canvas.subAccounts(domain, token, root_account_id)
displayAccount = input('An account is required. Do you want to display a list of account ids? Or you can enter the account id or "ALL" instead. (Yes, account #, All):')
if displayAccount.upper() == 'Y' or displayAccount.upper() == 'YES':
  print('Account ID     NAME')
  for a in accountList:
    print(a['account_id'], ' - ', a['account_name'])
  accountID = input('Enter the Account ID:')
else:
  accountID = displayAccount

confirmAccount = canvas.confirm_account(domain, token, accountList, accountID)
  
if not accountID or confirmAccount == False:
  accountID = root_account_id
  print('#########################################################################')
  print('The Account entered didn\'t match, accountID set to root.')
  print('#########################################################################')

#########################################################################
######################## Collect Term ID ################################
#########################################################################
termData = canvas.get_terms(domain, token, root_account_id)
displayTerm = input('A term designation is required. Do you want to display a list of term ids? Or you can enter the term id or "ALL" instead.(Yes, term #, All):')
if displayTerm.upper() == 'Y' or displayTerm.upper() == 'YES':
  print('Term ID     NAME')
  for t in termData:
    print(t['term_id'], ' - ', t['term_name'])
  termID = input('Enter the Term ID:')
else:
  termID = displayTerm

if displayTerm.upper() != 'ALL':
  confirmTerm = canvas.confirm_term(domain, token, termData, termID)

if not termID or confirmTerm == False:
  termID = input('The term id entered is not valid. Enter another term id:')
  confirmTerm = canvas.confirm_term(domain, token, termData, termID)
  
if not termID or confirmTerm == False:
    print('#########################################################################')
    print('The Term is a required field.')
    print('Exiting script.')
    print('#########################################################################')
    exit()

#single out the data for a specific term
termInfo = canvas.get_term_info(termData, termID)

#########################################################################
##################### Canvas API Reports ################################
#########################################################################
#Make a call to the Canvas API to generate and download the Provisioning
# and Unused_Courses reports. The Provisioning report can be customized
# to allow for multiple file parameters. Only the courses, enrollments,
#and xlist files are needed here.
#########################################################################
########################## Unused Courses################################

unused_report_path= canvas.create_api_report(domain, token, accountID, termID, "unused_courses_csv", "")
print(unused_report_path)
df = pd.read_csv(unused_report_path)
df = df.rename(columns = {'course id': 'canvas_course_id', 'status':'status_unused'})
unused_courses = df[['canvas_course_id', 'status_unused']]

#########################################################################
######################### Provisioning Files ############################
#provision reports are saved as zip files, the extracted reports are in
#a folder titled the same as the zip. To get the folder name, remove .zip
#from the string. create counts of the number of courses, student enrollment
#in courses, and number of other courses xlisted.

accounts = False
courses = True
enrollments = True
sections = False
users = False
xlist = True

#create, save, and extract the provisioning reports, return the path of the report 
provision_report_path = canvas.create_provisioning_report(domain, token, accountID, termID, "provisioning_csv", "", accounts, courses, enrollments, sections, users, xlist)
#get zip file name from returned report path
title_path=provision_report_path.split(".")
report_path=title_path[0].split("_")
reportID=report_path[7]
report_date= '%s_%s_%s' % (report_path[4], report_path[5],report_path[6])

if courses == True:
  course_path = title_path[0] + "/courses.csv"
  df = pd.read_csv(course_path)
  courses = df
  course_count = df.groupby([df.canvas_term_id, df.status]).size()

if enrollments == True:
  enrollment_path = title_path[0] + "/enrollments.csv"    
  df = pd.read_csv(enrollment_path)
  df = df[df.role== 'student']
  enrollment_count = df.groupby([df.canvas_course_id]).size().rename('enrolled_count')

if xlist == True:
  xlist_path = title_path[0] + "/xlist.csv"
  df = pd.read_csv(xlist_path)
  df = df.rename(columns = {'canvas_xlist_course_id': 'canvas_course_id'})
  xlist_count = df.groupby([df.canvas_course_id]).size().rename('xlist_count')
  #print('xlist count: ', df['canvas_section_id'].count())
  #print(xlist_count.sum())
  
#########################################################################
########################### Join and Merge ##############################
#########################################################################
#Join and merge data from courses, enrollments, xlist, and unused courses
#into a single dataframe.
#########################################################################
canvasData = courses.join(enrollment_count, on=('canvas_course_id'))
canvasData = canvasData.join(xlist_count, on=('canvas_course_id'))
#print(canvasData.dtypes)
canvasData = canvasData.merge(unused_courses, on='canvas_course_id', how='left')

#########################################################################
############################## Filter ###################################
#########################################################################
#Filter data and create summary statistic variables.
#########################################################################

#Split data into accounts
accounts_dict= {k: v for k, v in canvasData.groupby('canvas_account_id')}


print('#############################################')
course_count = canvasData['canvas_course_id'].count()

canvasData_published = canvasData.loc[canvasData['status'] == 'active']
course_published_count = canvasData_published['canvas_course_id'].count()


course_enrolled1 = canvasData[(canvasData['enrolled_count']>0)]
course_enrolled_count1 = course_enrolled1['canvas_course_id'].count()
course_enrolled2 = canvasData[(canvasData['enrolled_count']>1)]
course_enrolled_count2 = course_enrolled2['canvas_course_id'].count()
course_enrolled3 = canvasData[(canvasData['enrolled_count']>2)]
course_enrolled_count3 = course_enrolled3['canvas_course_id'].count()
course_enrolled4 = canvasData[(canvasData['enrolled_count']>3)]
course_enrolled_count4 = course_enrolled4['canvas_course_id'].count()
course_enrolled5 = canvasData[(canvasData['enrolled_count']>4)]
course_enrolled_count5 = course_enrolled5['canvas_course_id'].count()


canvasData_published_enrolled1 = canvasData[(canvasData['status'] == 'active') & (canvasData['enrolled_count'] > 0)]
course_published_enrolled_count1 = canvasData_published_enrolled1['canvas_course_id'].count()
canvasData_published_enrolled2 = canvasData[(canvasData['status'] == 'active') & (canvasData['enrolled_count'] > 1)]
course_published_enrolled_count2 = canvasData_published_enrolled2['canvas_course_id'].count()
canvasData_published_enrolled3 = canvasData[(canvasData['status'] == 'active') & (canvasData['enrolled_count'] > 2)]
course_published_enrolled_count3 = canvasData_published_enrolled3['canvas_course_id'].count()
canvasData_published_enrolled4 = canvasData[(canvasData['status'] == 'active') & (canvasData['enrolled_count'] > 3)]
course_published_enrolled_count4 = canvasData_published_enrolled4['canvas_course_id'].count()
canvasData_published_enrolled5 = canvasData[(canvasData['status'] == 'active') & (canvasData['enrolled_count'] > 4)]
course_published_enrolled_count5 = canvasData_published_enrolled5['canvas_course_id'].count()

xlist_published_sum = canvasData_published['xlist_count'].sum()
xlist_published_enrolled_sum1 = canvasData_published_enrolled1['xlist_count'].sum()
xlist_published_enrolled_sum2 = canvasData_published_enrolled2['xlist_count'].sum()
xlist_published_enrolled_sum3 = canvasData_published_enrolled3['xlist_count'].sum()
xlist_published_enrolled_sum4 = canvasData_published_enrolled4['xlist_count'].sum()
xlist_published_enrolled_sum5 = canvasData_published_enrolled5['xlist_count'].sum()

unused_published = canvasData_published.loc[canvasData_published['status_unused'] == 'active']
unused_published_count = unused_published['status_unused'].count()

unused_published_enrolled1 = canvasData_published_enrolled1.loc[canvasData_published_enrolled1['status_unused'] == 'active']
unused_published_enrolled2 = canvasData_published_enrolled2.loc[canvasData_published_enrolled2['status_unused'] == 'active']
unused_published_enrolled3 = canvasData_published_enrolled3.loc[canvasData_published_enrolled3['status_unused'] == 'active']
unused_published_enrolled4 = canvasData_published_enrolled4.loc[canvasData_published_enrolled4['status_unused'] == 'active']
unused_published_enrolled5 = canvasData_published_enrolled5.loc[canvasData_published_enrolled5['status_unused'] == 'active']
unused_published_enrolled_count1 = unused_published_enrolled1['status_unused'].count()
unused_published_enrolled_count2 = unused_published_enrolled2['status_unused'].count()
unused_published_enrolled_count3 = unused_published_enrolled3['status_unused'].count()
unused_published_enrolled_count4 = unused_published_enrolled4['status_unused'].count()
unused_published_enrolled_count5 = unused_published_enrolled5['status_unused'].count()

print('account id: ', accountID)
print('term id: ', termID)
print('term start date: ', termInfo['start_at'])
print('term name: ', termInfo['term_name'])
print('report path: ', title_path[0])
print('report id: ', reportID)
print('report date: ', report_date)
print('course count: ',course_count)
print('course published count: ' ,course_published_count)
print('course enrolled count >=1: ',course_enrolled_count1)
print('course enrolled count >=2: ',course_enrolled_count2)
print('course enrolled count >=3: ',course_enrolled_count3)
print('enrolled published count >=1: ', course_published_enrolled_count1 )
print('enrolled published count >=2: ', course_published_enrolled_count2 )
print('enrolled published count >=3: ', course_published_enrolled_count3 )
print('xlist published sum: ', xlist_published_sum)
print('xlist enrolled published sum: ', xlist_published_enrolled_sum1)
print('unused published c ', unused_published_count)
print('unused enrolled published count: ', unused_published_enrolled_count1)

print('#############################################')
total_course_published_count = (course_published_count + xlist_published_sum - unused_published_count)
total_course_published_percentage = ((course_published_count + xlist_published_sum - unused_published_count)/ course_count)*100

total_course_published_enrolled_count1 = (course_published_enrolled_count1 + xlist_published_enrolled_sum1 - unused_published_enrolled_count1)
total_course_published_enrolled_percentage1= ((course_published_enrolled_count1 + xlist_published_enrolled_sum1 - unused_published_enrolled_count1)/ course_enrolled_count1)*100

total_course_published_enrolled_count2 = (course_published_enrolled_count2 + xlist_published_enrolled_sum2 - unused_published_enrolled_count2)
total_course_published_enrolled_percentage2= ((course_published_enrolled_count2 + xlist_published_enrolled_sum2 - unused_published_enrolled_count2)/ course_enrolled_count2)*100

total_course_published_enrolled_count3 = (course_published_enrolled_count3 + xlist_published_enrolled_sum3 - unused_published_enrolled_count3)
total_course_published_enrolled_percentage3= ((course_published_enrolled_count3 + xlist_published_enrolled_sum3 - unused_published_enrolled_count3)/ course_enrolled_count3)*100

total_course_published_enrolled_count4 = (course_published_enrolled_count4 + xlist_published_enrolled_sum4 - unused_published_enrolled_count4)
total_course_published_enrolled_percentage4= ((course_published_enrolled_count4 + xlist_published_enrolled_sum4 - unused_published_enrolled_count4)/ course_enrolled_count4)*100

total_course_published_enrolled_count5 = (course_published_enrolled_count5 + xlist_published_enrolled_sum5 - unused_published_enrolled_count5)
total_course_published_enrolled_percentage5= ((course_published_enrolled_count5 + xlist_published_enrolled_sum5 - unused_published_enrolled_count5)/ course_enrolled_count5)*100

print('Total count courses published: ', total_course_published_count)
print('Total % courses published: ', total_course_published_percentage ,'%' )

print('Total count courses published enrolled >=1: ', total_course_published_enrolled_count1)
print('Total % courses published enrolled >=1: ', total_course_published_enrolled_percentage1,'%' )

print('Total count courses published enrolled >=2: ', total_course_published_enrolled_count2)
print('Total % courses published enrolled >=2: ', total_course_published_enrolled_percentage2,'%' )

print('Total count courses published enrolled >=3: ', total_course_published_enrolled_count3)
print('Total % courses published enrolled >=3: ', total_course_published_enrolled_percentage3,'%' )

print('Total count courses published enrolled >=4: ', total_course_published_enrolled_count4)
print('Total % courses published enrolled >=4: ', total_course_published_enrolled_percentage4,'%' )

print('Total count courses published enrolled >=5: ', total_course_published_enrolled_count5)
print('Total % courses published enrolled >=5: ', total_course_published_enrolled_percentage5,'%' )

#print('#############################################')
##the uncorrected count for xlist published without accounting for the count of xlist enrolled
#print('courses published*: ', course_published_enrolled_count + xlist_published_sum)
#print('% courses published*: ', ((course_published_enrolled_count + xlist_published_sum)/ course_enrolled_count)*100,'%' )

#########################################################################
##################### Save to File ######################################
#########################################################################
#Save data and summary data to two different csv files
#########################################################################
filePath = 'usage_report/data_files/%s_%s_%s_%s.csv' % (termID,accountID,report_date,start)
canvasData.to_csv(filePath, sep=',')

columnNames = ['reportID', 'accountID', 'termID', 'term_name', 'sis_term_id', 'term_start_date', 'course_count', 'course_published_count', 'course_enrolled_count1', 'course_published_enrolled_count1', 'course_enrolled_count2', 'course_published_enrolled_count2', 'course_enrolled_count3', 'course_published_enrolled_count3', 'course_enrolled_count4', 'course_published_enrolled_count4', 'course_enrolled_count5', 'course_published_enrolled_count5', 'unused_published_count','unused_published_enrolled_count1', 'unused_published_enrolled_count2',  'unused_published_enrolled_count3',  'unused_published_enrolled_count4',  'unused_published_enrolled_count5', 'xlist_published_sum', 'xlist_published_enrolled_sum1', 'xlist_published_enrolled_sum2', 'xlist_published_enrolled_sum3', 'xlist_published_enrolled_sum4', 'xlist_published_enrolled_sum5', 'total_course_published_count', 'total_course_published_percentage', 'total_course_published_enrolled_count1', 'total_course_published_enrolled_percentage1', 'total_course_published_enrolled_count2', 'total_course_published_enrolled_percentage2', 'total_course_published_enrolled_count3', 'total_course_published_enrolled_percentage3', 'total_course_published_enrolled_count4', 'total_course_published_enrolled_percentage4', 'total_course_published_enrolled_count5', 'total_course_published_enrolled_percentage5', 'report_path', 'report_date', 'latest_report']
row = [int(reportID), int(accountID), int(termID), termInfo['term_name'], int(termInfo['sis_term_id']), termInfo['start_at'], course_count, course_published_count, course_enrolled_count1, course_published_enrolled_count1, course_enrolled_count2, course_published_enrolled_count2, course_enrolled_count3, course_published_enrolled_count3, course_enrolled_count4, course_published_enrolled_count4, course_enrolled_count5, course_published_enrolled_count5, unused_published_count, unused_published_enrolled_count1, unused_published_enrolled_count2, unused_published_enrolled_count3, unused_published_enrolled_count4, unused_published_enrolled_count5, xlist_published_sum, xlist_published_enrolled_sum1, xlist_published_enrolled_sum2, xlist_published_enrolled_sum3, xlist_published_enrolled_sum4, xlist_published_enrolled_sum5, total_course_published_count, total_course_published_percentage, total_course_published_enrolled_count1, total_course_published_enrolled_percentage1, total_course_published_enrolled_count2, total_course_published_enrolled_percentage2, total_course_published_enrolled_count3, total_course_published_enrolled_percentage3, total_course_published_enrolled_count4, total_course_published_enrolled_percentage4, total_course_published_enrolled_count5, total_course_published_enrolled_percentage5, filePath, report_date, 1.0]

if use_file_name:
  ufn = use_file_name.split('.')
  print(ufn)
  try:
    if ufn[1] == 'csv':
      csvFileName = 'usage_report/%s' % (use_file_name)
    else:
      use_file_name = '%s.csv' % (use_file_name)
      csvFileName = 'usage_report/%s' % (use_file_name)
  except:
      use_file_name = '%s.csv' % (use_file_name)
      csvFileName = 'usage_report/%s' % (use_file_name)
else:
  csvFileName='usage_report/canvas_usage_data.csv'
  
if not os.path.exists(csvFileName):
  with open(csvFileName, 'w') as newfile:
    writer=csv.writer(newfile, quoting=csv.QUOTE_NONNUMERIC)
    writer.writerow(columnNames)


df = pd.read_csv(csvFileName)
df.loc[df["termID"]==int(termID), "latest_report"] = 0
df.to_csv(csvFileName, quoting=csv.QUOTE_NONNUMERIC, index=False)
  
with open(csvFileName, 'a',) as f:
  writer=csv.writer(f, quoting=csv.QUOTE_NONNUMERIC)
  writer.writerow(row)
  
#with open(csvFileName, 'r') as f:
#  readCSV = csv.reader(f)
#  csvList = list(readCSV)
#  #print(csvList)
print('#############################################')
print(csvFileName,' file saved')



print('#############################################')
end = timer()
print('Total runtime:',end - start)   
print('#############################################')