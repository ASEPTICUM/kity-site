from typing import List, Dict


class CouldNotCreateUserException(Exception):
    def __init__(self, error: Dict[str, List[str]]):
        self.error = error


class CouldNotLoginUserException(Exception):
    def __init__(self, error: Dict[str, List[str]]):
        self.error = error
