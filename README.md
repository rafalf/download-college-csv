## arguments:
* -v, --verbose : to run in the verbose mode (debug logger)
* -c, --college : pass in the college id. e.g. -c 1,2 - scrape college no 1 and college no 2.
</br>
To scrape all colleges pass in: __-c all__
</br>
How to get college ids, it's as simply as running the script with this argument:
__--print-college__
</br>
* -t, --tree : to save a screenshot of the browser before the csv file is downloaded
* -p, --print-college : to print all available colleges with their ids. ids are used to pass as an argument when we want to
scrape only a specific college.