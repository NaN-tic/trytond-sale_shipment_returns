# This file is part sale_shipment_returns module for Tryton.
# The COPYRIGHT file at the top level of this repository contains
# the full copyright notices and license terms.
try:
    from trytond.modules.sale_shipment_returns.tests.test_sale_shipment_returns import suite
except ImportError:
    from .test_sale_shipment_returns import suite

__all__ = ['suite']
