## arguments:
* -v, --verbose : to run in the verbose mode (debug logger)
* -c, --college : pass in the college id. e.g. -c 1,2 - scrape college no 1 and college no 2.

To scrape all colleges pass in: 
**-c all** or don't do **-c** at all
</br>
How to get college ids, it's as simple as running the script with this argument:
**--print-college**
</br>
* -s, --screen-capture : to save a screenshot of the browser before the csv file is downloaded
* -p, --print-college : to print all available colleges with their ids. ids are used to pass as an argument when we want to
scrape only a specific college.

## Installation
* https://www.python.org/downloads/release/python-2713/
* run command line as administrator: **pip instal -U selenium**
