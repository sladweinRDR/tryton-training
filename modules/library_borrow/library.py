import datetime

from sql import Window
from sql.conditionals import Coalesce
from sql.aggregate import Count, Max

from trytond.pool import Pool
from trytond.transaction import Transaction
from trytond.model import ModelSQL, ModelView, fields
from trytond.model import Unique
from trytond.pyson import Eval, If, Bool


__all__ = [
    ]


