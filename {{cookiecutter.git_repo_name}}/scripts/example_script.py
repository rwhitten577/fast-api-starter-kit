from src.core.script import Script
from src.orm.session import SessionLocal


class Example(Script):
    def __init__(self, args=None):
        super(Example, self).__init__(args)

    def add_args(self):
        pass

    def run(self):
        session = SessionLocal()
        session.add_all([])
        session.commit()


if __name__ == "__main__":
    import sys

    cmd = Example(sys.argv[1:])
    sys.exit(cmd())
