from odoo import models, fields, api
from odoo.addons.stock_account.models.stock_move import StockMove

class StoctMoveCounter(models.Model):
    _name = 'stock.move.counter.move.rel'

    move_id = fields.Many2one('stock.move', string='Move ID')
    counter_move_id = fields.Many2one('stock.move', string='Counter Move ID')
    quantity = fields.Float(string='Quantity')

class StockMoveQuant(models.Model):
    _inherit = 'stock.move'

def __run_fifo(self, move, quantity=None):

    move.ensure_one()

    # Deal with possible move lines that do not impact the valuation.
    valued_move_lines = move.move_line_ids.filtered(lambda
                                                        ml: ml.location_id._should_be_valued() and not ml.location_dest_id._should_be_valued() and not ml.owner_id)
    valued_quantity = 0
    for valued_move_line in valued_move_lines:
        valued_quantity += valued_move_line.product_uom_id._compute_quantity(valued_move_line.qty_done,
                                                                             move.product_id.uom_id)

    # Find back incoming stock moves (called candidates here) to value this move.
    qty_to_take_on_candidates = quantity or valued_quantity
    candidates = move.product_id._get_fifo_candidates_in_move()
    new_standard_price = 0
    tmp_value = 0  # to accumulate the value taken on the candidates
    for candidate in candidates:
        new_standard_price = candidate.price_unit
        if candidate.remaining_qty <= qty_to_take_on_candidates:
            qty_taken_on_candidate = candidate.remaining_qty
        else:
            qty_taken_on_candidate = qty_to_take_on_candidates

        # As applying a landed cost do not update the unit price, naivelly doing
        # something like qty_taken_on_candidate * candidate.price_unit won't make
        # the additional value brought by the landed cost go away.
        candidate_price_unit = candidate.remaining_value / candidate.remaining_qty
        value_taken_on_candidate = qty_taken_on_candidate * candidate_price_unit
        candidate_vals = {
            'remaining_qty': candidate.remaining_qty - qty_taken_on_candidate,
            'remaining_value': candidate.remaining_value - value_taken_on_candidate,
        }
        candidate.write(candidate_vals)

        self.env['stock.move.counter.move.rel'].create({'move_id': candidate.id, 'counter_move_id': move.id,
                                                        'quantity': qty_taken_on_candidate})
        self.env['stock.move.counter.move.rel'].create({'move_id': move.id, 'counter_move_id': candidate.id,
                                                        'quantity': qty_taken_on_candidate})
        qty_to_take_on_candidates -= qty_taken_on_candidate
        tmp_value += value_taken_on_candidate
        if qty_to_take_on_candidates == 0:
            break

    # Update the standard price with the price of the last used candidate, if any.
    if new_standard_price and move.product_id.cost_method == 'fifo':
        move.product_id.sudo().with_context(force_company=move.company_id.id) \
            .standard_price = new_standard_price

    # If there's still quantity to value but we're out of candidates, we fall in the
    # negative stock use case. We chose to value the out move at the price of the
    # last out and a correction entry will be made once `_fifo_vacuum` is called.
    if qty_to_take_on_candidates == 0:
        move.write({
            'value': -tmp_value if not quantity else move.value or -tmp_value,
        # outgoing move are valued negatively
            'price_unit': -tmp_value / (move.product_qty or quantity),
        })
    elif qty_to_take_on_candidates > 0:
        last_fifo_price = new_standard_price or move.product_id.standard_price
        negative_stock_value = last_fifo_price * -qty_to_take_on_candidates
        tmp_value += abs(negative_stock_value)
        vals = {
            'remaining_qty': move.remaining_qty + -qty_to_take_on_candidates,
            'remaining_value': move.remaining_value + negative_stock_value,
            'value': -tmp_value,
            'price_unit': -1 * last_fifo_price,
        }
        move.write(vals)
    return tmp_value

StockMove._run_fifo = __run_fifo