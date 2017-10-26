#################################################
#Author: Matt Lewis
#Department: Instructional Technology
#Institution: Eastern Washington University
##################################################
from .api_core import *
import requests
import simplejson as json

###########################################################################   
################################ Outcomes #################################
###########################################################################
def getRootOutcomeGroup(domain, token, apiType):  
  headers = {'Authorization':'Bearer %s'%token,'Content-Type':'application/json'}
  url = "https://%s/api/v1/%s/root_outcome_group" % (domain,apiType)
  return requests.get(url,headers=get_headers(token),verify=False).json()

###########################################################################
def getOutcome_groups(domain, token, apiType):
  # Get outcome subgroups (this needs to walk)
  groupOutcomeList = []
  all_done = False
  url = 'https://%s/api/v1/%s/outcome_groups?per_page=100' % (domain,apiType)
  while not all_done:
    response = requests.get(url,headers=get_headers(token))
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
def getOutcomes(domain, token, apiType):
  outcomeList = []
  all_done = False
  url = 'https://%s/api/v1/%s/outcome_group_links?per_page=100' % (domain,apiType)
  #print(url)
  while not all_done:
    response = requests.get(url,headers=get_headers(token))
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
        #print(outcome_title, " : ", outcome['outcome']['title'])
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
def addGroup(domain, token, title, parent_id, apiType):
    headers = {'Authorization':'Bearer %s'%token,'Content-Type':'application/json'}
    vendor_guid = title
    if not parent_id:
      parent_id = rootOutcomeGroup['id']
    
    url = 'https://%s/api/v1/%s/outcome_groups/%d/subgroups' % (domain,apiType,parent_id)
    params = {'title':title,'description': '','vendor_guid':vendor_guid, 'parent_outcome_group_id': parent_id}
    r=requests.post(url,data=json.dumps(params),headers=headers)
    return r
###########################################################################
def enterOutcome(domain, token, outcome, url, callType):
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
###########################################################################
def update_outcome(domain, token, outcomeID, title, description):
    url = 'https://%s/api/v1/outcomes/%s' % (domain, outcomeID)
    
    outcomeParams = {'title':title,'description':description,'mastery_points':3}
    #outcomeParams = {"title": "v2 Dept Outcome42","display_name": "v2 Dept Outcome42", "description": "this is an outcome", "vendor_guid": 99, "mastery_points": 2}
    #outcomeParams = {'title':title,'description':description,'mastery_points': mastery_points,'ratings':ratings, 'calculation_method': calculation_method, 'calculation_int': calculation_int,'vendor_guid': vendor_guid}

    outcomeParams = {key: value for key, value in outcomeParams.items() if value != ""}
    
    r=requests.put(url,params=outcomeParams,headers=get_headers(token))
      
    return r.status_code
  ###########################################################################
def get_outcome(domain, token, outcomeID):
  outcomeList = []
  all_done = False
  url = 'https://%s/api/v1/outcomes/%s' % (domain, outcomeID)
  #print(url)
  while not all_done:
    response = requests.get(url,headers=get_headers(token))
    s = response.json()
    #print(s['id'])
    if not response.json():
      all_done = True
    else:
      outcomeList.append({'outcome_id': s['id'], 'context_id': s['context_id'],  'context_type': s['context_type'], 'vendor_guid': s['vendor_guid'], 'display_name': s['display_name'], 'title': s['title'], 'url': s['url'], 'can_edit': s['can_edit'], 'description': s['description'], 'calculation_method': s['calculation_method'], 'calculaation_int': s['calculation_int'], 'point_possible': s['points_possible'], 'mastery_points': s['mastery_points'], 'ratings': s['ratings'], 'assessed': s['assessed']})

    if 'next' in response.links:
      url = response.links['next']['url']
    else:
      all_done = True
    #print(outcomeList)
    return outcomeList

###########################################################################
#title,description,mastery_points,ratings,calculation_method,calculation_int,vendor_guid
     
###########################################################################