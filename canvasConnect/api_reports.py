#################################################
#Author: Matt Lewis
#Department: Instructional Technology
#Institution: Eastern Washington University
##################################################
from .api_core import *
import requests
import simplejson as json
import sys,os
import csv
import urllib.request
import time
import zipfile
###########################################################################   
############################ API REPORTS ####################################
########################################################################### 
def list_api_reports(domain, token, accountID):
  reportsData=[]
  url = "https://%s/api/v1/accounts/%s/reports?per_page=100" % (domain, accountID)
  print(url)
  response = requests.get(url,headers=get_headers(token))
  if not response.json():
    return "No Terms"
  else:
    json = response.json()
    for s in json:
      paraList = ""
      for key in s['parameters'].keys():
        paraList = paraList + " / " + key
      reportsData.append({'title': s['title'], 'report': s['report'],'parameters': paraList})
  return reportsData
      
###########################################################################
def create_api_report(domain, token, accountID, termID, reportName, reportParams):
  #reportParams = {"parameters[start_at]": startDate, "parameters[enrollment_term_id]": enrollment_term_id}
  reportParams = {"parameters[enrollment_term_id]": termID}
  url = "https://%s/api/v1/accounts/%s/reports/%s" % (domain, accountID, reportName)
  response = requests.post(url,params=reportParams,headers=get_headers(token))
  #print(response.text)
  time.sleep(1)
  status = status_api_report(domain, token, accountID, reportName, response.json()['id'])
    
  return status
###########################################################################
def create_provisioning_report(domain, token, accountID, termID, reportName, reportParams, accounts, courses, enrollments, sections, users, xlist):
  #reportParams = {"parameters[start_at]": startDate, "parameters[enrollment_term_id]": enrollment_term_id}
  reportParams = {"parameters[enrollment_term]": termID, "parameters[accounts]": accounts, "parameters[courses]": courses, "parameters[enrollments]": enrollments,"parameters[sections]": sections, "parameters[users]": users, "parameters[xlist]": xlist, "parameters[groups]": False, "parameters[group_membership]": False, "parameters[include_deleted]": False, "parameters[terms]": False  }
  url = "https://%s/api/v1/accounts/%s/reports/%s" % (domain, accountID, reportName)
  response = requests.post(url,params=reportParams,headers=get_headers(token))
  #print(response.text)
  time.sleep(1)
  status = status_api_report(domain, token, accountID, reportName, response.json()['id'])
  return status
###########################################################################
def status_api_report(domain, token, accountID, reportName, report_id):
  url = "https://%s/api/v1/accounts/%s/reports/%s/%s" % (domain, accountID, reportName, report_id)
  response = requests.get(url,headers=get_headers(token))
  save_path = ""
  if not response.json():
    return "No reports"
  else:
    json = response.json()
    #print(json)
    if json['status'] == 'complete':
      print('Ready for download...')
      save_path = download_api_report(domain, token, json['attachment']['url'], json['report'], json['attachment']['filename'], report_id, json['attachment']['mime_class'])
    elif json['status'] == 'error':
      print('Returned status ERROR.')
      print(json)
      exit
    else:
      message = "Status is %s. Progress at %s percent." % (json['status'], json['progress'])
      print(message)
      time.sleep(10)
      save_path = status_api_report(domain, token, accountID, reportName, report_id)
  return save_path    
###########################################################################
def download_api_report(domain, token, file_url, reportName, filename, report_id, filetype):
  directory = "reports_%s" % (reportName)
  if not os.path.exists(directory):
    os.makedirs(directory)
  #file_name = "%s_%s.csv" % (name, report_id)
  save_path = directory +"/"+ filename
  #urllib.request.urlretrieve (file_url, save_path)
  file_response = requests.get(file_url,get_headers(token),stream=True)
  with open(save_path,'wb') as file_name:
    file_name.write(file_response.content)
  print('Download Complete. File saved to: ' + save_path)
  if filetype == 'zip':
    title=filename.split(".")
    z = zipfile.ZipFile(save_path, "r")
    zip_path = directory +"/%s" % (title[0])
    if not os.path.exists(zip_path):
      os.makedirs(zip_path)
    z.extractall(zip_path)
    z.close()
  return save_path
