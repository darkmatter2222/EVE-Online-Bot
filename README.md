# EVE Online Bot
:star: Consider leaving a Star on [GitHub](https://github.com/darkmatter2222/EVE-Online-Bot) — Great motivation to continue development!

![TensorFlow](https://img.shields.io/badge/TensorFlow-%23FF6F00.svg?style=for-the-badge&logo=TensorFlow&logoColor=white)

## Table Of Contents
- [Installation](#installation)
     - [Requirements](#requirements)
     - [Settings](#settings)

## Installation
This bot consumes your mouse and keyboard, good for running on standalone PC.

### Requirements
1. 1920x1080 Monitor
2. Eve Online running full screen or windowed
3. Create your virtual environment (python 3.9)
4. Install requirements (pip install -r requirements.txt)
5. Install your tensorflow of choice:  
    - pip install tensorflow (recommended, for CPU only)
    - pip install tensorflow-gpu (will require additional GPU setup, not recommended)

### Settings
Working on a YT video for this. You will need to configure this for your personal setup. Some of this config is done by hand, the rest is done by an overlay tool.
##### General Config
In [this config file](https://github.com/darkmatter2222/EVE-Online-Bot/blob/main/AI_Pilot/ai_pilot_config_v2.json), under "default.general", set "log_dir", "monitor_number", and "eve_launcher" to your appropriate settings:  
'''json
"general": {
  "log_dir": "\\\\databrick\\N\\eve_logs",
  "monitor_number": 2,
  "eve_launcher": "D:\\EVE\\Launcher\\evelauncher.exe"
},
'''  
> **Note**
> 'monitor_number' is just a random number the toolkit assigns to your monitors. if you only have 1 monitor, set the value to 0. Experiment what number is yours in the next step.










![alt text](https://github.com/darkmatter2222/EVE-Online-Bot/blob/main/Images/banner.png)  


