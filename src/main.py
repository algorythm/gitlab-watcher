from config import get_env

def main(config_path: str):
    config = get_env(config_path)

if __name__ == '__main__':
    main('../env.yml')
