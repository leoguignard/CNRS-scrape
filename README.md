# A small script to scrape the candidates from current and previous CNRS competitions

This script allows the retrieval of the applicants for the CNRS competitions of years 2019 to today (thanks to François-Xavier Coudert [website](https://www.coudert.name/)).

The format it is saved in is not great and all but that's a start.

**Also, the google scholar scrape is really (really) slow**

## Disclaimer!

All the data scraped here is to be taken with a **grain of salt**.

Even though it is likely that the people that are pulled in google scholar are the people who applied, it is not necessarily true. Therefore **the data might be sometimes erroneous**.

Moreover, **not everyone can be found on google scholar, so the data is only partial**.

Finally, **some people have homonyms**, because I would rather have no data than false data, I decided to **discard data points when multiple hits were found** by google scholar.

## Dependencies

If one just wants to scrape the data:
- [pandas](https://pandas.pydata.org/)
- [scholarly](https://scholarly.readthedocs.io/en/stable/quickstart.html)

If one wants to also plot the data using the provided notebook:
- [jupyter notebook](https://jupyter.org/)
- [matplotlib](https://matplotlib.org/)
- [seaborn](seaborn.pydata.org/)

## Installation

One can either download the code using the `Code/Download zip` button or using git:
```
git clone https://github.com/leoguignard/CNRS-results.git
```

Once in the folder CNRS-results, to install all dependencies at once, one can run the following command:
```
pip install .
```

I would recommend to run the command in a separated environment:
```
conda create -n CNRS-scrape
conda activate CNRS-scrape
conda install pip
pip install .
```

## Usage:

To retrieve the wanted data, after installation, one can run the command:
```
python read_html.py --years 2019 2020 2021 2022 --sections 7 21 22 51 --output data.json
```

As many years as wanted can be given (though only years from 2019 to now are accessible).
Same for the sections.

The output can be a file name or a path+file name. All the necessary folder(s) will be created.

**It is important to remember that the scrape is quite slow!!**

**Please, be patient :)**
