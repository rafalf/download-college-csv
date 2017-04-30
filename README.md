# Installation
* https://www.python.org/downloads/release/python-2713/
* run command line as administrator: ```pip instal -U selenium```
* ```pip install openpyxl```

# Scrape course success:
## arguments:
* -v, --verbose : to run in the verbose mode (debug logger)
* -c, --college : pass in a college name e.g. -c Alameda (if not provided, all colleges scraped)
* -p, --print-college : to print out all available colleges
* -s, --screen-capture : to save a screenshot of the browser before the csv file is downloaded
* -p, --print-college : to print all available colleges with their ids. ids are used to pass as an argument when we want to
scrape only a specific college.
* -r, --retry : to set how many times the script will retry to scrape/download data. (***default*** = 3).
* --convert :  to create a xlsx file
* -u, --url : set to: "course success" (or don't pass in as it's set by ***default***)
* --search-type: set to: "Collegewide Search" (***default***) , "Districtwide Search" or "Statewide Search"

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

# Scrape basic skills:
## arguments: 
As before however 2 new arguments are introduced to narrow down search criteria:
* --cohort-term 
* --end-term
* -u, --url : must be set to: basic skills
* --convert : to convert csv to xlsx (***default*** is false; dont convert)
* --level : to scrape a specific cohort level e.g. "One Level Below Transfer"

## Example:
``` python run.py -u "basic skills" -c Alameda --cohort-term "Summer 2009" --end-term "Winter 2017" -s ```
</br>
```python run.py -u "basic skills" -c Alameda --cohort-term "Summer 2009" --end-term "Winter 2017" -s --level "One Level Below Transfer" --convert```

# Scrape transfer
## arguments:
* -u, -url : transfer
* --cohort-year : 1995-1996 (**default** - "Select All") *Note: Did not download a report for me for All*
* --search-type: set to: "Collegewide Search" (***default***) or "Districtwide Search" 
*Note: Statewide Search - no data available for this search*
## Example:
```python run.py -u transfer -c Alameda --convert --cohort-year 1995-1996 -r 5```
</br>
```python run.py -u transfer -c "Cabrillo CCD" --convert --cohort-year 1995-1996 -v --search-type "Districtwide Search"```