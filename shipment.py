# This file is part sale_shipment_returns module for Tryton.
# The COPYRIGHT file at the top level of this repository contains
# the full copyright notices and license terms.
from trytond.pool import Pool, PoolMeta
from trytond.wizard import Wizard, StateAction
from trytond.transaction import Transaction

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
                'shipment_done_msg': ('The return shipment with code "%s" is '
                    'not yet sent.'),
                'shipment_description': ('Shipment Out Return "%s"'),
                'shipment_out_origin': ('Shipment Out Return "%s" origin does '
                    'not come from a Shipment Out'),
                })

    def do_start(self, action):
        pool = Pool()
        ShipmentOut = pool.get('stock.shipment.out')
        ShipmentOutReturn = pool.get('stock.shipment.out.return')
        Sale = pool.get('sale.sale')
        SaleLine = pool.get('sale.line')
        Move = pool.get('stock.move')

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
                (shipment_out_return.code), raise_exception=False)

            # create sale and lines from moves, and new origin move
            sale = Sale.get_sale_data(party, description)
            sale.shipment_address = shipment_out_return.delivery_address

            lines = []
            moves_to_save = []
            if isinstance(shipment_out_return.origin, ShipmentOut):
                outgoing_move_products = {m.product: m.origin
                    for m in shipment_out_return.origin.outgoing_moves
                    if hasattr(m, 'origin') and isinstance(m.origin, SaleLine)}
                for move in shipment_out_return.incoming_moves:
                    if move.product in outgoing_move_products:
                        line, = SaleLine.copy(
                            [outgoing_move_products[move.product]],
                            {'quantity': -move.quantity})
                        lines.append(line)
                        move.origin = 'sale.line,%s' % line.id
                        moves_to_save.append(move)
            if not lines:
                self.raise_user_error('shipment_out_origin', (
                    shipment_out_return.rec_name,))
            sale.lines = lines
            sales.append(sale)

        if sales:
            Sale.save(sales)
        if moves_to_save:
            Move.save(moves_to_save)

        data = {'res_id': [x.id for x in sales]}
        if len(sales) == 1:
            action['views'].reverse()
        return action, data

    def transition_start(self):
        return 'end'
