#  WIP
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

Screen Scraping + Tesseract = High Performance  
![alt text](https://github.com/darkmatter2222/EVE-Online-Bot/blob/main/Images/SurveyScanResults_Fact.png)  
![alt text](https://github.com/darkmatter2222/EVE-Online-Bot/blob/main/Images/SurveyScanResults_Extract.png)
