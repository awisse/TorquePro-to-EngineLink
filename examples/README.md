# Examples of converted files

Using a simplified directory structure from 
[OBD-PIDs-for-HKMC-EVs](https://github.com/JejuSoul/OBD-PIDs-for-HKMC-EV), we 
present a number of PID files converted from that project with comments about 
the actual availability of the values in the EngineLink apps in the Excel file
ending in *concatenated-EL.xlsx*.

Certain variables in formulas in the project files refer to values in 
other files, or to values defined further down in the same file. For example. 
The file *Kia_Soul_EV_Extra_gauges.csv* contains a reference to the value of 
`000_HV_Charging`, defined in *Kia_Soul_EV_BMS_data.csv*. `tp2el.py` only 
substitutes variables defined in the same file. A workaround is to 
concatenate the *csv* files in the order of the leading digits of the 
variable names defined in the first column of the original TorquePro csv 
files. However, this doesn't solve the issue with variables defined further
down in the same file. These issues are adressed in #1 and #2.

The working status of all of the values is documented in the **Works** column
of the "concatenated-EL.xlsx" file in the subdirectory of each vehicle.
