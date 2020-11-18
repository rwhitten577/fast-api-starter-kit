import argparse
import logging.config

from src.core.settings import Settings
from src.core.slack_connector import SlackConnector

logger = logging.getLogger(__name__)


class Script:
    def __init__(self, args=None):
        self.parser = argparse.ArgumentParser()
        self._configure_args()
        self.args = self.parser.parse_args(args or [])
        self.settings = Settings(self.args.config) if getattr(self.args, "config", None) else None
        self.slack_connector = SlackConnector(self.settings)

    def __call__(self, *args, **kwargs):
        try:
            return self.run()
        except Exception as e:
            msg = f"Generic error caught running ETL. Update code to catch this further down. {e}"
            logger.exception(msg)
            self.slack_connector.send_slack_alert(msg)

    def _configure_args(self):
        self.parser.add_argument(
            "--config", "-c", help="A .ini config file.", required=True, default=None
        )
        self.add_args()

    def add_args(self):
        """Override this to add script-specific arguments."""
        pass

    def run(self):
        pass
