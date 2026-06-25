"""
This file contains the tuple for tabs and parameter lists for
the dropdowns of CTkOptionMenus and CTkComboBoxes.
After adding 'import params' to the main.py file,
the lists can be called as 'params.my_list'.

First compiled 03-06-2026 by Thoralf Opitz (topitz@uni-bonn.de)
"""

# Headers of tabs in main window
tab_title: tuple[str, str, str, str, str] = (
    "add Animal",
    "add Session",
    "kill Animal",
    "Welcome",
    "display Sessions"
)

mouse_sex: list[str] = ["Female", "Male"]

# List of commonly used mouse lines, partially including genotype
mouse_line: list[str] = [
    "C57B6/J",
    "C57B6/N",
]

# Names of people appearing in dropdown list of surgeons
mouse_surgeon: list[str] = [
    "Max Mueller",
    "Lena Schulze",
    "T_Opitz"
]

# List of animal welfare licenses for fUSI experiments
mouse_license: list[str] = [
    "2020-007",     # fUSI-pilot, valid until 02-08-2029
    "2021-666"      # fUSI-cortical_dysplasia, valid until xx-xx-2031
]

# Descriptive name of specific experiments that include fUSI
experiment_name: list[str] = [
    "generic test",
    "trace Eyeblink",
    "Odd ball",
    "social contact"
]

# Descriptive name of a recording session as part of a specific experiment
session_name: list[str] = [
    "plain recording",
    "habituation",
    "conditioning",
    "extinction",
    "acoustic stimuli",
    "visual stimuli",
    "social odor",
    "sensory stimuli"
]

# Purpose the animal was killed for (adheres to Pyrat assignments)
kill_purpose: list[str] = [
    "Experiment",
    "Health issue",
    "other"
]

# Method the animal was killed with (check animal welfare grant!)
kill_method: list[str] = [
    "perfusion",
    "cerv. dislocation",
    "deceased"
]

# Folder-ID for "mice" in RSpace
rspace_mice_folder_id = "FL248822"
rspace_session_notebook_id = "NB484055"

