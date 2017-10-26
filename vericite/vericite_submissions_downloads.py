#!/usr/bin/env python
#################################################
#Author: Matt Lewis
#Department: Instructional Technology
#Institution: Eastern Washington University
##################################################
################## DESCRIPTION ###################
##################################################
#This code is used to collect the file submissions to assignments marked as using Vericite for a specific term.

##################################################
################## DIRECTIONS ####################
##################################################
# DIRECTIONS: Edit the below variables to match your institution domain and your personal token
domainBeta = "[name].beta.instructure.com"
domainProduction = "[name].instructure.com"
domainTest= "[name].test.instructure.com"

csvFileName = "Canvas-vericite_submissions"

hasData = False
collegeLevelSubAccounts=['add a list of your college level subaccount ids']
# example - collegeLevelSubAccounts=[101110, 101111, 101112, 101113, 101114, 101115]
##################################################
########## DO NOT EDIT BELOW THIS LINE ###########
##################################################


import requests
import simplejson as json
import urllib.request
#import urllib2
import argparse
import sys,os
import csv
import pprint
import os
import getpass
import configparser
import canvasConnect as canvas

from timeit import default_timer as timer

start = timer()
callCount=0
fileCount=0
fileCountAll=0
##################################################

#########################################################################
######################## Determine Domain ###############################
#########################################################################  
server = input('Which Canvas install should be used? (B=beta, P=Production, or T-test)')
if server.upper() == 'B':
  domain = domainBeta
elif server.upper() == 'P':
  domain = domainProduction
elif server.upper() == 'T':
  domain = domainTest
else:
  print('#########################################################################')
  print('No matching Canvas install was found.')
  print('Exiting script.')
  print('#########################################################################')
  exit()
  
if not domain:
    print('#########################################################################')
    print('The Canvas Domain name is a required field.')
    print('Exiting script.')
    print('#########################################################################')
    exit()

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

###########################################################################
courseFilter = input('Do you want to filter data to selected courses, If yes, enter the Course ID(s), if no, leave blank. [if multiple courses, seperate with a comma: 1234, 5678, 9012]:')
if courseFilter:
#  courseInput = input('Enter the Course ID(s) [if multiple courses, seperate with a comma: 1234, 5678, 9012]:')
  #if not courseInput:
  #    print('#########################################################################')
  #    print('The Course ID is a required field.')
  #    print('Exiting script.')
  #    print('#########################################################################')
  #    exit()
      
  print('#########################################################################')
  print(courseFilter)
  #courseList = [int(courseInput) for courseInput in input().split(",")]
  if ',' in courseFilter:
    courseNumbers = [int(courseFilter) for courseFilter in input().split(",")]
  else:
    #courseNumbers = [{'id' : int(courseFilter)} ]
    courseNumbers = [int(courseFilter) ]
  print(courseNumbers)
else:
  courseNumbers = False
  singleTerm = input('Do you want to select courses to a single term? (Y=yes, N=no):')
  displayTerm = input('Do you want to display term ids? (Y=yes, else enter the termid, or enter All to use all terms):')
  if displayTerm.upper() == 'Y':
    termData = canvas.get_terms(domain, token, root_account_id)
    print('Term ID     NAME')
    termList=[]
    for t in termData:
      termList.append(t['term_id'])
      print(t['term_id'], ' - ', t['term_name'])
      
    termID = input('Enter the Term ID:')
    
    if singleTerm.upper() == 'Y':
      termList = [termID]
  #elif not isinstance(int(displayTerm), int):
  #  if not displayTerm.upper() == 'ALL':
  #    termID = ''
  else:
    termID = displayTerm
    termList = [displayTerm]
    print(termID)
    print(termList)
  #if isinstance(termID, int) == False:
  #    termID = ''
      
  if not termID:
      print('#########################################################################')
      print('The Term is a required field.')
      print('Exiting script.')
      print('#########################################################################')
      exit()
  accountFilter = input('Do you want to filter data to selected sub-account (Y=yes, N=no):')
  if accountFilter.upper() == 'Y':
    account_id = input('Enter the account id:')
    if not account_id:
      account_id = root_account_id
    collegeSubAccounts = [account_id]
  else:
    account_id = root_account_id
    #
    #collegeSubAccounts=[102894, 102895, 102896, 102897, 102898, 103422]
    collegeSubAccounts=collegeLevelSubAccounts
      
  #print('#########################################################################')
  #courseList = get_courses(account_id, termID)
  #print('Count of rows in courseList:',len(courseList))
  #enrollmentList = get_enrollments(courseList, "", "TeacherEnrollment")
  #print('Count of rows in enrollmentList:',len(enrollmentList))
  

if courseNumbers:
  courseList=[]
  for i in courseNumbers:
    #submissionsFolder = 'submissions_course'+ str(i)
    directory = "vericite/vericite_submissions"
    if not os.path.exists(directory):
      os.makedirs(directory)
    submissionsFolder = directory +'/Vsubmissions_course'+ str(i)
    courseList = canvas.get_course_data(False,i, courseList, False)
  csvFileName = csvFileName + '_course'
  print('Count of rows in courseList:',len(courseList))
  print('#########################################################################')
  #keys = courseList[0].keys()
  #with open('courseList.csv', 'w', newline='') as fp:
  #    a = csv.DictWriter(fp, keys)
  #    a.writeheader()
  #    a.writerows(courseList)
  #print('courseList.csv file complete')
  end = timer()
  seconds = end - start
  m, s = divmod(seconds, 60)
  h, m = divmod(m, 60)
  runtime = 'runtime: %d h :%d m :%d s' % (h, m, s)
  print (runtime)
  print('#########################################################################')
  if len(courseList) > 0:
    assignmentList = canvas.get_vericite_assignments(domain, token, courseList, submissionsFolder)
    print('#########################################################################')
    #print(courseList)
    print('Count of rows in assignmentList:',len(assignmentList))
    end = timer()
    print('runtime:',end - start)  
    print('#########################################################################')
    print('#########################################################################')
    if len(assignmentList) > 0:
      hasData = True
      turnitinList = assignmentList
else:
  for t in termList:
    termID = t
    #submissionsFolder = 'submissions_term'+ str(termID)
    directory = "vericite/vericite_submissions"
    if not os.path.exists(directory):
      os.makedirs(directory)
    submissionsFolder = directory +'/Vsubmissions_term'+ str(termID)
    csvFileName = csvFileName + '_' + str(termID)
    for subaccount in collegeSubAccounts:
      account_id = subaccount
      csvFileName = csvFileName + '_' + str(account_id)
      print('#########################################################################')
      print('#########################################################################')
      print('#########################################################################')
      print('sub-account: ', account_id)
      print('#########################################################################')
      courseList = canvas.get_courses(domain, token, account_id, termID, 0)
      print('Count of rows in courseList:',len(courseList))
      print('#########################################################################')
      #keys = courseList[0].keys()
      #with open('courseList.csv', 'w', newline='') as fp:
      #    a = csv.DictWriter(fp, keys)
      #    a.writeheader()
      #    a.writerows(courseList)
      #print('courseList.csv file complete')
      end = timer()
      seconds = end - start
      m, s = divmod(seconds, 60)
      h, m = divmod(m, 60)
      runtime = 'runtime: %d h :%d m :%d s' % (h, m, s)
      print (runtime)
      print('#########################################################################')
      if len(courseList) > 0:
        assignmentList = canvas.get_vericite_assignments(domain, token, courseList, submissionsFolder)
        print('#########################################################################')
        #print(courseList)
        print('Count of rows in assignmentList:',len(assignmentList))
        end = timer()
        seconds = end - start
        m, s = divmod(seconds, 60)
        h, m = divmod(m, 60)
        runtime = 'runtime: %d h :%d m :%d s' % (h, m, s)
        print (runtime)
        print('Total Files Downloaded: ', fileCount)
        print('#########################################################################')
        print('#########################################################################')
        if len(assignmentList) > 0:
          hasData = True
          turnitinList = assignmentList
          
if hasData:
  #create the csv file
  keys = turnitinList[0].keys()
  #print('keys:', keys)
  
  csvFileName = csvFileName + '_' + str(start) + '.csv'
  #csvFileName = csvFileName + '_quiz_data.csv'
  print(csvFileName,'.csv file save started')
  
  with open(csvFileName, 'w', newline='') as fp:
      a = csv.DictWriter(fp, keys)
      a.writeheader()
      a.writerows(turnitinList)
  print(csvFileName,'.csv file complete')
  print('#########################################################################')
else:
  hasData = False
  
end = timer()

seconds = end - start
m, s = divmod(seconds, 60)
h, m = divmod(m, 60)
runtime = 'runtime: %d h :%d m :%d s' % (h, m, s)
print (runtime)