import multiprocessing

from .settings import Settings
from .spot import SpotState
from .logger import log
from .web import run_server


if __name__ == "__main__":
    log.info("start")

    settings = Settings()

    log.info(f"load settings, {settings=}")

    manager = multiprocessing.Manager()
    context = multiprocessing.get_context("spawn")

    spot_state: SpotState = manager.dict()
    spot_state.setdefault("battery", None)

    web_server_proc = context.Process(
        target=run_server,
        args=(
            settings,
            spot_state,
        )
    )

    web_server_proc.start()
    web_server_proc.join()
