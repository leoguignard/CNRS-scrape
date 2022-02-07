# A small script to scrape the candidates from current and previous CNRS competitions

This script allows to retrieve the applicants for the CNRS competitions of years 2018 to today (thanks to François-Xavier Coudert [website](https://www.coudert.name/)).

The format it is saved in is not great and all but that's a start.

## Dependencies

If one just wants to scrap the data:
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

I would recommand to run the command in a separated environement:
```
conda create -n CNRS-scrape
conda activate CNRS-scrape
pip install .
```

## Usage:

To retrieve the wanted data, after installation, one can run the command:
```
python read_html.py --years 2020 2021 2022 --sections 7 21 22 51 --output data.json
```

As many year as wanted can be given (thought only years from 2018 to now are accessible).
Same for the sections.

The output can be a file name or a path+file name. All the necessary folder(s) will be created.