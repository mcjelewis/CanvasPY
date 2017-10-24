#################################################
#Author: Matt Lewis
#Department: Instructional Technology
#Institution: Eastern Washington University
##################################################
from .api_core import *
import requests
import simplejson as json
###########################################################################   
############################ Terms ####################################
########################################################################### 
def confirm_term(domain, token, termData, termID):
  confirm = False
  intWarning = ''
  display = 'Term ID     NAME\n'
  for t in termData:
    try:
      if int(t['term_id']) == int(termID):
        confirm = True
        termName = '%s - %s' % (t['term_id'], t['term_name'])
    except:
      intWarning = 'Please enter the number of the term ID.'
    display = '%s %s - %s\n' % (display, t['term_id'], t['term_name'])
      
  if confirm:
    print('You have entered the term %s' % (termName))
  else:
    print(display, intWarning)
    
  return confirm

###########################################################################
def get_terms(domain, token, accountID):
  termData=[]
  url = "https://%s/api/v1/accounts/%s/terms?per_page=100" % (domain, accountID)
  response = requests.get(url,headers=get_headers(token))
  if not response.json():
    return "No Terms"
  else:
    json = response.json()
    #print(json['enrollment_terms'])
    for s in json['enrollment_terms']:
      termData.append({'term_id': s['id'], 'term_name': s['name'], 'start_at':s['start_at'], 'end_at':s['end_at'], 'sis_term_id':s['sis_term_id']})
  
  return termData
###########################################################################
def get_term_info(termData, termID):
  for t in termData:
      if t['term_id']==int(termID):
        return t
