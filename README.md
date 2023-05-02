# EVE Online Bot
:star: Consider leaving a Star on [GitHub](https://github.com/darkmatter2222/EVE-Online-Bot) — Great motivation to continue development!

![TensorFlow](https://img.shields.io/badge/TensorFlow-%23FF6F00.svg?style=for-the-badge&logo=TensorFlow&logoColor=white)

## Table Of Contents
- [Features](#features)
    - [Objectives](#objectives)
        - [Auto Miner](#auto-miner)
        - [Waypoint Navigation](#waypoint-navigation)
    - [Sub Functions (Developers)](#sub-functions)
- [Architecture](#architecture)
- [Installation](#installation)
     - [Requirements](#requirements)
     - [Settings](#settings)

## :gift:Features
The following are features of this bot and for the most part, work out of the box after the user has [configured](#installation) their environment. 
### :bulb:Objectives
Objectives are high level functions where all the rules to accomplish the particular objective have been aggregated and normalized into a sequence of events.  
Some objectives can be short lived such as navigating waypoints. Other objectives can consume an entire session such as mining. 
#### :construction:Auto Miner
This objective consumes the entire session, and in fact, will create its own session and manage both the launcher and login process. This bot was built to be a One Click start and will manage itself.  
**Key Features:**
 - Auto Unload at 'Home'
 - Auto Field depleted detection and avoidance 
 - Auto server reboot and reconnect  
 
**ML Component:**
 - Game State (In Hanger, In Flight, Server Disconnected, Character Selection)
 - Miner 1 and miner 2 states  
 
**Pixel Density Component:**
 - Survey Scan Results Window
 - Inventory Window Cargo Fullness  
 
**Tesseract Component:**
 - Locations Window
#### :car:Waypoint Navigation
This objective only runs for as long as you need it to or until it has arrived at its destination, set a chain of waypoints and let the bot blitz through them. How is this different from Auto Pilot in Eve Online? Auto Pilot will land you w/in 5-10km of the target. This wings you as close as your ship will allow.  
Whats the magic here? Leveraging ML to understand the content menus and select the right options.  
**Key Features:**
 - High Speed Way Point Navigation 
 - Auto Stop on Destination
 
**ML Component:**
 - Game State (In Hanger, In Flight, Server Disconnected, Character Selection)
 - Context menu understanding
 
**Pixel Density Component:**
 - None
 
**Tesseract Component:**
 - None

### :wrench:Sub Functions
 - [cargo levels](https://github.com/darkmatter2222/EVE-Online-Bot/blob/main/AI_Pilot/Game_Functions/Cargo/Cargo.py)
 - [unload cargo](https://github.com/darkmatter2222/EVE-Online-Bot/blob/main/AI_Pilot/Game_Functions/Cargo/Cargo.py)
 - [game state](https://github.com/darkmatter2222/EVE-Online-Bot/blob/main/AI_Pilot/Game_Functions/Common/Common.py)
 - [exit hanger](https://github.com/darkmatter2222/EVE-Online-Bot/blob/main/AI_Pilot/Game_Functions/Common/Common.py)
 - [game launcher](https://github.com/darkmatter2222/EVE-Online-Bot/blob/main/AI_Pilot/Game_Functions/Game_Client/Game_Client.py)
 - [login](https://github.com/darkmatter2222/EVE-Online-Bot/blob/main/AI_Pilot/Game_Functions/Game_Client/Game_Client.py)
 - [waypoint navigation](https://github.com/darkmatter2222/EVE-Online-Bot/blob/main/AI_Pilot/Game_Functions/Navigation/Waypoint_Navigation.py)
 - [saved locations navigation](https://github.com/darkmatter2222/EVE-Online-Bot/blob/main/AI_Pilot/Game_Functions/Navigation/Locations_Navigation.py)
 - [mining](https://github.com/darkmatter2222/EVE-Online-Bot/blob/main/AI_Pilot/Game_Functions/Mining/Mining.py)

## :office:Architecture
![alt text](https://github.com/darkmatter2222/EVE-Online-Bot/blob/main/Images/banner.png)  

## :floppy_disk:Installation
This bot consumes your mouse and keyboard, good for running on standalone PC.

### :clipboard:Requirements
1. 1920x1080 Monitor
2. Eve Online running full screen or windowed
3. Create your virtual environment (python 3.9)
4. Install requirements (pip install -r requirements.txt)
5. Install your tensorflow of choice:  
    - pip install tensorflow (recommended, for CPU only)
    - pip install tensorflow-gpu (will require additional GPU setup, not recommended)

### :page_with_curl:Settings
Working on a YT video for this. You will need to configure this for your personal setup. Some of this config is done by hand, the rest is done by an overlay tool.
##### General Config
In [this config file](https://github.com/darkmatter2222/EVE-Online-Bot/blob/main/AI_Pilot/ai_pilot_config_v2.json), under "default.general", set "log_dir", "monitor_number", and "eve_launcher" to your appropriate settings:  
```json
"general": {
  "log_dir": "\\\\databrick\\N\\eve_logs",
  "monitor_number": 2,
  "eve_launcher": "D:\\EVE\\Launcher\\evelauncher.exe"
},
```  
> **Note**
> 'monitor_number' is just a random number the toolkit assigns to your monitors. if you only have 1 monitor, set the value to 0. Experiment what number is yours in the next step.

> **Note**
> You wont need to alter anything under, 'ml_botting_core' if you are using the repo as intended. 'ml_botting_core' feeds directly into, [ml-botting-core](https://github.com/darkmatter2222/ml_botting_core)

##### Static Screen Locations
Out of the box, the following command would work, we are starting the Overlay tooling to set your static clicking and reading space.  
```bat
..\EVE-Online-Bot\Start_AI_Pilot.py --config_file "O:\source\repos\EVE-Online-Bot\AI_Pilot\ai_pilot_config_v2.json" --setup_mode 1
```














