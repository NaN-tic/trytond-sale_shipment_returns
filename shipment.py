#This file is part sale_shipment_returns module for Tryton.
#The COPYRIGHT file at the top level of this repository contains 
#the full copyright notices and license terms.
from trytond.pool import Pool, PoolMeta
from trytond.wizard import Wizard, StateAction
from trytond.transaction import Transaction
from decimal import Decimal

__all__ = ['CreateSaleReturn']
__metaclass__ = PoolMeta


class CreateSaleReturn(Wizard):
    'Create Sale from Customer Return Shipment'
    __name__ = 'stock.sale.return.create'
    start = StateAction('sale.act_sale_form')

    @classmethod
    def __setup__(cls):
        super(CreateSaleReturn, cls).__setup__()
        cls._error_messages.update({
                'shipment_done_title': 'You can not create return sale',
                'shipment_done_msg': ('The return shipment with code "%s" is not yet '
                    'sent.'),
                'shipment_description': ('Shipment Out Return "%s"'),
                })

    def do_start(self, action):
        pool = Pool()
        ShipmentOutReturn = pool.get('stock.shipment.out.return')
        Sale = pool.get('sale.sale')
        SaleLine = pool.get('sale.line')

        shipment_ids = Transaction().context['active_ids']
        shipment_out_returns = ShipmentOutReturn.browse(shipment_ids)

        sales = []
        for shipment_out_return in shipment_out_returns:
            if shipment_out_return.state != 'done':
                self.raise_user_error('shipment_done_title',
                        error_description='shipment_done_msg',
                        error_description_args=shipment_out_return.code)

            party = shipment_out_return.customer
            description = self.raise_user_error('shipment_description',
                (shipment_out_return.code),raise_exception=False)

            # create sale
            sale = Sale.get_sale_data(party, description)
            sale.shipment_address = shipment_out_return.delivery_address
            sale.save()
            sales.append(sale)

            # create sale lines from moves
            lines = []
            for move in shipment_out_return.incoming_moves:
                product = move.product
                quantity = -move.quantity
                uom = move.uom.symbol
                line = SaleLine.get_sale_line_data(
                    sale, product, quantity, uom)

                unit_price = None
                if move.origin:
                    if hasattr(move.origin, 'unit_price'):
                        unit_price = move.origin.unit_price
                line.unit_price = unit_price or move.unit_price or Decimal('0.0')

                line.save()
                lines.append(line)

            # write stock move origin
            lines_to_move = []
            if lines:
                for line in lines:
                    lines_to_move.append({
                        'product': line.product,
                        'quantity': abs(line.quantity),
                        'id': line.id,
                        })
            if lines_to_move:
                for move in shipment_out_return.incoming_moves:
                    for l2m in lines_to_move:
                        if l2m['product'] == move.product and \
                                l2m['quantity'] == move.quantity:
                            move.origin = 'sale.line,%s' % l2m['id']
                            move.save()

        data = {'res_id': [x.id for x in sales]}
        if len(sales) == 1:
            action['views'].reverse()
        return action, data

    def transition_start(self):
        return 'end'
