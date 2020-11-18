import boto3
import logging.config
import os

from botocore.exceptions import ClientError
from configparser import ConfigParser, BasicInterpolation
from dotenv import find_dotenv, load_dotenv

logger = logging.getLogger(__name__)


class EnvironmentInterpolation(BasicInterpolation):
    def __init__(self):
        self.ssm = boto3.client("ssm", region_name="us-east-1")

    def before_get(self, parser, section, option, value, defaults):
        # If env variable is not set, try to fetch from SSM path, or return value.
        env_var = self._env_name(section, option)

        if env_var in os.environ:
            return os.environ.get(self._env_name(section, option))
        elif value.startswith("ssm:"):
            try:
                param = self.ssm.get_parameter(
                    Name=value.replace("ssm:", ""),
                    WithDecryption=True
                )

                if param.get("Parameter"):
                    return param["Parameter"]["Value"]
            except ClientError as e:
                # Best effort to load parameter
                logger.error(e)
        else:
            return os.path.expandvars(value)

    @classmethod
    def _env_name(cls, section, option):
        def munge(name):
            return name.upper().replace(".", "_")

        return "%s_%s" % (munge(section), munge(option))


class Settings:
    # Sections to ignore loading into this class, mainly logging config.
    _sections_to_load = {"DEFAULT", "slack"}

    def __init__(self, config_file=os.environ.get("PROJECT_SETTINGS", "local.ini")):
        if not os.path.exists(config_file):
            raise OSError("Could not load the default or provided settings file.")

        # Load from .env file if exists. Will set env variables for use in .ini files.
        load_dotenv(find_dotenv(".env", usecwd=True), verbose=True)

        self.parser = ConfigParser(interpolation=EnvironmentInterpolation())
        self.parser.optionxform = str
        self.parser.read(config_file)

        for section, items in self.parser.items():
            if section in self._sections_to_load:
                for key, value in items.items():
                    if section != "DEFAULT":
                        name = f"{section.upper()}_{key.upper()}"
                    else:
                        name = key.upper()
                    setattr(self, name, value)


settings = Settings()

logging.config.fileConfig(settings.parser, disable_existing_loggers=False)
