# Automated download of OECD surveys

This module uses Selenium to navigate through pages of OECD datasets.

It clicks on a sequence of buttons in order to download one or more surveys as Excel files.


## Installation


### Requirements:
> 
> * [Python 3.7](https://www.python.org/downloads/release/python-370/)
> * [pipenv](https://docs.pipenv.org/en/latest/)



### Clone the repository

`git clone https://github.com/Patechoc/yangle-oecd-download.git`

### Setup your python environment

* `pipenv shell  # create your local environment` 
* `pipenv install --dev  # install the dependencies`

## Run the script

`pipenv run start`

or 

`python -m oecd_firefox`