#This file is part sale_shipment_returns module for Tryton.
#The COPYRIGHT file at the top level of this repository contains 
#the full copyright notices and license terms.
from trytond.model import fields
from trytond.pool import Pool, PoolMeta

__all__ = ['Sale']
__metaclass__ = PoolMeta


class Sale:
    __name__ = 'sale.sale'
    shipment_out_returns = fields.Function(fields.One2Many('stock.shipment.out.return', None,
        'Shipment Returns from Shipment Out'), 'get_shipment_out_returns')

    def get_shipment_out_returns(self, name):
        pool = Pool()
        ShipmentOutReturn = pool.get('stock.shipment.out.return')

        shipments = []
        if self.shipments:
            shipments_returns = ShipmentOutReturn.search([
                ('origin_shipment', 'in', self.shipments),
                ])
            if shipments_returns:
                shipments = [x.id for x in shipments_returns]
        return shipments
