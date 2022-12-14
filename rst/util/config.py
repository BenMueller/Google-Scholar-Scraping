import configparser, os

class Config:

    _instance = None

    def __new__(cls, *args, **kwargs):
        if not cls._instance:
            cls._instance = super(Config, cls).__new__(cls)
        return cls._instance

    def __init__(self, config_file = None, config_opts = None):
        if config_file is None:
            config = configparser.ConfigParser()
            config['DEFAULT'] = {'WebDriver': 'Chrome',
                                 'DownloadDir': 'Downloads',
                                 'TimeOut': '60',
                                 'Languages': 'en',
                                 'AllowBrokenSSL': False,
                                 'Blacklist': True, #ignore known broken domains. Disable for testing.
                                 'Slash': '/'
                                 }
        else:
            assert os.path.exists(config_file)
            config.read_file(open(config_file))

        if config_opts is not None:
            for entry in config_opts:
                config.set(entry)

        Config._CONFIG = config

    @staticmethod
    def get_config() -> configparser:
        if Config._CONFIG is None:
            Config.__init__()
        return Config._CONFIG['DEFAULT']