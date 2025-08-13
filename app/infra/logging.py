import logging, sys


def configure_logging() -> None:
    handler = logging.StreamHandler(sys.stdout)
    fmt = logging.Formatter(
        '{"level":"%(levelname)s","ts":"%(asctime)s","logger":"%(name)s","msg":"%(message)s"}'
    )
    handler.setFormatter(fmt)
    root = logging.getLogger()
    root.setLevel(logging.INFO)
    root.handlers.clear()
    root.addHandler(handler)
