# This file is part sale_shipment_returns module for Tryton.
# The COPYRIGHT file at the top level of this repository contains
# the full copyright notices and license terms.
from trytond.pool import Pool
from trytond.wizard import Wizard, StateAction
from trytond.transaction import Transaction
from trytond.i18n import gettext
from trytond.exceptions import UserError

__all__ = ['CreateSaleReturn']


class CreateSaleReturn(Wizard):
    'Create Sale from Customer Return Shipment'
    __name__ = 'stock.sale.return.create'
    start = StateAction('sale.act_sale_form')

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
                raise UserError(gettext(
                    'sale_shipment_returns.msg_shipment_done_title',
                        shipment=shipment_out_return.number))

            sale_origin = None
            if isinstance(shipment_out_return.origin, ShipmentOut):
                shipment_out = shipment_out_return.origin
                if isinstance(shipment_out.origin, Sale):
                    sale_origin = shipment_out.origin

            if sale_origin:
                party = sale_origin.party
            else:
                party = shipment_out_return.customer
            description = gettext('sale_shipment_returns.msg_shipment_description',
                shipment=shipment_out_return.number)

            # create sale and lines from moves, and new origin move
            sale = Sale.get_sale_data(party, description)

            # add shipment_party when delivery address party
            # is not the same as the customer
            delivery_address = shipment_out_return.delivery_address
            if delivery_address.party and (delivery_address.party != party):
                sale.shipment_party = delivery_address.party
            sale.shipment_address = delivery_address

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
                raise UserError(
                    gettext('sale_shipment_returns.msg_shipment_out_origin',
                    shipment=shipment_out_return.rec_name))

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
