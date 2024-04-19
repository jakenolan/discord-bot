import json
from pathlib import Path


# Used for read and write json functions
def get_path():
    cwd = Path(__file__).parents[1]
    cwd = str(cwd)
    return cwd


# Global read json function
def read_json(filename):
    cwd = get_path()
    with open(cwd+'/config/'+filename+'.json', 'r') as file:
        data = json.load(file)
    return data


# Global write json function
def write_json(data, filename):
    cwd = get_path()
    with open(cwd+'/config/'+filename+'.json', 'w') as file:
        json.dump(data, file, indent=4)