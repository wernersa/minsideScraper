# minsideScraper
Downloads all files from courses joined on the University of Bergen student website.

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
