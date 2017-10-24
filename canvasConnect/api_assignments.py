#################################################
#Author: Matt Lewis
#Department: Instructional Technology
#Institution: Eastern Washington University
##################################################
from .api_core import *
import requests
import simplejson as json
import sys,os
###########################################################################   
############################ Assignments ####################################
########################################################################### 
def course_assignments(domain, token, courseIDList):
  gradebookList=[]
  assignmentCount = 1
  pCount = 10
  apiCount = 1
  all_done = False
  print('Depending on the number of assignments and courses in this term, this could take a some time.')
  for i in courseIDList:
    #url = 'https://%s/api/v1/courses/%s/assignments?' % (domain,i['course_id'])
    gradebookList = paginated_course_assignments(domain, token,'', gradebookList, i, all_done, 1, pCount, apiCount)
  return gradebookList 

###########################################################################
def paginated_course_assignments(domain, token, url, gradebookList, i, all_done, assignmentCount, pCount, apiCount):
  if not url:
    url = 'https://%s/api/v1/courses/%s/assignments?' % (domain,i['course_id'])
  while not all_done:
    response = requests.get(url,headers=get_headers(token))
    if response.status_code == 200:
      apiCount+=1
      if not response.json():
        exit
      else:
        for s in response.json():
          if assignmentCount > pCount:
            print('Please be patient. ', pCount,' Processing call count: ',apiCount, ' assignment count:', assignmentCount)
            pCount+=15
          assignmentCount+= 1
          if s['published']== true:
            gradebookList.append({'course_id': i['id'], 'course_name': i['name'],  'term_id': i['term']['id'], 'term_name': i['term']['name'], 'canvas_assignment': 'Yes'})
        
      if 'next' in response.links:
          url = response.links['next']['url']
          gradebookList = paginated_course_assignments(domain, token, url, gradebookList, i, all_done, assignmentCount, pCount, apiCount)
      else:
          all_done = True
    else:
      print('#########################################################################')
      print(url)
      print('Returned error code: ', response.status_code)
      print('#########################################################################')      
  return gradebookList
###########################################################################
def get_assignments(domain, token, courseList):
  assignmentList=[]
  for i in courseList:
    all_done = False
    courseID=i['id']
    teacherList=[]
    roleType = "TeacherEnrollment"
    url = "https://%s/api/v1/courses/%s/enrollments?per_page=100&type[]=%s" % (domain, courseID, roleType)
    while not all_done:
      response = requests.get(url,headers=get_headers(token))
      if not response.json():
        all_done = True
      else:
        for t in response.json():
          teacherList.append(t['user']['name'])
      if 'next' in response.links:
          url = response.links['next']['url']
      else:
          all_done = True
    url = 'https://%s/api/v1/courses/%s/assignments?per_page=100' % (domain,i['id'])
    #print(url)
    
    all_done = False
    while not all_done:
      response = requests.get(url,headers=get_headers(token))
      #print(response)
      if not response.json():
        all_done = True
      else:
        for s in response.json():
          assignment = flattenjson(s, "__")
          #Not all fields are set in the data returned by Canvas for each individual assignment.
          #Add additional fields to the saved data array
          if not 'allowed_extensions' in s:
            assignment.update({'allowed_extensions': ""})
          if not 'quiz_id' in s:
            assignment.update({'quiz_id': ""})
          if not 'anonymous_submissions' in s:
            assignment.update({'anonymous_submissions': ""})
          if not 'hide_download_submissions_button' in s:
            assignment.update({'hide_download_submissions_button': ""})
          if not 'points' in s:
            assignment.update({'points': ""})
          if not 'discussion_topic' in s:
            assignment.update({'discussion_topic__user_can_see_posts': "", 'discussion_topic__id': "", 'discussion_topic__user_name': "", 'discussion_topic__group_category_id': "", 'discussion_topic__root_topic_id': "", 'discussion_topic__attachments': "", 'discussion_topic__podcast_has_student_posts': "", 'discussion_topic__last_reply_at': "", 'discussion_topic__permissions__attach': "", 'discussion_topic__read_state': "", 'discussion_topic__posted_at': "", 'discussion_topic__title': "", 'discussion_topic__can_lock': "", 'discussion_topic__discussion_type': "", 'discussion_topic__published': "", 'discussion_topic__locked': "", 'discussion_topic__require_initial_post': "", 'discussion_topic__podcast_url': "", 'discussion_topic__allow_rating': "", 'discussion_topic__delayed_post_at': "", 'discussion_topic__can_unpublish': "", 'discussion_topic__position': "", 'discussion_topic__assignment_id': "", 'discussion_topic__only_graders_can_rate': "", 'discussion_topic__pinned': "", 'discussion_topic__url': "", 'discussion_topic__sort_by_rating': "", 'discussion_topic__html_url': "", 'discussion_topic__discussion_subentry_count': "", 'discussion_topic__permissions__update': "", 'discussion_topic__locked_for_user': "", 'discussion_topic__unread_count': "", 'discussion_topic__lock_at': "", 'discussion_topic__can_group': "", 'discussion_topic__subscribed': "", 'discussion_topic__topic_children': "", 'discussion_topic__message': "", 'discussion_topic__permissions__delete': "",'discussion_topic__author__avatar_image_url': "", 'discussion_topic__author__id': "", 'discussion_topic__author__html_url': "", 'discussion_topic__author__display_name': "",'discussion_topic__subscription_hold':""})
          if not 'rubric' in s:
            assignment.update({'id':"", 'points':"", 'description':"", 'free_form_criterion_comments':"", 'rubric_settings__id':"", 'use_rubric_for_grading':"", 'rubric_settings__free_form_criterion_comments':"", 'rubric':"", 'rubric_settings__title':"", 'rubric_settings__points_possible':""})
          if not 'external_tool_tag_attributes__resource_link_id' in s:
            assignment.update({'external_tool_tag_attributes__resource_link_id':"", 'external_tool_tag_attributes__url':"", 'url':"", 'external_tool_tag_attributes__new_tab':""})
          if not 'peer_review_count' in s:
            assignment.update({'peer_review_count':"", 'peer_reviews_assign_at':""})
          
          assignment.update({'teachers': teacherList})
          assignment.update(i)
          
          #print(teacherList)
          assignmentList.append(assignment)
          #quizID = s.quiz_id
          #get_quiz_grades(courseID,quizID)
      if 'next' in response.links:
          url = response.links['next']['url']
      else:
          all_done = True
      
  return assignmentList
###########################################################################
def get_turnitin_assignments(domain, token, courseList):
  global callCount
  global start
  assignmentList=[]
  for i in courseList:
    all_done = False
    courseID=i['id']
    teacherList=[]
    sectionList=[]
    teacherNetIDList=[]
    url = 'https://%s/api/v1/courses/%s/assignments?per_page=100' % (domain,i['id'])
    print(url)
    
    all_done = False
    while not all_done:
      end = timer()
      seconds = end - start
      m, s = divmod(seconds, 60)
      h, m = divmod(m, 60)
      runtime = 'runtime: %d h :%d m :%d s' % (h, m, s)
      callCount += 1
      print(callCount, " Runtime: ", runtime, " url: ", url)
      response = requests.get(url,headers=get_headers(token))
      #print(response)
      if not response.json():
        all_done = True
      else:
        for s in response.json():
          t = flattenjson(s, "__")
          #print('enabled:', s['turnitin_enabled'])
          if t['turnitin_enabled']:
            #print('enabled')
            #if s['published']:
              #if s['has_submitted_submissions']:
                assignment={}
                assignment.update({'account_id' : i['account_id'], 'term__sis_term_id' : i['term__sis_term_id'], 'course_id': t['course_id'], 'sis_course_id' : i['sis_course_id'], 'assignment_id' : t['id']})
                if not 'discussion_id' in t:
                  assignment.update({'discussion_id' : "" })
                else:
                  assignment.update({'discussion_id' : t['quiz_id'] })
                if not 'quiz_id' in t:
                  assignment.update({'quiz_id' : "" })
                else:
                  assignment.update({'quiz_id' : t['quiz_id'] })
                assignment.update({'course_code' : i['course_code'], 'total_students' : i['total_students']})
                #assignment.update({'teachers': teacherList, 'login': teacherNetIDList, 'sections' : sectionList, })
                assignment.update({'published' : t['published'], 'workflow_state' : i['workflow_state']})
                assignment.update({'has_submitted_submittions' : t['has_submitted_submissions'], 'submission_types' : t['submission_types'], 'submissions_download_url' : t['submissions_download_url']})
                assignment.update({'peer_reviews' : t['peer_reviews'], 'points_possible' : t['points_possible']})
                assignment.update({'turnitin_enabled' : t['turnitin_enabled']})
      
                assignmentList.append(assignment)
                if t['has_submitted_submissions']:
                  #if t['turnitin_settings__submit_papers_to']:
                  folderPath2 = folderPath1 +  str(i['term__sis_term_id']) + str(i['account_id']) + str(t['course_id'])
                    #if not os.path.isdir(folderPath):
                    #   os.makedirs(folderPath)
   
                  #download_submissions(s['course_id'],s['id'], folderPath2)
                  download_submissions(s['course_id'],s['id'], "")

                
      if 'next' in response.links:
          url = response.links['next']['url']
      else:
          all_done = True
      
  return assignmentList 
###########################################################################
def get_vericite_assignments(domain, token, courseList):
  global callCount
  global start
  assignmentList=[]
  for i in courseList:
    all_done = False
    courseID=i['id']
    teacherList=[]
    sectionList=[]
    teacherNetIDList=[]

    url = 'https://%s/api/v1/courses/%s/assignments?per_page=100' % (domain,i['id'])
    print(url)
    
    all_done = False
    while not all_done:
      end = timer()
      seconds = end - start
      m, s = divmod(seconds, 60)
      h, m = divmod(m, 60)
      runtime = 'runtime: %d h :%d m :%d s' % (h, m, s)
      callCount += 1
      print(callCount, " Runtime: ", runtime, " url: ", url)
      response = requests.get(url,headers=get_headers(token))
      #print(response)
      if not response.json():
        all_done = True
      else:
        for s in response.json():
          t = flattenjson(s, "__")
          #print('enabled:', s['vericite_enabled'])
          if t['vericite_enabled']:
            #print('enabled')
            #if s['published']:
              #if s['has_submitted_submissions']:
                assignment={}
                assignment.update({'account_id' : i['account_id'], 'term__sis_term_id' : i['term__sis_term_id'], 'course_id': t['course_id'], 'sis_course_id' : i['sis_course_id'], 'assignment_id' : t['id']})
                if not 'discussion_id' in t:
                  assignment.update({'discussion_id' : "" })
                else:
                  assignment.update({'discussion_id' : t['quiz_id'] })
                if not 'quiz_id' in t:
                  assignment.update({'quiz_id' : "" })
                else:
                  assignment.update({'quiz_id' : t['quiz_id'] })
                assignment.update({'course_code' : i['course_code'], 'total_students' : i['total_students']})
                #assignment.update({'teachers': teacherList, 'login': teacherNetIDList, 'sections' : sectionList, })
                assignment.update({'published' : t['published'], 'workflow_state' : i['workflow_state']})
                assignment.update({'has_submitted_submittions' : t['has_submitted_submissions'], 'submission_types' : t['submission_types'], 'submissions_download_url' : t['submissions_download_url']})
                assignment.update({'peer_reviews' : t['peer_reviews'], 'points_possible' : t['points_possible']})
                assignment.update({'vericite_enabled' : t['vericite_enabled']})
      
                assignmentList.append(assignment)
                if t['has_submitted_submissions']:
                  #if t['turnitin_settings__submit_papers_to']:
                  folderPath2 = folderPath1 +  str(i['term__sis_term_id']) + str(i['account_id']) + str(t['course_id'])
                    #if not os.path.isdir(folderPath):
                    #   os.makedirs(folderPath)
   
                  #download_submissions(s['course_id'],s['id'], folderPath2)
                  download_submissions(s['course_id'],s['id'], "")

                
      if 'next' in response.links:
          url = response.links['next']['url']
      else:
          all_done = True
      
  return assignmentList 

###########################################################################
def download_submissions(domain, token, courseID,assignmentID, folderPath):
  global callCount
  global fileCount
  global fileCountAll
  global submissionsFolder
  fileCountCourse=0
  assessmentList=[]
  all_done = False
  if not os.path.exists(submissionsFolder):
    os.makedirs(submissionsFolder)
  url = 'https://%s/api/v1/courses/%s/assignments/%s/submissions?per_page=100' % (domain,courseID,assignmentID)
  print(url)
  while not all_done:
    callCount += 1
    print(callCount, " url: ", url)
    response = requests.get(url,headers=get_headers(token))
    #print(response)
    if not response.json():
      all_done = True
    else:
      for a in response.json():
        #print(a)
        if 'attachments' in a:
          for b in a['attachments']:
            attachmentID = b['id']
            fileName = b['filename']
            urlFile = b['url']
            fileSize = b['size']
            contentType = b['content-type']
            #contentPieces = contentType.split("/")
            contentPieces = fileName.split(".")
            fileExtension = contentPieces[len(contentPieces)-1]
            contentName = contentPieces[0]
            #truncate name down to a max of 200 characters
            if len(contentName) > 200:
              contentName = contentName[:200]
            fileName = contentName + "." + fileExtension
            #print(fileExtension)
            #filePath = folderPath + "/" + fileName
            fileNameAttachment = str(attachmentID) + "_" + fileName
            filePath = '%s/%s' % (submissionsFolder, fileNameAttachment)
            extAvailable = ["doc", "docx", "pdf", "rtf", "txt", "ps", "wp", "odt", "ods", "odp"]
            #print(filePath)
            
            fileCountAll +=1
            if os.path.isfile(filePath):
              print('File already exists: ', fileName)
            else:  
              if fileExtension in extAvailable:
                fileCountCourse +=1
                fileCount +=1
                r = requests.get(urlFile)
                with open(filePath, "wb") as code:
                  code.write(r.content)
                    

    if 'next' in response.links:
      url = response.links['next']['url']
    else:
      print("Course downloadCount:", fileCountCourse)
      print("Running downloadCount:", fileCount)
      print("All Files:", fileCountAll)
      all_done = True
 