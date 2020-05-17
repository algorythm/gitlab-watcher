from src.config import get_env
from src.gitlab import GitLab
from datetime import datetime
import time

def main(config_path: str):
    config = get_env(config_path)['gitlab']
    gl = GitLab(17170378, config['token'])

    # gl.list_users()

    while True:
        latest_tag = gl.latest_tag()
        print('latest tag:', latest_tag.name, end='')
        ci_status = gl.pipeline_status_for_tag(latest_tag.name)
        print('\tci status:', ci_status, end='')
        print('\t', datetime.now())
        time.sleep(6)


if __name__ == '__main__':
    main('env.yml')
