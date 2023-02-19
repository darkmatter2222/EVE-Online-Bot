#  WIP
![alt text](https://github.com/darkmatter2222/EVE-Online-Bot/blob/main/Images/banner.png)  

## UPDATE - 2/18/23  
More cleaning up, now have a dedicated working Interface to Eve and fully working ends to end mining and unloading. Also began making all the necessary config items configureable. Deplyed to local server and workes after some fine tuning in the configs. Also crafted an "Overlay" notebook to guide the fuine tuing of the configs. 
Dropped OCR on some of the tables, this was very smary. Far mroe reliable and far more performant.  

## UPDATE - 2/17/23  
Beginning to formalize the Eve Interface for Screen Scraping. A one Stop Shop for ripping data from the screen configured by JSON. [Here](https://github.com/darkmatter2222/EVE-Online-Bot/blob/main/MiningBot/EveInterface/Interface.py)  
I think i might drop OCR for some cases, the "[get_cargo_data](https://github.com/darkmatter2222/EVE-Online-Bot/blob/9d1428ffa6042c1a8f6d826f4931190bc38bcb0b/MiningBot/EveInterface/Interface.py#L154)" is so accuriate, I might do the same with some of the tables. OCR might be Overkill. 

## UPDATE - 2/16/23  
A complete end to end automated mining run is finished and working. Many Many quarks to work out.   
Inside this [notebook](https://github.com/darkmatter2222/EVE-Online-Bot/blob/main/Experiment/SurveyScanResultsInit.ipynb)  








## Objective  
Build a Bot for Eve Online that has only one input and one control mechanism, graphical screen scraping and mouse movements respectively.  

Screen scraping is a very powerful tool for different types of applications. Web browsers and thick clients generally have some method of UI snagging that bots can read from. Eve Online is very difficult to scrape from and generally requires memory access and memory dumps to interoperate what is on screen. While very powerful, memory dumps can be very large and if not managed properly, murder an SSD.  

### *Enter, Screen Scraping*  
The screen scraping approach we take here is not traditional by any means, we will implement several forms of OCR and ML models to identify objects on screen and action for that inference. Eve is comprised of sprites and tables; the plan of action is:  
- OCR for Alphanumeric in tables  
- ML (TensorFlow) for Sprite Classification (Mostly Binary)  

## What does this Repo offer you?
This repo will contain several things: 
- Python Bots
- Python UI Exploration Tools
- Training Data Sets
- Ability to Execute Yourself

