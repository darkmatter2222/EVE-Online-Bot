@echo off
start /min cmd /k "C: & cd C:\Users\ryans\source\repos\EVE-Online-Bot"
start /min cmd /k "C: & cd C:\Users\ryans\source\repos\venvs\Python310\Scripts & activate & cd /d C:\Users\ryans\source\repos\EVE-Online-Bot\AI_Pilot & python -m --config_file ai_pilot_config_v2.json --headless_miner 1"