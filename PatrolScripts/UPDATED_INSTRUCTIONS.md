The original code provided by AVA includes:
- robot_patrol_map.py
- robotutils.py
- get-pip.py
- Instructions for installing and running from a Windows 10 machine

We have made the following changes:
- Created multi-tag patrol scripts for BA00161 and BA00155
- Non-windows instructions

## RUNNING THE PATROL SCRIPTS
1. Navigtate to the appropriate folder
2. If this is the first time running, setup the environment by running:
  * ` python3 -m pipenv install `
3. Run the appropriate patrol script as follows:
  * `python3 -m pipenv run python3 PATROL_SCRIPT_NAME.py`


## PATROL SCRIPT DESIGN
All functionality is built from the test script provided by AVA. The major changes are:
- By default, I've saved the Robot configuration info into the script (the original input-based config code is commented out above). 
- The list of tags to patrol is also defined in the script. (also easily changed to input)
- The robot will perform as single patrol of the tags listed, then return to base. 
- Battery checks are included between each waypoint, instead of at the end of a cycle

The script checks the list of tags to patrol. If there is an error, the user is asked to manually re-enter the entire list. This is done by first asking the user for total number of tags to visit, then the name of each tag (with the list of tags displayed).
