from dataclasses import dataclass


@dataclass
class ServerConfig:
    SERVER: int = 973851473131761674

    @dataclass
    class Channels:
        INTRODUCTION_CHANNEL: int = 1107343423167541328

    @dataclass
    class Roles:
        CONTRIBUTOR_ROLE: int = 973852365188907048

        @classmethod
        def isCollegeChapter(roleName: str) -> bool:
            return True if roleName.startswith("College:") else False
