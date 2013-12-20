#:after:stock/stock:section:movimientos#

Crear ventas de devolución
==========================

Si ha realizados un albarán de devolución de cliente, y desea abonar este
ya que finalmente no se realiza la entrega, deberá crear una venta de devolución
(unidades negativas) y esta realizar la correspondiente factura de abono de cliente.

Desde los albaranes de devolución dispone de un asistente que le permite generar
una venta a partir del albarán de devolución. Para crear una venta de devolución
el albarán de devolución debe de estar en el estado de "Realizado".

Esta venta es una copia del albarán de devolución pero con una grande diferencia:
las líneas de la venta serán en negativo para realizar una devolución.

Para que se nos genere la factura de devolución simplemente procesamos la venta para
realizarla. Los albaranes de devolución ya están creados y sólo creará la factura de
abono de cliente.

Si en esta venta que disponemos de cantidades negativas añadimos nuevas líneas con
cantidades positivas, las cantidades positivas nos generarán nuevos albaranes, en este
caso, albaranes de cliente (y posteriormente facturas de cliente).
