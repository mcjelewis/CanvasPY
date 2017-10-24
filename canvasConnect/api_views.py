#################################################
#Author: Matt Lewis
#Department: Instructional Technology
#Institution: Eastern Washington University
##################################################
from .api_core import *
import requests
import simplejson as json
###########################################################################   
############################ Page Views ####################################
########################################################################### 
def get_views(domain, token, userList, userID, recordCount, start_date, end_date):
  viewsData=[]
  userListNew = []
  useDate = False
  pageViews_dates = ""
  
  try:
    for i in userList:
      userListNew.append(i['user_id'])
    userListClean = list(set(userListNew))
    userLen = len(userListClean)
    userCountText = "%s users..." % (userLen)
  except:
    userCountText = "1 user..."
    
  if start_date != "":
    pageViews_dates += '&start_time=%s' % start_date
    useDate = True
  else:
    pageViews_dates += ""
    
  if end_date != "":
    pageViews_dates += '&end_time=%s' % end_date
    useDate = True
  else:
    pageViews_dates += ""
  
  if useDate:
    pageCount = 1
    print('Returning records by start date: ', start_date,' and/or end date: ', end_date,' for ', userCountText)
    if userID:
      url = "https://%s/api/v1/users/%s/page_views?per_page=100%s" % (domain, userID, pageViews_dates )
      print(url)
      viewsData = collectViewByDate(url, token, viewsData, pageCount)
    else:
      for i in userListClean:
        userID=i
        url = "https://%s/api/v1/users/%s/page_views?per_page=100%s" % (domain, userID, pageViews_dates )
        viewsData = collectViewByDate(url, token, viewsData, pageCount)
  else:
    print('Returning ', recordCount, 'records for each of the ', userCountText)
    try:
      recordCount = int(recordCount)
    except ValueError:
      recordCount=100
    totalPages = recordCount//100
    #print(totalPages)
    if userID:
      pageCount = 1
      url = "https://%s/api/v1/users/%s/page_views?per_page=100" % (domain, userID)
      viewsData = collectViewByCount(url, token, totalPages, pageCount, userID, viewsData)
    else:
      for i in userListClean:
        pageCount = 1
        userID=i
        url = "https://%s/api/v1/users/%s/page_views?per_page=100" % (domain, userID)
        viewsData = collectViewByCount(url, token, totalPages, pageCount, userID, viewsData)
        
  return viewsData
###########################################################################
def collectViewByCount(url, token, totalPages, pageCount, userID, viewsData):
  while (pageCount <= totalPages):
    #print(pageCount)
    response = requests.get(url,headers=get_headers(token))
    if not response.json():
      print("End of Page Views reached at page ", pageCount," for: ",userID)
    else:
      json = response.json()
      #print(json['enrollment_terms'])
      for s in response.json():
        page_views = flattenjson(s, "__")
        viewsData.append(page_views)
    if 'next' in response.links:
      url = response.links['next']['url']
    pageCount = pageCount + 1
  return viewsData  
###########################################################################
def collectViewByDate(url, token, viewsData, pageCount):
  all_done = False
  while not all_done:
    #print(url)
    if pageCount % 5 == 0:
      numRecord = pageCount * 100
      print('Collecting record number ',numRecord,'...')
    response = requests.get(url,headers=get_headers(token))
    if not response.json():
      all_done = True
    else:
      json = response.json()
      #print(json['enrollment_terms'])
      for s in response.json():
        page_views = flattenjson(s, "__")
        viewsData.append(page_views)
    if 'next' in response.links:
      url = response.links['next']['url']
    else:
      all_done = True
    pageCount = pageCount + 1
  return viewsData             
###########################################################################        
def courseFilter(x, course_id):
  try:
    #return x['context_type'] == 'Course'
    #x['context_type'] == 'Course'
    #x['links__context'] == course_id
    return 'courses/'+ course_id in x['url'] 
    #return 'courses/834960' in x['url']
  except (KeyError, TypeError):
    return False

