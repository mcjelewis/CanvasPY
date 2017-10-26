#!/usr/bin/env python
#################################################
#Author: Matt Lewis
#Department: Instructional Technology
#Institution: Eastern Washington University
##################################################
################## DESCRIPTION ###################
##################################################
#This code is used to upload new outcomes into Canvas at an account level. Data from an uploaded csv file is used to add a new outcome group if needed, as well
#as update or add the settings for an outcome. Only one rating scale can be used for each file being uploaded.

#This is a heavily modified version of kajiagga' outcome importer (https://github.com/kajigga/canvas-contrib/tree/master/API_Examples/import_outcomes/python).
#kept the access to csv files through kajiagga's functions, rewrote most of the logic on process for searching, adding, updating outcomes
#modifided the kajiagga csv file: added columns for account_id and outcome group vendor, renamed other fields and removed parent_id field

##################################################
################### CSV FILE #####################
##################################################
#You will need to format a csv file with the required headers.
#Required Header Field Names:'account_id','parent_directory','title','description','calculation_method','calculation_int','mastery_points'
# 'account_id': Enter the account id for where the outcome will reside if in a department or college.  Leave empty if adding outcomes to a course. Course ID can be entered when executing the script.
# 'parent_directory': Directory structure of where the outcome will reside within the account. Canvas allows for the creation of folders (Canvas calls them groups).
#   Limitation: While Canvas will allow for the same name to be used for multiple folders, this script does not. When creating the folder structure use a different title for each folder (group).
# 'title': Title of the outcome
# 'description': Description of the outcome
# 'calculation_method': Canvas allows the options; decaying_average, n_mastery, highest, lowest
# 'calculation_int': If method is decaying_average or n_mastery, the calculation integer should be set
# 'mastery_points': The value marking mastery of the outcome
# At the end of the header row add the rating scale title that will be used for this set of outcomes. For example, 'Exceeds Expectations', 'Mets Expectations', 'Does Not Met Expectations' each as a column title
#   The point values for each rating are place in the data row under each outcome scale title.

#Notes:
#1. For each csv file, only one rating scale can be used.
#2. Limitation on folder (group) titles; cannot use same title for multiple folders. Outcome will be placed in the first folder (group) found.

##################################################
################## DIRECTIONS ####################
##################################################
# DIRECTIONS: Edit the below domain variables to match your institution Canvas domain
domainBeta = "[name].beta.instructure.com"
domainProduction = "[name].instructure.com"
domainTest= "[name].test.instructure.com"

##################################################
#################### Example #####################
##################################################
#Example of python call:
#>>> cd [path to outcome script]
#>>> python outcomes/outcome_importer.py --outcomesfile Outcome_Import_Example.csv
#Note you will need to edit the account_id field in the example csv file

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



##################################################

###########################################################################   
############################ File Arguments ###############################
###########################################################################  
# Prepare argument parsing
parser = argparse.ArgumentParser()
parser.add_argument('--outcomesfile',required=True,help='path to the outcomes.csv file')

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


###########################################################################  
level = input('Are these course or account level outcomes? (A=account,C=course)')
course_id = ''
if level.upper() == 'C':
  course_id = input('Enter Canvas Course ID (required field):')
  if not course_id:
    course_id = input('Canvas Course ID is a required field:')



#Start the timer used to determine how long it took to run the script
start = timer()
groupID = 0
parentGroupID=0
#mark where in the csv file the rating scale column starts
rating_column=7
if __name__ == '__main__':
    args = parser.parse_args()
    currentFile = __file__  # May be 'my_script', or './my_script' or
                        # '/home/user/test/my_script.py' depending on exactly how
                        # the script was run/loaded.
    realPath = os.path.realpath(currentFile)  # /home/user/test/my_script.py
    dirPath = os.path.dirname(realPath)  # /home/user/test
    dirName = os.path.basename(dirPath) # test
    file_name = args.outcomesfile
    file_path = dirPath + "/" + file_name
    outcomes_file = canvas.checkFileReturnCSVReader(file_path)
    print(outcomes_file)
    if outcomes_file :
      outcomes = {}
      outcome_data = {}
      for outcome_row in outcomes_file:
        if outcome_row[0]=="account_id":
          # add the rating scale titles from the csv header row into a rating_levels array
          outcome_data['rating_levels'] = outcome_row[rating_column:]
        else:
          #set field names array - matching csv header row up to ratings
          fields = ['account_id','parent_directory','title','description','calculation_method','calculation_int','mastery_points']
          
          #collect from csv header the outcome rating names
          #collect from row the value for those rating names
          #combine names and values into an array with the necissary Canvas titles (description, points), and add list to outcome array
          outcome = dict(zip(fields,outcome_row[:rating_column]))
          outcome.update({'ratings': list()})
          combo = dict(zip(outcome_data.get('rating_levels'),outcome_row[rating_column:]))
          outcome['ratings']=[]
          for key in combo:
            outcome['ratings'].append({'description': key, 'points': combo[key]})
          
          #Since this script can be used to add outcomes into the course as well as at the account level,
          #set the api type for use within the url of the api call.
          if level.upper() == 'A':
            if not outcome['account_id']:
              print('###########################  ERROR  ####################################')
              print('An account id is requried in the csv file for each outcome if not entering into a course.')
              print('The outcome ', outcome['title'], ' was not added.')
              print('#########################################################################')
              break
            else:
              apiType = 'accounts/' + outcome['account_id']
          else:
            if not course_id:
              print('###########################  ERROR  ####################################')
              print('A course id is requried in the csv file for each outcome if not entering into an account.')
              print('The outcome ', outcome['title'], ' was not added.')
              print('#########################################################################')
              break
            else:
              apiType = 'courses/' + course_id
            
          #set the root group id
          rootOutcomeGroup = canvas.getRootOutcomeGroup(domain, token, apiType)
          
          #create a full list of outcome groups in account
          outcomeGroupList = canvas.getOutcome_groups(domain, token, apiType)
          
          #create a full list of outcomes in account
          outcomeList = canvas.getOutcomes(domain, token, apiType)
          
          #find outcomeID if created
          foundOutcome = canvas.findOutcomeID(outcome['title'], outcomeList)
          #print(outcomeGroupList)
          
          
          #find account's parent outcome. The outcome will be the only one without the content for 'parent_outcome_group', it is the original outcome to the account.
          #the parentGroupID is needed to help determine placement when adding new outcome group folders.
          for group in outcomeGroupList:
            #if parentGroupID ==0:
              if 'parent_outcome_group' not in group:
                parentGroupID= group['id']
          
          #Split the directory field coming from csv file and add new groups if not found in list
          parentList = outcome['parent_directory'].split(";")
          foundGroup = False
          for x in parentList:
            for group in outcomeGroupList:
              if group['title'] == x:
                #print('parentGroupID:',parentGroupID, ' parent_outcome_group:',group['parent_outcome_group']['id'])
                #This if statement was used to be able to add multiple folder/groups with the same title.
                #However, until there is a way of retrieving the id of a folder/group after creating it,
                # an outcome will only be entered into the first found instance of the folder/group title.
                if group['parent_outcome_group']['id'] == parentGroupID:
                  parentGroupID = group['id']
                  groupID = group['id']
                  foundGroup = True
                # Until that time, limit the number of named folder/groups to a single instance of the name.
                #parentGroupID = group['id']
                #groupID = group['id']
                #foundGroup = True
                break
              else:
                foundGroup = False
            
            if foundGroup == False:
              r = canvas.addGroup(domain, token, x,parentGroupID,apiType)
              #Grab the ID for the newly created group
              response = r.json()
              groupID = response['id'];
              parentGroupID = groupID
              print('#########################################################################')
              print('Added Folder:',x,' - ', parentGroupID)
            print('#########################################################################')
            
            #print('Title:', group['title'],'foundGroup:', foundGroup, 'groupID:',groupID,' parentID ', parentGroupID)
            #print(foundOutcome['outcomeGroupID'])
            #print(outcome)
          #if the groupID coming from a previously created outcome does not match the groupID,
          #then it is a new outcome in a different folder. If id does match then this is an update to a previously created outcome.

            
          if foundOutcome['outcomeGroupID'] != groupID:
            url = 'https://%s/api/v1/%s/outcome_groups/%s/outcomes' % (domain,apiType,groupID)
            
            #create outcome 
            outcomeStatus = canvas.enterOutcome(domain, token, outcome, url, 'post')
            
            print('#########################################################################')
            if outcomeStatus == 200:
              print('Created outcome:',outcome['title'])
              print(url)
            else:
              print('Error', outcomeStatus, 'occured on the creation of the Outcome:', outcome['title'],' ',outcome['description'])
              print(url)
          
          else:
            url = 'https://%s/api/v1/outcomes/%s' % (domain,foundOutcome['outcomeID'])
            #update outcome 
            outcomeStatus = canvas.enterOutcome(domain, token, outcome, url, 'put')
          
            print('#########################################################################')
            if outcomeStatus == 200:
              print('Edited outcome:',outcome['title'])
            else:
              print('Error', outcomeStatus, 'occured on the creation of the Outcome:', outcome['title'],' ',outcome['description'])

          print('#########################################################################')
    else:
      print('problem with finding the file')
print('#########################################################################')

end = timer()
secondsRun = end - start
minutesRun =secondsRun/60
print('runtime minutes:',minutesRun)   