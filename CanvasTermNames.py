#!/usr/bin/env python
#################################################
#Author: Matt Lewis
#Department: Instructional Technology
#Institution: Eastern Washington University
##################################################
################## DESCRIPTION ###################
##################################################
#This code is used to print out a list of term names with their Canvas id.

##################################################
################## DIRECTIONS ####################
##################################################
# DIRECTIONS: Edit the below variables to match your institution domain
domain = "canvas.[name].edu"

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

from timeit import default_timer as timer

start = timer()
callCount=0
fileCount=0
fileCountAll=0
########################################################################### 
def get_headers():
  return {'Authorization': 'Bearer %s' % token}

###########################################################################
def flattenjson( b, delim ):
    val = {}
    for i in b.keys():
      if isinstance( b[i], dict ):
        get = flattenjson( b[i], delim )
        for j in get.keys():
          val[ i + delim + j ] = get[j]
      else:
        val[i] = b[i]

    return val
###########################################################################
def confirm_token():
  url = "https://%s/api/v1/users/self/activity_stream/summary" % (domain)
  response = requests.get(url,headers=get_headers())
  if response.status_code == 200:
    confirm = True
  else:
    confirm = False
    print('The entered Canvas token did not authenticate.')
    
  return confirm

###########################################################################
def getRootID():
  url = "https://%s/api/v1/accounts?per_page=100" % (domain)
  print(url)
  response = requests.get(url,headers=get_headers())
  if not response.json():
    return "No Root"
  else:
    for s in response.json():
      if not s['root_account_id']:
        rootID = s['id']
      else:
        rootID = s['root_account_id']
  return rootID
###########################################################################
###########################################################################
def get_terms(accountID):
  termData=[]
  url = "https://%s/api/v1/accounts/%s/terms?per_page=100" % (domain, accountID)
  global callCount
  callCount += 1
  print(callCount, " url: ", url)
  response = requests.get(url,headers=get_headers())
  if not response.json():
    return "No Terms"
  else:
    json = response.json()
    #print(json['enrollment_terms'])
    for s in json['enrollment_terms']:
      termData.append({'term_id': s['id'], 'term_name': s['name']})
      
  return termData
###########################################################################

#collect Canvas token from a file titled .canvasConfig in same directory
#if not found, require manual entry of token
try:
  config = configparser.ConfigParser()
  config.read(".canvasConfig")
  token = config['configuration']['token']
except:
  print('The Canvas Config file could not be found, please enter your Canvas token.')
  token = getpass.getpass('Canvas Token:')

confirmToken = confirm_token()

if not token or confirmToken == False:
  token = getpass.getpass('Canvas Token is a required field:')
  confirmToken = confirm_token()

if not token or confirmToken == False:
    print('#########################################################################')
    print('The Canvas Token is a required field.')
    print('Exiting script.')
    print('#########################################################################')
    exit()
###########################################################################

root_account_id = getRootID()
termData = get_terms(root_account_id)
print('Term ID     NAME')
termList=[]
for t in termData:
  termList.append(t['term_id'])
  print(t['term_id'], ' - ', t['term_name'])