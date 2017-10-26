#!/usr/bin/env python
#################################################
#Author: Matt Lewis
#Department: Instructional Technology
#Institution: Eastern Washington University
##################################################
################## DESCRIPTION ###################
##################################################
#This code was used to collect the file submissions to assignments marked as using Turnitin for a specific term.
#Note that the Turnitin plugin must be made available to your account otherwise the turnitin data is hidden and is not shown in the API calls.

#This was a one off project, so once I got what I needed, I stopped working on it.  My apologies for not
#commenting the code better. It also, I'm sure, is not the most efficient script and takes a while to run.
#But we got what we needed to migrate past assignment submissions.

#When this script runs:
#1. It will first ask for your Canvas Token ID.
#2. Next it will ask to enter the domain used for your Canvas instance.
#3. Next it will ask if you want to collect submissions from a specific course (good for testing)
#4. If question 3 is left blank, it will then ask if you'd like to display term ids (helpful if you don't know which term you want to run)
#5. If question 4 is yes, it will display a list of term names and id numbers for reference.
#6. Next it will ask you to 'Enter the Term ID'
#7. Next it will ask if you want to filter to a select sub-account
#8. The script then makes Canvas API calls and steps through all the courses in the term and all the assignments, identifies the assignments marked
#as Turnitin, then downloads all the submitted files of the right file type for that assignment.

#list of file types downloaded: "doc", "docx", "pdf", "rtf", "txt", "ps", "wp", "odt", "ods", "odp"
##################################################
################## DIRECTIONS ####################
##################################################
# DIRECTIONS: Edit the below variables to match your institution domain
domainBeta = "[name].beta.instructure.com"
domainProduction = "[name].instructure.com"
domainTest= "[name].test.instructure.com"

csvFileName = "Canvas-turnitin_submissions"
#add your folder path here for where you'd like the files saved: in addition, add a folder titled 'submissions'.
#Below is an example of my folder structure.
#folderPath1 = "/Canvas-python/turnitin/submissions/"
folderPath1 = ""

#It was simpler to just hard set the sub account id numbers than to create a function to grab them. Edit below to match your subaccount id numbers
collegeLevelSubAccounts=[100101, 100102, 100103, 100104, 100105]
##################################################
########## DO NOT EDIT BELOW THIS LINE ###########
##################################################
hasData = False

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

courseFilter = input('Do you want to filter data to selected courses, If yes, enter the Course ID(s) [if multiple courses, seperate with a comma: 1234, 5678, 9012], otherwise leave blank:')
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
  displayTerm = input('Do you want to display term ids? (Y=yes, else enter the termid, or enter All to use all terms):')
  #if displayTerm.upper() == 'Y':
  termData = canvas.get_terms(domain, token, root_account_id)
  if displayTerm.upper() == 'Y':
    print('Term ID     NAME')
  termList=[]
  for t in termData:
    termList.append(t['term_id'])
    if displayTerm.upper() == 'Y':
      print(t['term_id'], ' - ', t['term_name'])
  if displayTerm.upper() != 'ALL':
    if displayTerm.upper() == 'Y':
      termID = input('Enter the Term ID:')
      termList = [termID]
    else:
      termID = displayTerm
      termList = [displayTerm]
    

      
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
    directory = "turnitin/turnitin_submissions"
    if not os.path.exists(directory):
      os.makedirs(directory)
    submissionsFolder = directory +'/Tsubmissions_course'+ str(i)
    courseList = canvas.get_course_data(domain, token, False,i, courseList, False)
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
    assignmentList = canvas.get_turnitin_assignments(domain, token, courseList)
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
    directory = "turnitin/turnitin_submissions"
    if not os.path.exists(directory):
      os.makedirs(directory)
    submissionsFolder = directory +'/Tsubmissions_term'+ str(termID)
    csvFileName = csvFileName + '_' + str(termID)
    for subaccount in collegeSubAccounts:
      account_id = subaccount
      csvFileName = csvFileName + '_' + str(account_id)
      print('#########################################################################')
      print('#########################################################################')
      print('#########################################################################')
      print('sub-account: ', account_id)
      print('#########################################################################')
      courseList = canvas.get_courses(domain, token, account_id, termID)
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
        assignmentList = canvas.get_turnitin_assignments(domain, token, courseList)
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