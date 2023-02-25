#  WIP
![alt text](https://github.com/darkmatter2222/EVE-Online-Bot/blob/main/Images/banner.png)  

## UPDATE - 2/24/23
Today, we installed the magic! Our first Tensorflow Image classifier. Very simple classifier (yet to be shared w/ the public.) grab the screen and classify if, ["connection_lost", "in_flight", "in_hanger"]. And it works with very minimal trainign data. Will share more when it is cleaned up...  Also built the "Login" function, need to builod "Logout" and "Server Reset" logic. This image classifier enables reading this.  This image classifier can also be sued to detect enemies and build emergency exit plans.  
![](https://github.com/darkmatter2222/EVE-Online-Bot/blob/main/Images/state.png)

## UPDATE - 2/22/23  
It had some hard fails when it did not correctly OCR the Locations table. Added some failsafe logic. Looking at adding some "known depleted" table mapping to make navigation more efficient. Also started testing a complete end-to-end login process.

## UPDATE - 2/21/23  
She works. Got stuck in a situation where we had ore targeted; however, the extractors were not running. Added a 30-minute failsafe to restart the mining run. An ideal solution would be to train an image classifier on the extractor glow from the Icons. Thats overkill.  Next steps, build the auto-login process; not sure how I want to approach that just yet, timers and clicks? That's cheap and easy. Do I need to build a classification engine for the current screen state? Grumble. 
![](https://github.com/darkmatter2222/EVE-Online-Bot/blob/main/Images/extractionhistogram.png)  

## UPDATE - 2/20/23  
Formalized [Miner.py](https://github.com/darkmatter2222/EVE-Online-Bot/blob/main/MiningBot/Miner.py) and moved actions into [Actions.py](https://github.com/darkmatter2222/EVE-Online-Bot/blob/main/MiningBot/BotActions/Actions.py). Also built [Histroy.py](https://github.com/darkmatter2222/EVE-Online-Bot/blob/main/MiningBot/AuditHistory/History.py) to log 'log_navigate', 'log_unload', and 'log_extraction' to a Mongo Atlas cluster.  
Real-Time Chart [Here](https://charts.mongodb.com/charts-homeautomation-snhch/public/dashboards/63f41f3b-3f54-4fe9-847e-affaab662973)  
![](https://github.com/darkmatter2222/EVE-Online-Bot/blob/main/Images/mongo_histroy.png)

## UPDATE - 2/19/23  
A good day; the bot ran nearly all day on a private on-prem server. Had one bug fix that resulted in optimizing the configurations further. Bot cleared three mining belts all by itself today. Likely to add in a mongo cluster for tracking events in real-time and possibly remote control via pubsub. Docking w/ a space station can have some latency. Should install some real-time recognition for when we enter/exit the station. Also need to add in some logic to not round robin all the warp points when they are known to be depleted. 

## UPDATE - 2/18/23  
More cleaning up, now have a dedicated working Interface to Eve and fully working ends-to-end mining and unloading. I also began making all the necessary config items configurable. Deployed to the local server and works after some fine-tuning in the configs. Also crafted an "Overlay" notebook to guide the fine-tuning of the configs. 
I dropped OCR on some of the tables; this was very smart. Far more reliable and far more performant.  

## UPDATE - 2/17/23  
Beginning to formalize the Eve Interface for Screen Scraping. A one Stop Shop for ripping data from the screen configured by JSON. [Here](https://github.com/darkmatter2222/EVE-Online-Bot/blob/main/MiningBot/EveInterface/Interface.py)  
I think I might drop OCR for some cases; the "[get_cargo_data](https://github.com/darkmatter2222/EVE-Online-Bot/blob/9d1428ffa6042c1a8f6d826f4931190bc38bcb0b/MiningBot/EveInterface/Interface.py#L154)" is so accurate, I might do the same with some of the tables. OCR might be Overkill. 

## UPDATE - 2/16/23  
A complete end-to-end automated mining run is finished and working. Many, Many quarks to work out.   
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

