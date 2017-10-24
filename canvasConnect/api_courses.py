#################################################
#Author: Matt Lewis
#Department: Instructional Technology
#Institution: Eastern Washington University
##################################################
from .api_core import *
import requests
import simplejson as json
###########################################################################   
############################ Courses ####################################
########################################################################### 
def courses_id(domain, token, accountList, termID):
  courseIDList=[]
  courseCount = 1
  pCount=10
  print('Depending on the number of courses in this term, this could take a little while.')
  for i in accountList:
    all_done = False
    courseIDList = paginated_courses_id(domain, token,'', i['account_id'], courseIDList, termID,  all_done, 1, 10)

  return courseIDList 

###########################################################################
def paginated_courses_id(domain, token, url, accountid, courseIDList, termID, all_done, courseCount, pCount):
  if not url:
    url = 'https://%s/api/v1/accounts/%s/courses?per_page=100&include[]=term&enrollment_term_id=%s' % (domain,accountid,termID)
  while not all_done:
    response = requests.get(url,headers=get_headers(token))
    print(response.links)
    if response.status_code == 200:
      print(response.links)
      
      if not response.json():
        exit
      else:
        for s in response.json():
          if courseCount > pCount:
            print('Please be patient. Processing accountID: ', accountid, '  course count: ', courseCount)
            print(url)
            pCount+=100
          courseCount+= 1
          courseIDList.append({'course_id': s['id'], 'course_name': s['name'],  'term_id': s['term']['id'], 'term_name': s['term']['name']})

      if 'next' in response.links:
        print(response.links)
        url = response.links['next']['url']
        paginated_courses_id(domain, token,url, accountid, courseIDList, '', False, courseCount, pCount)
      else:
          all_done = True
    else:
      print('#########################################################################')
      print(url)
      print('Returned error code: ', response.status_code)
      print('#########################################################################')
  return courseIDList 

###########################################################################
def get_courses(domain, token, account_id, termID, callCount):
  courseList=[]
  all_done = False
  #print('account_id:', account_id)
  paginated_account_courses(domain, token,'', account_id, termID, courseList, all_done, callCount)
    
  return courseList
###########################################################################
def paginated_account_courses(domain, token, url, account_id, termID, courseList, all_done, callCount):
  if callCount == "":
    callCount = 0
  course_count=0
  if not url:
    url = 'https://%s/api/v1/accounts/%s/courses?include[]=storage_quota_used_mb&include[]=term&include[]=total_students&include[]=sections&with_enrollments=true&enrollment_term_id=%s&per_page=100' % (domain, account_id,termID)
  #print('course:', url)
  while not all_done:
    callCount += 1
    #print(callCount, " url: ", url)
    response = requests.get(url,headers=get_headers(token))
    if not response.json():
      url = ''
      all_done = True
    else:
      for s in response.json():
        course = flattenjson(s, "__")
        if not 'course_format' in s:
          course.update({'course_format': ""})
        #print('id:', s['id'])
        course_count += 1
        courseList.append(course)
        
      if 'next' in response.links:
        url = response.links['next']['url']
        paginated_account_courses(domain, token,url, account_id, termID, courseList, True, callCount)
      else:
        url = ''
        all_done = True
  return courseList 
###########################################################################
def get_course_data(domain, token, url, courseID, courseList, all_done):
  global callCount
  course_count=0

  if not url:
    url = 'https://%s/api/v1/courses/%s?include[]=storage_quota_used_mb&include[]=term&include[]=total_students&include[]=sections&with_enrollments=true&per_page=100' % (domain, courseID)
  #print('course:', url)
  while not all_done:
    callCount += 1
    print(callCount, " url: ", url)
    response = requests.get(url,headers=get_headers(token))
    if not response.json():
      url = ''
      all_done = True
    else:
      s = response.json()
      #for s in response.json():
      #print(s)
      course = flattenjson(s, "__")
      if not 'course_format' in s:
        course.update({'course_format': ""})
      #print('id:', s['id'])
      course_count += 1
      courseList.append(course)
        
      if 'next' in response.links:
        url = response.links['next']['url']
        get_course_data(url, courseID, courseList, True )
      else:
        url = ''
        all_done = True
  return courseList 
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