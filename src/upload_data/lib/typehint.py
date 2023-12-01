import pandas as pd
from typing import List


class HintDataFrame(pd.DataFrame):
    __class_getitem__ = classmethod(type(List[str]))
