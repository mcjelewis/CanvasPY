#################################################
#Author: Matt Lewis
#Department: Instructional Technology
#Institution: Eastern Washington University
##################################################
from .api_core import *
import requests
import simplejson as json
###########################################################################   
############################ Grading - Assignments ####################################
###########################################################################
def getRootOutcomeGroup(apiType):  
  headers = {'Authorization':'Bearer %s'%token,'Content-Type':'application/json'}
  url = "https://%s/api/v1/%s/root_outcome_group" % (domain,apiType)
  return requests.get(url,headers=get_headers(),verify=False).json()

###########################################################################
def getOutcome_groups(apiType):
  # Get outcome subgroups (this needs to walk)
  groupOutcomeList = []
  all_done = False
  url = 'https://%s/api/v1/%s/outcome_groups?per_page=100' % (domain,apiType)
  while not all_done:
    response = requests.get(url,headers=get_headers())
    if not response.json():
      #yield []
      return
    else:
      for s in response.json():
        groupOutcomeList.append(s)
    if 'next' in response.links:
      url = response.links['next']['url']
    else:
      all_done = True
    return groupOutcomeList
###########################################################################
def getOutcomes(apiType):
  outcomeList = []
  all_done = False
  url = 'https://%s/api/v1/%s/outcome_group_links?per_page=100' % (domain,apiType)
  print(url)
  while not all_done:
    response = requests.get(url,headers=get_headers())
    #print(response.json())
    if not response.json():
      #yield []
      return
    else:
      for s in response.json():
        #t = flattenjson(s, "__")
        outcomeList.append(s)
    if 'next' in response.links:
      url = response.links['next']['url']
    else:
      all_done = True
    #print(outcomeList)
    return outcomeList

###########################################################################
def findOutcomeID(outcome_title, outcomeList):
    outcomeFound=""
    outcomeFound = {'outcomeID': 0, 'outcomeGroupID': 0, 'url': ''}
    if outcomeList:
      for outcome in outcomeList:
        print(outcome_title, " : ", outcome['outcome']['title'])
        if outcome_title == outcome['outcome']['title']:
          outcomeFound = {'outcomeID': outcome['outcome']['id'], 'outcomeGroupID': outcome['outcome_group']['id'], 'url': outcome['outcome']['url']}
    return outcomeFound

###########################################################################
def findGroup(outcome_group_id, outcomeGroupList):
  foundGroup = False
  if not outcome_group_id:
    for group in outcomeGroupList:
      if outcome_group_id == group['id']:
        foundGroup = True
  return foundGroup
  
###########################################################################
def findGroupID(outcome_group, outcomeGroupList):
    groupID = ""
    for group in outcomeGroupList:
      if outcome_group == group['title']:
        groupID = group['id']
    return groupID
###########################################################################
def addGroup(title, parent_id, apiType):
    headers = {'Authorization':'Bearer %s'%token,'Content-Type':'application/json'}
    vendor_guid = title
    if not parent_id:
      parent_id = rootOutcomeGroup['id']
    
    url = 'https://%s/api/v1/%s/outcome_groups/%d/subgroups' % (domain,apiType,parent_id)
    params = {'title':title,'description': '','vendor_guid':vendor_guid, 'parent_outcome_group_id': parent_id}
    r=requests.post(url,data=json.dumps(params),headers=headers)
    return r
###########################################################################
def enterOutcome(outcome, url, callType):
    headers = {'Authorization':'Bearer %s'%token,'Content-Type':'application/json'}
    title = outcome['title']
    description = outcome['description']
    mastery_points = outcome['mastery_points']
    ratings = outcome['ratings']
    calculation_method = outcome['calculation_method']
    vendor_guid = outcome['title']
    if calculation_method == 'decaying_average' or calculation_method == 'n_mastery' :
      calculation_int = outcome['calculation_int']
      params = {'title':title,'description':description,'mastery_points': mastery_points,'ratings':ratings, 'calculation_method': calculation_method, 'calculation_int': calculation_int,'vendor_guid': vendor_guid}
    else:
      params = {'title':title,'description':description,'mastery_points': mastery_points,'ratings':ratings, 'calculation_method': calculation_method, 'vendor_guid': vendor_guid}
    if callType == 'post':
      r=requests.post(url,data=json.dumps(params),headers=headers)
    elif callType == 'put':
      r=requests.put(url,data=json.dumps(params),headers=headers)
      
    return r.status_code
