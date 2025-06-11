from enum import StrEnum


class ChangeModePermission(StrEnum):
    READ = '+r'
    WRITE = '+w'
    EXECUTE = '+x'

    REMOVE_READ = '-r'
    REMOVE_WRITE = '-w'
    REMOVE_EXECUTE = '-x'
