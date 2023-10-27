#!/usr/bin/env python3

import argparse
import json
import tomlkit
from pathlib import Path


########## Project functions ##########

def project_setup(name, path, settings, set_active=True):
    """
    Start a project with a new 'name.json' file in the path directory. Always sets new
    project as `Current Project` if there is none, and optionally does so otherwise.
    """
    if not name:
        name = input("Enter a name for the new project: ")

    project_file = Path(path) / f"{name}.json"
    project_dict = {'name': project_file, 'counters': {}, 'description': '', 'default': ''}

    if "Current Project" not in settings or set_active:
        switch_current_project(project_dict, settings)

    add_counters(int(input("Enter the number of counters in the project: ")), project_dict)
    switch_current_project(project_dict, settings)

    with project_file.open(mode = "x") as f:
        json.dumps(project_dict, f)


def add_counters(num_counters, project_dict):
    """
    Adds num_counters amount of counters to the project json. Asks user for names, rollover value, and relationship
    between counters.
    """
    # TODO set counter relationships
    counters = project_dict['counters']
    for _ in range(num_counters):
        counter_name = input("Please enter a counter name: ")
        rollover = input("Please give a rollover number for the counter: ")
        rollover_value = int(rollover) if rollover.isnumeric() else None
        print(f"Rollover for {counter_name} is {rollover_value}")
        counters[counter_name] = {"count": 0, "rollover": rollover_value}
        print()

    default_counter = input("Enter the default counter name: ")
    if default_counter not in counters.keys():
        print(f"The default counter entered was not in {list(counters.keys())} and will be the first listed.\nYou can change this with the -D option.")
        default_counter = list(counters.keys())[0]
        print(f"The default counter is {default_counter}")
    change_project_default(project_dict, default_counter)


def inc_counter(counter_name, project_dict, num=1):
    """
    Increments counter by num.
    """
    actual_name = counter_name or project_dict['default']
    counter = project_dict['counters'][actual_name]

    start = int(counter['count'])
    rollover = int(counter['rollover'])
    counter['count'] = str((start+num) % rollover) if rollover else str(start + num)

    print(f"Counter: {counter_name} incremented by {num} to {counter['count']}")


def change_project_default(project_dict, new_counter):
    """
    Switches the stored default counter in the project json file.
    """
    project_dict['default'] = new_counter


def switch_default_counter(next_name, config):
    """
    Switches the default counter environment variable to the next_name counter.
    config should be a tomlkit document.
    """
    config["Default Counter"] = next_name


def switch_current_project(project, config):
    """
    Switches the active project to project['name']. Also switches the
    default counter in config. config should be a tomlkit document.
    """
    config["Current Project"] = project["name"]
    switch_default_counter(project["default"], config)


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


def get_project(project_path):
    """
    Get dict from json project file.
    """
    with open(project_path, "r") as file:
        project_dict = json.load(file)
    return project_dict


def put_project(project_dict):
    """
    Write project information to json project file.
    """
    with open(project_dict['name'], "w") as file:
        json.dump(project_dict, file)


def config_init():
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


def main(args):
    # config handling
    if not Path("./knitter.toml").exists():
        config_init()
    settings = get_config()
    project_dict = None

    # argparse handling
    if args.setup or 'Current Project' not in settings:
        path = Path(args.path) if args.path else Path("./Projects")
        project_setup(args.active_name if args.active_name else None, path, settings)
    elif args.project:
        switch_current_project(args.project, settings)
    elif args.default_counter:
        switch_default_counter(args.default_counter, settings)
    elif args.active_name.isnumeric():
        # increment default counter in default project if only number is given
        project_dict = get_project(settings['Current Project'])
        inc_counter(None, project_dict, args.active_name)
    elif args.active_name:
        # increment a specific counter in the default project by 1
        project_dict = get_project(settings['Current Project'])
        inc_counter(args.active_name, project_dict)

    put_config(settings)
    if project_dict:
        put_project(project_dict=project_dict)

if __name__ == "__main__":
########## Start Parser ###############
    parser = argparse.ArgumentParser(description="Adjust, create, and switch knitting project counters.")
    parser.add_argument("active_name", nargs='?', default='default_name', help="Name argument to be acted on, defaults to name of counter to increment.")
    parser.add_argument("-s", "--setup", action="store_true", help="Provide the name of a new knitting project.")
    parser.add_argument("-p", "--path", help="Path to project directory.")
    parser.add_argument("-P", "--project", help="Project to switch to. Must be a relative path to the current working directory.")
    parser.add_argument("-D", "--default_counter", help="The counter to set as default.")
    args = parser.parse_args()
    main(args)
