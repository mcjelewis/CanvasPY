#################################################
#Author: Matt Lewis
#Department: Instructional Technology
#Institution: Eastern Washington University
##################################################
from .api_core import *
import requests
import simplejson as json
###########################################################################   
########################### Enrollments ###################################
########################################################################### 
def get_enrollments(domain, token, courseList, courseID, roleType):
  global callCount
  addRoles=""
  for role in roleType:
    addRoles += "&type[]=%s" % (role.strip())
  enrollmentsList = []
  all_done = False
  if courseID:
      url = "https://%s/api/v1/courses/%s/enrollments?per_page=100%s" % (domain, courseID, addRoles)
      while not all_done:
        #callCount += 1
        #print(callCount, " url: ", url)
        print(url)
        response = requests.get(url,headers=get_headers(token))
        if not response.json():
          all_done = True
        else:
          for s in response.json():
            enrollments = flattenjson(s, "__")
            enrollmentsList.append(enrollments)
            #print(s)
            #enrollmentsList.append(s)
        if 'next' in response.links:
            url = response.links['next']['url']
            print(url)
        else:
            all_done = True
  else:
    for i in courseList:
      courseID=i['id']
      url = "https://%s/api/v1/courses/%s/enrollments?per_page=100&type[]=%s" % (domain, courseID, roleType)
      while not all_done:
        #callCount += 1
        #print(callCount, " url: ", url)
        response = requests.get(url,headers=get_headers(token))
        if not response.json():
          all_done = True
        else:
          for s in response.json():
            enrollments = flattenjson(s, "__")
            enrollmentsList.append(enrollments)
            #print(s)
            #enrollmentsList.append(s)
        if 'next' in response.links:
            url = response.links['next']['url']
        else:
            all_done = True
      
  return enrollmentsList 

###########################################################################