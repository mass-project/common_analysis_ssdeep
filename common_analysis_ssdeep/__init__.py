__version__ = '0.1'

from .ssdeep_analysis import CommonAnalysisSsdeep
from .ssdeep_analysis import n_grams

__all__ = [
        'CommonAnalysisSsdeep',
        'n_grams',
        ]

analysis_class = CommonAnalysisSsdeep
