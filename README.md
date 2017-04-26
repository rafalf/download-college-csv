# Scrape college:
## arguments:
* -v, --verbose : to run in the verbose mode (debug logger)
* -c, --college : pass in a college name e.g. -c Alameda

To scrape all colleges pass in: 
**-c all** or don't do **-c** at all
</br>
* -p, --print-college : to print out all available colleges
</br>
* -s, --screen-capture : to save a screenshot of the browser before the csv file is downloaded
* -p, --print-college : to print all available colleges with their ids. ids are used to pass as an argument when we want to
scrape only a specific college.
* -r, --retry : to set how many times the script will retry to scrape/download data. by default is set to 3.
* --convert :  to create a xlsx file
* -u, --url : set to: "course success" (or don't pass in as it's set by ***default***)
* --search-type: set to either: "Collegewide Search" (***default***) , "Districtwide Search" or "Statewide Search"
## Installation
* https://www.python.org/downloads/release/python-2713/
* run command line as administrator: **pip instal -U selenium**
* **pip install openpyxl**

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

# Scrape cohort:
## arguments: 
As before however 2 new arguments are introduced to narrow down search criteria:
* --cohort-term 
* --end-term
</br></br>
* -u, --url : must be set to: basic skills
* --convert : to convert csv to xlsx
* --level : to scrape a specific cohort level e.g. "One Level Below Transfer"

## Example:
``` python run.py -u "basic skills" -c Alameda --cohort-term "Summer 2009" --end-term "Winter 2017" -s ```
</br>
```python run.py -u ""basic skills" -c Alameda --cohort-term "Summer 2009" --end-term "Winter 2017" -s --level "One Level Below Transfer" --convert```