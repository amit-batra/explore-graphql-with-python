from enum import Enum


class Genre(str, Enum):
    FICTION = "fiction"
    NONFICTION = "nonfiction"
    SCI_FI = "sci-fi"
    POETRY = "poetry"
