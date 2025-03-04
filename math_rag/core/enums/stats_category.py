from enum import Enum


class StatisticsCategory(str, Enum):
    AP = 'applications'
    CO = 'computation'
    ME = 'methodology'
    ML = 'machine_learning'
    OT = 'other_statistics'
    TH = 'statistics_theory'
