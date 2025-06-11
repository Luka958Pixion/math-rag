from enum import StrEnum


class ChangeModePermission(StrEnum):
    READ = 'a+r'
    WRITE = 'a+w'
    EXECUTE = 'a+x'

    REMOVE_READ = 'a-r'
    REMOVE_WRITE = 'a-w'
    REMOVE_EXECUTE = 'a-x'
