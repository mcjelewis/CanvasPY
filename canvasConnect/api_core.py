#################################################
#Author: Matt Lewis
#Department: Instructional Technology
#Institution: Eastern Washington University
##################################################
from .api_core import *
import requests
import simplejson as json
###########################################################################   
############################ Core FUNCTIONS ####################################
########################################################################### 
def get_headers(token):
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
def confirm_token(domain, token):
  url = "https://%s/api/v1/users/self/activity_stream/summary" % (domain)
  response = requests.get(url,headers=get_headers(token))
  if response.status_code == 200:
    confirm = True
  else:
    confirm = False
    print('The entered Canvas token did not authenticate.')
    
  return confirm
###########################################################################
def getRootID(domain, token):
  url = "https://%s/api/v1/accounts?per_page=100" % (domain)
  print(url)
  response = requests.get(url,headers=get_headers(token))
  print('Status Code ',response.status_code)
  if response.status_code == 200:
    for s in response.json():
      if not s['root_account_id']:
        rootID = s['id']
      else:
        rootID = s['root_account_id']
  else:
    print('Returned error code: ', response.status_code)
    print('#########################################################################')
    exit()
  return rootID

###########################################################################
def checkFileReturnCSVReader(file_name):
  if file_name and os.path.exists(file_name):
    return csv.reader(open(file_name,'rU'))
  else:
    return None
  
###########################################################################
  