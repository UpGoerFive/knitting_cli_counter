import argparse
import json
import os
from pathlib import Path

########## Start Parser ##########
parser = argparse.ArgumentParser(description="Adjust, create, and switch knitting project counters.")
parser.add_argument("counter_name", help="The name of the counter to increment.")
parser.add_argument("-s", "--setup", help="Provide the name of a new knitting project.")
parser.add_argument("-p", "--path", help="Path to project directory.")
parser.add_argument("-P", "--project", help="Project to switch to.")
parser.add_argument("-D", "--default-counter", help="The counter to set as default.")
args = parser.parse_args()

########## Project functions ##########

# Setup a knitting project
def project_setup(name, path, envs_dict, set_active=True):
    """
    Start a project with a new 'name.json' file in the path directory. Optionally sets the
    new project as the active one.
    """
    project_file = Path(path) / f"{name}.json"
    with project_file.open(mode = "xa") as f:
        json.dump("{'counters': {}, 'description': '', 'default': ''}", f)
    add_counters(input("Enter the number of counters in the project: "), project_file)
    switch_project(project_file, envs_dict)

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
        rollover_value = None if rollover == "None" else int(rollover)
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

    counter = project_dict['default'] if not counter_name else counter_name
    project_dict['counters'][counter]['count'] += num

    with active_path.open(mode="w") as f:
        json.dump(project_dict, f)

# Switch default counter in project
def change_default(project_path, new_counter):
    """
    Switches the stored default counter in the project json file.
    """
    with project_path.open() as f:
        project_dict = json.load(f)

    project_dict['default'] = new_counter

    with project_path.open(mode='w') as f:
        json.dump(project_dict, f)

# Switch default counter variable
def switch_counter(next_name, envs_dict):
    """
    Switches the default counter environment variable to the next_name counter.
    """
    current_counter = envs_dict.get('DEFAULT_COUNTER', next_name)
    if current_counter != next_name:
        envs_dict['DEFAULT_COUNTER'] = next_name

# Switch default project
def switch_project(project_path, envs_dict):
    """
    Switches the active project to next_project located in project_path.
    """
    current_project = envs_dict.get('ACTIVE_PROJECT') # Not setting a default so the counter gets updated as well.
    if current_project != project_path:
        envs_dict['ACTIVE_PROJECT'] = project_path
        with project_path.open() as f:
            default_counter = json.load(f)['default']
        switch_counter(default_counter, envs_dict)

def main():
    if not Path("./Projects").exists():
        Path("./Projects").mkdir()
    envs_dict = os.environ
    if args.setup:
        path = Path(args.path) if args.path else Path("./Projects")
        project_setup(args.setup, path, envs_dict)
    elif args.project:
        switch_project(args.project, envs_dict)
    elif args.default-counter:
        change_default(envs_dict['ACTIVE_PROJECT'], args.default-counter)
    elif args.counter_name:
        inc_counter(args.counter_name, envs_dict['ACTIVE_PROJECT'])
    else:
        inc_counter(None, envs_dict['ACTIVE_PROJECT'])

if __name__ == "__main__":
    main()
