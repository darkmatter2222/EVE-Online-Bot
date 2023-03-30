@echo off
start /min cmd /k "O: & cd O:\source\repos\EVE-Online-Bot"
start /min cmd /k "O: & cd O:\source\repos\venv\Python310\Scripts & activate & cd O:\source\repos\EVE-Online-Bot"
start /min cmd /k "O: & cd O:\source\repos\venv\Python310\Scripts & activate & cd /d O:\source\repos\EVE-Online-Bot & python -m jupyter lab"