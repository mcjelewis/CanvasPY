#################################################
#Author: Matt Lewis
#Department: Instructional Technology
#Institution: Eastern Washington University
##################################################
from .api_core import *
import requests
import simplejson as json
###########################################################################   
############################ Messaging/Communication ####################################
########################################################################### 
def message_list(domain, token, url, user_id, filterMsg, messageList, all_done):
  message_count=0
  if not url:
      url = "https://%s/api/v1/comm_messages?user_id=%s%s&per_page=100" % (domain, user_id, filterMsg)
  print('message list api url:', url)
  while not all_done:
    response = requests.get(url,headers=get_headers(token))
    if response.status_code == 200:
      if not response.json():
        url = ''
        all_done = True
      else:
        for s in response.json():
          message = flattenjson(s, "__")
          #print('id:', s['id'])
          message_count += 1
          messageList.append(message)
          
        if 'next' in response.links:
          url = response.links['next']['url']
          messageList = message_list(url, user_id, filterMsg,  messageList, False)
        else:
          url = ''
          all_done = True
    else:
      print('Returned error code: ', response.status_code)
      print('#########################################################################')
      exit()
  return messageList


###########################################################################
def conversation_list(domain, token, url, user_id, filterTxt, conversationList, all_done):
  conversation_count=0
  if not url:
      url = "https://%s/api/v1/conversations?as_user_id=%s%s&per_page=100" % (domain, user_id, filterTxt)
  print('conversation api url:', url)
  while not all_done:
    response = requests.get(url,headers=get_headers(token))
    if response.status_code == 200:
      if not response.json():
        url = ''
        all_done = True
      else:
        for s in response.json():
          aud_context = s['audience_contexts']
          del s['audience_contexts']
          conversation = flattenjson(s, "__")
          conversation.update({'audience_contexts' : aud_context})
          #print('id:', s['id'])
          conversation_count += 1
          conversationList.append(conversation)
          
        if 'next' in response.links:
          url = response.links['next']['url']
          conversationList = conversation_list(domain, token, url, user_id, filterTxt, conversationList, False)
        else:
          url = ''
          all_done = True
    else:
      print('Returned error code: ', response.status_code)
      print('#########################################################################')
  return conversationList 

###########################################################################