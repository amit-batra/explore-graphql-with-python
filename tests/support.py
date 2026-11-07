import logging


def step(log: logging.Logger, message: str) -> None:
    log.info(message)


def verify(log: logging.Logger, label: str, observed, expected) -> None:
    log.info(
        f"verify {label}: expected={expected!r} observed={observed!r}"
    )
    assert observed == expected, (
        f"{label} failed: expected {expected!r} but observed {observed!r}"
    )


def verify_true(log: logging.Logger, label: str, condition: bool) -> None:
    log.info(f"verify {label}: condition={condition!r}")
    assert condition, f"{label} failed: expected True but observed {condition!r}"


def verify_false(log: logging.Logger, label: str, condition: bool) -> None:
    log.info(f"verify {label}: condition={condition!r}")
    assert not condition, (
        f"{label} failed: expected False but observed {condition!r}"
    )
