from src.utils import load_config

config = load_config('src/configs/configs.yaml')['config']


class FlaskConfig:
    SQLALCHEMY_DATABASE_URI = config['SQLALCHEMY_DATABASE_URI']
    DEBUG = True
