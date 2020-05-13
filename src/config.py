import os
import yaml

def get_env(path):
    if not os.path.isfile(path):
        raise Exception(f'"{path}" doesn\'t exist')

    with open(path) as file:
        return yaml.load(file, Loader=yaml.FullLoader)


if __name__ == '__main__':
    get_env('./env.yml')
