#!/usr/bin/env python3

import argparse
import json
import os
import tomlkit
from pathlib import Path

########## Start Parser ###############

parser = argparse.ArgumentParser(description="Adjust, create, and switch knitting project counters.")
parser.add_argument("active_name", nargs='?', default='default_name', help="Name argument to be acted on, defaults to name of counter to increment.")
parser.add_argument("-s", "--setup", action="store_true", help="Provide the name of a new knitting project.")
parser.add_argument("-p", "--path", help="Path to project directory.")
parser.add_argument("-P", "--project", help="Project to switch to. Must be a relative path to the current working directory.")
parser.add_argument("-D", "--default_counter", help="The counter to set as default.")
args = parser.parse_args()

########## Project functions ##########

# Setup a knitting project
def project_setup(name, path, set_active=True):
    """
    Start a project with a new 'name.json' file in the path directory. Always sets new
    project as `Current Project` if there is none, and optionally does so otherwise.
    """

    project_file = Path(path) / f"{name}.json"

    with open("./knitter.toml", "r") as file:
        settings = tomlkit.load(file)

    if "Current Project" not in settings or set_active:
        settings["Current Project"] = project_file
        with open("./knitter.toml", "w") as file:
            tomlkit.dump(settings, file)

    with project_file.open(mode = "x") as f:
        json.dump({'counters': {}, 'description': '', 'default': ''}, f)
    add_counters(int(input("Enter the number of counters in the project: ")), project_file)
    switch_default_project(project_file)

# Add counters to project with counter logic
def add_counters(num_counters, active_path):
    """
    Adds num_counters amount of counters to the project json. Asks user for names, rollover value, and relationship
    between counters.
    """
    with active_path.open() as f:
        project_dict = json.load(f)

    counters = project_dict['counters']
    for _ in range(num_counters):
        counter_name = input("Please enter a counter name: ")
        rollover = input("Please give a rollover number for the counter: ")
        rollover_value = None if type(rollover) != int else int(rollover)
        counters[counter_name] = {"count": 0, "rollover": rollover_value}

    default_counter = input("Enter the default counter name: ")
    if default_counter not in counters.keys():
        print(f"The default counter entered was not in {list(counters.keys())} and will be the first listed.\nYou can change this with the -D option.")
        default_counter = list(counters.keys())[0]
        print(f"The default counter is {default_counter}")
    project_dict['default'] = default_counter

    with active_path.open(mode="w") as f:
        json.dump(project_dict, f)

# Save counts to JSON doc
def inc_counter(counter_name, active_path, num=1):
    """
    Increments counter by num.
    """
    with active_path.open() as f:
        project_dict = json.load(f)

    counter = counter_name or project_dict['default']
    start = int(project_dict['counters'][counter]['count'])
    project_dict['counters'][counter]['count'] = str(start+num)
    print(f"Counter: {counter_name} incremented by {num}")

    with active_path.open(mode="w") as f:
        json.dump(project_dict, f)

# Switch default counter in project
def change_project_default(project_path, new_counter):
    """
    Switches the stored default counter in the project json file.
    """
    with project_path.open() as f:
        project_dict = json.load(f)

    project_dict['default'] = new_counter

    with project_path.open(mode='w') as f:
        json.dump(project_dict, f)

# Switch default counter variable
def switch_default_counter(next_name, config):
    """
    Switches the default counter environment variable to the next_name counter.
    config should be a tomlkit document.
    """
    config["Default Counter"] = next_name
    return config


# Switch default project
def switch_default_project(project, config):
    """
    Switches the active project to project_path. Also call switches the
    default counter in config. config should be a tomlkit document.
    """
    config["Default Project"] = project["name"]
    return switch_default_counter(project["default"], config)


def get_config(config_file="./knitter.toml"):
    """
    Gets tomlkit document object from config file.
    """
    with open(config_file, "r") as file:
        config = tomlkit.load(file)
    return config

def put_config(config, config_file="./knitter.toml"):
    """
    Writes tomlkit document to config_file.
    """
    with open(config_file, "w") as file:
        tomlkit.dump(config, file)

def knit_config():
    """
    Configuration setup for knitting counter. Potential refactor target for setup tools if
    this ever becomes a package for distribution. Creates a `./Projects/` directory and
    `knitter.toml` config file.
    """

    doc = tomlkit.document()
    doc.add("Projects Directory", "./Projects")
    doc.add("Available Projects", "")
    put_config(doc)

    if not Path("./Projects").exists():
        Path("./Projects").mkdir()


def main():
    # Make project directory
    # Moving to a config file for settings, rather than environment variable mess.
    if not Path("./knitter.toml").exists():
        knit_config()

    # Argument parsing
    settings = get_config()

    if args.setup:
        path = Path(args.path) if args.path else Path("./Projects")
        project_setup(args.active_name, path)
    elif args.project:
        switch_default_project(Path(args.project), settings)
    elif 'Current Project' not in settings:
        project_setup(input("Enter new project name: "), Path("./Projects"))
    elif args.default_counter:
        change_project_default(settings['Current Project'], args.default_counter)
    elif args.active_name.isnumeric():
        inc_counter(None, settings['Current Project'], args.active_name)
    else:
        inc_counter(args.active_name, settings['Current Project'])

if __name__ == "__main__":
    main()
