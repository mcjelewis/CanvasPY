
***
Author: Matt Lewis  
Department: Instructional Technology  
Institution: Eastern Washington University
Script: Python3
***
## DESCRIPTION
***
This code is used to upload new outcomes into Canvas at an account level. Data from an uploaded csv file is used to add a new outcome group if needed, as well as update or add the settings for an outcome. Only one rating scale can be used for each file being uploaded.

This is a heavily modified version of kajiagga's [outcome importer](https://github.com/kajigga/canvas-contrib/tree/master/API_Examples/import_outcomes/python). Kept the access to csv files through kajiagga's functions, rewrote most of the logic on process for searching, adding, updating outcomes modifided the kajiagga csv file: added columns for account_id and outcome group vendor, renamed other fields and removed parent_id field

***
## CSV FILE
***
**Required Header**   
You will need to format a csv file with the required headers.
Required Header Field Names:'account_id','parent_directory','title','description','calculation_method','calculation_int','mastery_points'

   'account_id': Enter the account id for where the outcome will reside if in a department or college.  Leave empty if adding outcomes to a course. Course ID can be entered when executing the script.   
   'parent_directory': Directory structure of where the outcome will reside within the account. Canvas allows for the creation of folders (Canvas calls them groups).   
   Limitation: While Canvas will allow for the same name to be used for multiple folders, this script does not. When creating the folder structure use a different title for each folder (group).   
   'title': Title of the outcome   
   'description': Description of the outcome   
   'calculation_method': Canvas allows the options; decaying_average, n_mastery, highest, lowest   
   'calculation_int': If method is decaying_average or n_mastery, the calculation integer should be set   
   'mastery_points': The value marking mastery of the outcome   
   At the end of the header row add the rating scale title that will be used for this set of outcomes. For example, 'Exceeds Expectations', 'Mets Expectations', 'Does Not Met Expectations' each as a column title   

The point values for each rating are place in the data row under each outcome scale title.

**Notes**
1. For each csv file, only one rating scale can be used.
2. Limitation on folder (group) titles; cannot use same title for multiple folders. Outcome will be placed in the first folder (group) found.


***
## CUSTOMISE SCRIPT
***

Edit the domain variables starting on line 40 to match your institutional Canvas domains for beta, test, and production.

***
## RUN SCRIPT
***

For those unfamilar with how to run a python script, Python Central has a good article (http://pythoncentral.io/execute-python-script-file-shell/) that might help you get started.

This script has a required argument for the path of the csv file (--outcomesfile). Once the script runs, it will ask if the outcomes are for a specific course. If yes, it will then ask for the Canvas course id.

*Example Command*  
>  #! python [path to file]/outcome_imprter.py --outcomesfile [path to csv file]
