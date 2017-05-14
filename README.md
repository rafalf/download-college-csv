# Installation
* https://www.python.org/downloads/release/python-2713/
* run command line as administrator: ```pip instal -U selenium```
* ```pip install openpyxl```

# Scrape course success:
## arguments:
***default - the argument is not passed in*** 

* -v, --verbose : to run in the verbose mode (debug logger)
* -c, --college : pass in a college name e.g. -c Alameda (if not provided, all colleges scraped)
* -p, --print-college : to print out all available colleges
* -s, --screen-capture : to save a screenshot of the browser before the csv file is downloaded
* -r, --retry : to set how many times the script will retry to scrape/download data. (***default*** = 3).
* --convert :  to create a xlsx file
* -u, --url : set to: "course success" (or don't pass in as it's set by ***default***)
* --search-type: set to: "Collegewide Search" (***default***) , "Districtwide Search" or "Statewide Search"
* --checkboxes: whether to select checkboxes or not (***default*** - 000000000000000 - all unchecked)
*Note: as 0 means not selected, the script will uncheck the checkbox even if is selected by default*

## Examples:
``` python run.py -l -r 10 -v -s``` - scrape all colleges, log into a file in the verbose mode, 
retry up 10 times to scrape data and save a screencap right before the export to csv is cliked upon
</br>
```python run.py -c Alameda``` - scrape the Alameda college
</br>
```pyton run.py -print-college -l``` - open up the url, get the list of all colleges and print it out
</br>
```python run.py -c Alameda --convert``` - scrape Alameda and create a xlsx file
</br>
```python run.py -c "Allan Hancock CCD" --search-type "Districtwide Search"```
</br>
```-c Alameda --convert --checkboxes 111101111011```

# Scrape basic skills:
## arguments: 

***default - the argument is not passed in***  
</br>
As before however 2 new arguments are introduced to narrow down search criteria:
* --cohort-term 
* --end-term
* -u, --url : must be set to: basic skills
* --convert : to convert csv to xlsx (***default*** is false; dont convert)
* --level : to scrape a specific cohort level e.g. "One Level Below Transfer" (***default*** is All)
* --skills-subject : English - Writing, ESL - Listening etc. or Process All (***default***)
* --checkboxes: whether to select checkboxes or not (***default*** - 000000000000000 - all unchecked)
*Note: as 0 means not selected, the script will uncheck the checkbox even if is selected by default*
* --expand-collapse : 0 - collapse, 1 - expand e.g. 01 - collapse 1st heading element and make sure the second is expanded
(***default*** - don't change it)
## Example:
``` python run.py -u "basic skills" -c Alameda --cohort-term "Summer 2009" --end-term "Winter 2017" -s ```
</br>
```python run.py -u "basic skills" -c Alameda --cohort-term "Summer 2009" --end-term "Winter 2017" -s --level "One Level Below Transfer" --convert```
</br>
```python run.py -u "basic skills" -c Alameda --cohort-term "Summer 2009" --end-term "Winter 2017" -s --level "One Level Below Transfer" --skills-subject Mathematics --convert --checkboxes 11111111111```


# Scrape transfer
## arguments:
***default - the argument is not passed in*** 

* -u, -url : transfer
* --cohort-year : 1995-1996 (**default** - "Select All") *Note: Did not download a report for me for All*
* --search-type: set to: "Collegewide Search" (***default***) or "Districtwide Search" 
*Note: Statewide Search - no data available for this search*
* --years-transfer : 4 Years etc. or Process All (***default***)
* --checkboxes: whether to select checkboxes or not (***default*** - 000000000000000 - all unchecked)
*Note: as 0 means not selected, the script will uncheck the checkbox even if is selected by default*

## Example:
```python run.py -u transfer -c Alameda --convert --cohort-year 1995-1996 -r 5```
</br>
```python run.py -u transfer -c "Cabrillo CCD" --convert --cohort-year 1995-1996 -v --search-type "Districtwide Search"```
</br>
```python run.py -u transfer -c "Cabrillo CCD" --convert --cohort-year 1995-1996 -v --search-type "Districtwide Search" --years-transfer "4 Years" --checkboxes 111111111```

# Scrape retention success:
## arguments:
***default - the argument is not passed in*** 
* -u, --url : retention success
* -v, --verbose : to run in the verbose mode (debug logger)
* -c, --college : pass in a college name e.g. -c Alameda (if not provided, all colleges scraped)
* -p, --print-college : to print out all available colleges
* -s, --screen-capture : to save a screenshot of the browser before the csv file is downloaded
* -r, --retry : to set how many times the script will retry to scrape/download data. (***default*** = 3).
* --convert :  to create a xlsx file
* --search-type: set to: "Collegewide Search" (***default***) , "Districtwide Search" or "Statewide Search"
* --checkboxes: whether to select checkboxes or not (***default*** - 000000000000000 - all unchecked)
*Note: as 0 means not selected, the script will uncheck the checkbox even if is selected by default*
* --special-population e.g. "EOPS - Extended Opportunity Programs & Services"
*Note: to get all available special populations, pass in a non-existent population e.g. --special-population "Only Print Out"*

## Examples:
``` python run.py -u "retention success" -l -r 10 -v -s -search-type "Districtwide Search" --special-population "EOPS - Extended Opportunity Programs & Services" ``` - scrape all colleges, log into a file in the verbose mode, 
retry up 10 times to scrape data and save a screencap right before the export to csv is cliked upon
</br>
```python run.py -u "retention success" -c Alameda --convert --special-population "EOPS - Extended Opportunity Programs & Services"``` - scrape Alameda college
</br>
```python run.py -u "retention success" -c "Allan Hancock CCD" --search-type "Districtwide Search" --special-population "EOPS - Extended Opportunity Programs & Services" --checkboxes 111101111011```

# Scrape program awards:
## arguments:
***default - the argument is not passed in*** 
* -u, --url : program awards
* -v, --verbose : to run in the verbose mode (debug logger)
* -c, --college : pass in a college name e.g. -c Alameda (if not provided, all colleges scraped)
* -p, --print-college : to print out all available colleges
* -s, --screen-capture : to save a screenshot of the browser before the csv file is downloaded
* -r, --retry : to set how many times the script will retry to scrape/download data. (***default*** = 3).
* --convert :  to create a xlsx file
* --search-type: set to: "Collegewide Search" (***default***) , "Districtwide Search" or "Statewide Search"
* --checkboxes: whether to select checkboxes or not (***default*** - 000000000000000 - all unchecked)
*Note: as 0 means not selected, the script will uncheck the checkbox even if is selected by default*
* --academic-year e.g. "Annual 2015-2016" (***default*** - (Select All))
* --award-type: (***default*** - All Awards)

## Examples:
``` python run.py -c Alameda -u "program awards" --convert --academic-year "Annual 2015-2016" --checkboxes 11111111 ```
</br>
```python run.py -c Alameda -u "program awards" --convert --checkboxes 11111111 --award-type "Chancellor's Office Approved Awards"```

# Scrape program awards special populations:
## arguments:
***default - the argument is not passed in*** 
* -u, --url : program awards population
* -v, --verbose : to run in the verbose mode (debug logger)
* -c, --college : pass in a college name e.g. -c Alameda (if not provided, all colleges scraped)
* -p, --print-college : to print out all available colleges
* -s, --screen-capture : to save a screenshot of the browser before the csv file is downloaded
* -r, --retry : to set how many times the script will retry to scrape/download data. (***default*** = 3).
* --convert :  to create a xlsx file
* --search-type: set to: "Collegewide Search" (***default***) , "Districtwide Search" or "Statewide Search"
* --checkboxes: whether to select checkboxes or not (***default*** - 000000000000000 - all unchecked)
*Note: as 0 means not selected, the script will uncheck the checkbox even if is selected by default*
* --academic-year e.g. "Annual 2015-2016" (***default*** - (Select All))
* --award-type: (***default*** - All Awards)
* --special-population e.g. "CAA - Career Advancement Academy" (***default*** - (Select All))
*Note: to get all available special populations, pass in a non-existent population e.g. --special-population "Only Print Out"*

## Examples:
``` python run.py -c Alameda -u "program awards population" --convert --checkboxes 11111111```
</br>
``` python run.py -c Alameda -u "program awards population" --convert --academic-year "Annual 2015-2016" --checkboxes 11111111```

