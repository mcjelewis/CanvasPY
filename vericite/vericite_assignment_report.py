#!/usr/bin/env python
#################################################
#Author: Matt Lewis
#Department: Instructional Technology
#Institution: Eastern Washington University
##################################################
################## DESCRIPTION ###################
##################################################
#This code is used to collect information Vericite.

##################################################
################## DIRECTIONS ####################
##################################################
# DIRECTIONS: Edit the below variables to match your institution domain and your personal token
domainBeta = "[name].beta.instructure.com"
domainProduction = "[name].instructure.com"
domainTest= "[name].test.instructure.com"
domain=""

csvFileName = "Canvas-assignments"
##################################################
########## DO NOT EDIT BELOW THIS LINE ###########
##################################################


import requests
import json
import argparse
import sys,os
import csv
import pprint
import getpass
import configparser
import canvasConnect as canvas
from timeit import default_timer as timer

start = timer()
callCount=0
fileCount=0
fileCountAll=0

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
  
 
#########################################################################   
termList = canvas.get_terms(domain, token, root_account_id)
print('Term ID     NAME')
for t in termList:
  print(t['term_id'], ' - ', t['term_name'])

#termID=3838 #Group Term
termID = input('Enter the Term ID:')
if not termID:
    print('#########################################################################')
    print('The Term is a required field.')
    print('Exiting script.')
    print('#########################################################################')
    exit()
    
print('#########################################################################')
courseList = canvas.get_courses(domain, token, root_account_id, termID, 0)
print('#########################################################################')
#print(courseList)
print('Count of rows in courseList:',len(courseList))

#keys = courseList[0].keys()
#with open('courseList.csv', 'w', newline='') as fp:
#    a = csv.DictWriter(fp, keys)
#    a.writeheader()
#    a.writerows(courseList)
#print('courseList.csv file complete')
end = timer()
print('runtime:',end - start)


print('#########################################################################')

assignmentList = canvas.get_vericite_assignments(domain, token, courseList, None)
print('#########################################################################')
#print(courseList)
print('Count of Vericite assignments:',len(assignmentList))
end = timer()
print('runtime:',end - start)  
print('#########################################################################')
print('#########################################################################')
#create the csv file
keys = assignmentList[0].keys()
print('keys:', keys)

csvFileName = csvFileName + '_' + str(start) + '.csv'
with open(csvFileName, 'w', newline='') as fp:
    a = csv.DictWriter(fp, keys)
    a.writeheader()
    a.writerows(assignmentList)
print(csvFileName,'.csv file complete')
print('#########################################################################')

end = timer()
print('runtime:',end - start)   