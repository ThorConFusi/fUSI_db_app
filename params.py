"""
This file contains the tuple for tabs and parameter lists for
the dropdowns of CTkOptionMenus and CTkComboBoxes.
After adding 'import params' to the main.py file,
the lists can be called as 'params.my_list'.

First compiled 03-06-2026 by Thoralf Opitz (topitz@uni-bonn.de)
"""

# Destination for RSpace uploads
api_inbox_id = 492620

# Names of people appearing in dropdown list of surgeons
mouse_surgeon: list[str] = [
    "Therese Alich",
    "Olga Salyp",
    "Thoralf Opitz"
]

# List of animal welfare licenses for fUSI experiments
mouse_license: list[str] = [
    "2024-287",     # fUSI-pilot, valid until 02-08-2029
    "2026-642"      # fUSI-cortical_dysplasia, valid until xx-xx-2031
]

# List of commonly used mouse lines, partially including genotype
mouse_line: list[str] = [
    "C57B6/J",
    "C57B6/N",
]

mouse_keys = [
    "Pyrat-ID", "Sex", "Line", "D.o.Birth",
    "License", "D.o.Surgery", "T.o.Surgery",
    "Surgeon"
]

session_keys = [
    "Pyrat-ID", "D.o.Recording", "T.o.Recording",
    "Session_number", "Experiment", "Session"
]

sacrifice_keys = [
    "Pyrat-ID", "License", "D.o.Death", "T.o.Death",
    "Kill_method", "Kill_purpose", "Kill_comment"
]

comment_surgery = ("Body weight: g\n\nKetamine/Medetomidine i.p.: \nKetoprofen s.c.: \nDexamethasone s.c.: \n"
                   "Buprenorphine s.c.: \nAtipamezol i.p.: \n")

comment_sacrifice = ("Ketamine/Xylazine i.p.: ")

# Descriptive name of specific experiments that include fUSI
experiment_name: list[str] = [
    "generic_test",
    "trace_eyeblink",
    "odd_ball",
    "social_contact"
]

# Descriptive name of a recording session as part of a specific experiment
session_name: list[str] = [
    "plain_recording",
    "habituation",
    "conditioning",
    "extinction",
    "acoustic_stimuli",
    "visual_stimuli",
    "social_odor",
    "sensory_stimuli"
]

# Purpose the animal was killed for (adheres to Pyrat assignments)
kill_purpose: list[str] = [
    "experiment",
    "health_issue",
    "other"
]

# Method the animal was killed with (check animal welfare grant!)
kill_method: list[str] = [
    "perfusion",
    "cerv_dislocation",
    "deceased"
]

mouse_sex: list[str] = ["Female", "Male"]

# Headers of tabs in main window
tab_title: tuple[str, str, str, str, str] = (
    "add Animal",
    "add Session",
    "kill Animal",
    "Welcome",
    "display Sessions"
)

