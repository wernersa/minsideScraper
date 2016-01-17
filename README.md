# minsideScraper
Downloads all files from courses joined on the University of Bergen student website.

## Requirements

If you are to use the python file as is, you will have to add the neccesary variables to your environment. PYNMA_API is the api string for Notify my Android which is used by `pynma` for push notifications. This script has only been tested with `Python 2.7`

Adding environment variables in linux:
```bash
cat << ! >> ~/.bashrc
export PYNMA_API=api-string-goes-here
export MINSIDE_USERNAME=usr123
export MINSIDE_PASS=password
export MINSIDE_FOLDER=$HOME/Documents/Minside
!
source ~/.bashrc
```

Adding environment variables in windows:
```batch
putx PYNMA_API api-string-goes-here
putx MINSIDE_USERNAME usr123
putx MINSIDE_PASS password
putx MINSIDE_FOLDER $HOME\\Documents\\Minside
```

## Usage

If the python executable is in your environment you can run the file through cmd or terminal with the following line:

```bash
python /path/to/run.py PROPSY301 PROPSY302
```

The script will not run unless you supply course names as arguments in the command line.
