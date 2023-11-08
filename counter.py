#!/usr/bin/env python3

import argparse
import json
import tomlkit
from pathlib import Path


def project_setup(name, path, settings, set_active=True):
    """
    Start a project with a new 'name.json' file in the path directory. Always sets new
    project as `Current Project` if there is none, and optionally does so otherwise.
    """
    if name == "default_name":
        name = input("Enter a name for the new project: ")

    project_file = Path(path) / f"{name}.json"
    project_dict = {
        "name": str(project_file),
        "counters": {},
        "description": "",
        "default": "",
    }
    settings["Available Projects"].append(str(project_file))

    if "Current Project" not in settings or set_active:
        switch_current_project(project_file, settings)

    add_counters(
        int(input("Enter the number of counters in the project: ")), project_dict
    )

    with open(project_file, "x") as file:
        json.dump(project_dict, file)


def add_counters(num_counters, project_dict):
    """
    Adds num_counters amount of counters to the project json. Asks user for names, rollover value, and relationship
    between counters.
    """
    # TODO set counter relationships
    counters = project_dict["counters"]
    for _ in range(num_counters):
        counter_name = input("Please enter a counter name: ")
        rollover = input("Please give a rollover number for the counter: ")
        rollover_value = int(rollover) if rollover.isnumeric() else None
        print(f"Rollover for {counter_name} is {rollover_value}")
        counters[counter_name] = {"count": 0, "rollover": rollover_value}
        print()

    default_counter = input("Enter the default counter name: ")
    if default_counter not in counters.keys():
        print(
            f"The default counter entered was not in {list(counters.keys())} and will be the first listed.\nYou can change this with the -d option."
        )
        default_counter = list(counters.keys())[0]
        print(f"The default counter is {default_counter}")
    change_project_default(project_dict, default_counter)


def inc_counter(counter_name, project_dict, num=1):
    """
    Increments counter by num.
    """
    actual_name = counter_name or project_dict["default"]
    counter = project_dict["counters"][actual_name]

    start = int(counter["count"])
    rollover = counter["rollover"]
    counter["count"] = (
        str((start + num) % int(rollover)) if rollover else str(start + num)
    )

    print(f"Counter: {actual_name} incremented by {num} to {counter['count']}")


def change_project_default(project_dict, new_counter):
    """
    Switches the stored default counter in the project json file.
    """
    project_dict["default"] = new_counter


def switch_current_project(project_file, config):
    """
    Switches the active project to project_file.
    config should be a tomlkit document.
    """
    if project_file in config["Available Projects"]:
        config["Current Project"] = project_file
    else:
        print(list(enumerate(config["Available Projects"])))
        choice = int(input("Select index of project to switch to from list:\n"))
        config["Current Project"] = config["Available Projects"][choice]


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
    with open(project_dict["name"], "w") as file:
        json.dump(project_dict, file)


def make_project_dir(folder="./Projects"):
    """
    Separate Project directory creation. Use in config init and
    project setup.
    """
    if not Path(folder).exists():
        Path(folder).mkdir()


def config_init():
    """
    Configuration setup for knitting counter. Potential refactor target for setup tools if
    this ever becomes a package for distribution. Creates a `./Projects/` directory and
    `knitter.toml` config file.
    """

    doc = tomlkit.document()
    doc.add("Projects Directory", "./Projects")
    doc.add("Available Projects", [])
    put_config(doc)
    make_project_dir()


def main(args):
    # config handling
    if not Path("./knitter.toml").exists():
        config_init()
    settings = get_config()
    project_dict = None

    # argparse handling
    if "Current Project" not in settings:
        path = input("Enter project directory or leave blank for default ./Projects/" ) or "./Projects"
        make_project_dir(folder=path)
        project_setup(args.active_name, path, settings)
    # Previously combined with the preceding condition. Separated for readability.
    elif args.setup:
        path = args.setup[1] if len(args.setup) > 1 else "./Projects"
        make_project_dir(folder=path)
        project_setup(args.setup[0], path, settings)
    elif args.project:
        switch_current_project(args.project, settings)
    elif args.default_counter:
        project_dict = get_project(settings["Current Project"])
        change_project_default(project_dict, args.default_counter)
    elif args.active_name.isnumeric():
        # increment default counter in default project if only number is given
        project_dict = get_project(settings["Current Project"])
        inc_counter(None, project_dict, int(args.active_name))
    elif args.active_name:
        # increment a specific counter in the default project by 1
        project_dict = get_project(settings["Current Project"])
        counter_name = None

        # allows for handling of no arguments provided
        if args.active_name != "default_name":
            counter_name = args.active_name
        inc_counter(counter_name, project_dict)

    put_config(settings)
    if project_dict:
        put_project(project_dict=project_dict)


if __name__ == "__main__":
    ########## Start Parser ###############
    parser = argparse.ArgumentParser(
        description="Adjust, create, and switch knitting project counters."
    )
    parser.add_argument(
        "active_name",
        nargs="?",
        default="default_name",
        help="Name argument to be acted on, defaults to name of counter to increment.",
    )
    parser.add_argument(
        "-s",
        "--setup",
        nargs="*",
        # default="default_name",
        help="Provide the name of a new knitting project. Optional second item can be a directory location to put project file in.",
    )
    parser.add_argument(
        "-p",
        "--project",
        help="Project to switch to. Must be a relative path to the current working directory.",
    )
    parser.add_argument(
        "-d", "--default_counter", help="The counter to set as default."
    )
    parser.add_argument(
        "-i", "--interactive", help="Run counter interactively."
    )
    args = parser.parse_args()
    main(args)
