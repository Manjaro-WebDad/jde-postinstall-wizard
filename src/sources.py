import yaml
import requests
import os


def get_edition():
  return os.environ.get('DESKTOP_SESSION').lower()

def remote_workflow():
  return "https://raw.githubusercontent.com/Manjaro-WebDad/jde-wizard/master/software-workflow.yaml"

def get_remote_source(source=remote_workflow()):
    try:
        resp = requests.get(source)
        return resp.text
    except requests.exceptions.HTTPError as err:
        print(err)

def load_yaml(source=get_remote_source()):
  return yaml.load(source, Loader=yaml.FullLoader)

    
