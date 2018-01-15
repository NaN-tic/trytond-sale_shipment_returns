# This file is part sale_shipment_returns module for Tryton.
# The COPYRIGHT file at the top level of this repository contains
# the full copyright notices and license terms.
from trytond.pool import Pool
from .shipment import *

def register():
    Pool.register(
        CreateSaleReturn,
        module='sale_shipment_returns', type_='wizard')
