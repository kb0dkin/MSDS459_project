@echo off

:: Create and activate the conda environment
conda create -n MSDS459 --file environment.yaml
conda activate MSDS459

:: start the edgedb instance
edgedb instance start -I MSDS_459

:: start scraping
cd scraper
python scraper.py
cd ..