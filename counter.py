import argparse
import json
import os
from pathlib import Path

########## Start Parser ##########

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
    Start a project with a new 'name.json' file in the path directory. Optionally sets the
    new project as the active one.
    """
    project_file = Path(path) / f"{name}.json"
    with project_file.open(mode = "x") as f:
        json.dump({'counters': {}, 'description': '', 'default': ''}, f)
    add_counters(int(input("Enter the number of counters in the project: ")), project_file)
    switch_project(project_file)

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
    project_dict['counters'][counter]['count'] += num
    print(f"Counter: {counter_name} incremented by {num}")

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
def switch_counter(next_name):
    """
    Switches the default counter environment variable to the next_name counter.
    """
    current_counter = os.environ.get('DEFAULT_COUNTER', next_name)
    if current_counter != next_name:
        os.environ['DEFAULT_COUNTER'] = next_name

# Switch default project
def switch_project(project_path):
    """
    Switches the active project to next_project located in project_path.
    """
    current_project = os.environ.get('ACTIVE_PROJECT') # Not setting a default so the counter gets updated as well.
    if current_project != str(project_path):
        os.environ['ACTIVE_PROJECT'] = str(project_path)
        with project_path.open() as f:
            default_counter = json.load(f)['default']
        switch_counter(default_counter)

def main():
    # Make project directory
    # TODO make this optional
    if not Path("./Projects").exists():
        Path("./Projects").mkdir()

    # Argument parsing
    if args.setup:
        path = Path(args.path) if args.path else Path("./Projects")
        project_setup(args.active_name, path)
    elif args.project:
        switch_project(Path(args.project))
    elif 'ACTIVE_PROJECT' not in os.environ:
        current_projects = [str(child.stem) for child in Path("./Projects").iterdir()]
        print("Project options: ")
        print(current_projects)
        project_choice = input("Select project to work on. Enter 'None' for a new project. ")
        if project_choice not in current_projects:
            project_setup(input("Enter new project name: "), Path("./Projects"))
        else:
            choice_path = Path("./Projects") / project_choice
            switch_project(choice_path.with_suffix(".json"))
    elif args.default_counter:
        change_default(os.environ['ACTIVE_PROJECT'], args.default_counter)
    elif type(args.active_name) == int:
        inc_counter(None, os.environ['ACTIVE_PROJECT'], args.active_name)
    else:
        inc_counter(args.active_name, os.environ['ACTIVE_PROJECT'])

if __name__ == "__main__":
    main()
