from typing import NamedTuple, Tuple


class Config(NamedTuple):
    address: str
    username: str
    password: str

    @property
    def auth(self) -> Tuple[str, str]:
        return (self.username, self.password)
