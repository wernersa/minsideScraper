# minsideScraper
Downloads all files from courses joined on the University of Bergen student website.

Adding environment variables in linux:
```bash
cat << ! >> ~/.bashrc
export PYNMA-API=api-string-goes-here
export MINSIDE-USERNAME=usr123
export MINSIDE-PASS=password
export MINSIDE-FOLDER=$HOME/Documents/Minside
!
source ~/.bashrc
```

Adding environment variables in windows:
```batch
    putx PYNMA-API api-string-goes-here
    putx MINSIDE-USERNAME usr123
    putx MINSIDE-PASS password
    putx MINSIDE-FOLDER $HOME\\Documents\\Minside
```
