#################################################
#Author: Matt Lewis
#Department: Instructional Technology
#Institution: Eastern Washington University
##################################################
from .api_core import *
import requests
import simplejson as json
###########################################################################   
############################ Accounts ####################################
########################################################################### 
def subAccounts(domain, token, rootID):
  accountList=[]
  all_done = False
  #print('Depending on the number of sub-accounts, this could take a little while.')
  subaccountCount= 1
  aCount = 5
  accountList = paginated_subAccounts(domain, token,'', rootID, accountList, subaccountCount, aCount)
  return accountList 

###########################################################################
def paginated_subAccounts(domain, token, url, accountID, accountList, subaccountCount, aCount):
  all_done = False
  if not url:
    url = 'https://%s/api/v1/accounts/%s/sub_accounts' % (domain,accountID)
  while not all_done:

    response = requests.get(url,headers=get_headers(token))
    if not response.json():
      #yield []
      return
    else:
      print(subaccountCount)
      for s in response.json():
        if subaccountCount > aCount:
          print('Please be patient. counter:', subaccountCount)
          aCount+=5
        subaccountCount+=1
        accountList.append({'account_id': s['id'], 'account_name': s['name']})
        #paginated_subAccounts(s['id'], accountList, subaccountCount, pCount)
    if 'next' in response.links:
      url = response.links['next']['url']
     
      paginated_subAccounts(domain, token, url, '', accountList, subaccountCount, aCount) 

    else:
      all_done = True
    return accountList
########################################################################### 
def confirm_account(domain, token, accountData, accountID):
  confirm = False
  intWarning = ''
  display = 'Account ID     NAME\n'
  for a in accountData:
    try:
      if int(a['account_id']) == int(accountID):
        confirm = True
        accountName = '%s - %s' % (a['account_id'], a['account_name'])
    except:
      intWarning = 'Please enter the number of the account.'
    display = '%s %s - %s\n' % (display, a['account_id'], a['account_name'])
      
  if confirm:
    print('You have entered the account %s' % (accountName))
  else:
    print(display, intWarning)
  return confirm
