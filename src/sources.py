import yaml
import requests
import os


def get_edition():
  return os.environ.get('DESKTOP_SESSION').lower()

def remote_workflow():
  if get_edition() == "jde":
    return "https://raw.githubusercontent.com/Manjaro-WebDad/jde-wizard/master/software-workflow.yaml"

def get_remote_source(remote):
    try:
        response = requests.get(remote, headers={'Cache-Control': 'no-cache'})
        return response.text
    except Exception as err:
        print(err)

def load_yaml(source=None):
  source = get_remote_source(remote_workflow())
  if source:
    return yaml.load(source, Loader=yaml.FullLoader)
  else:
    return None
  

    
