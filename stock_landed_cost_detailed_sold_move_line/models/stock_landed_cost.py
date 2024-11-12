# -*- coding: utf-8 -*-
# Copyright © 2019 BulutKobi (https://www.bulutkobi.io)
# Part of BulutKobi Enterprise. See LICENSE file for full copyright and licensing details.

from odoo import models, _
from odoo.tools import  float_round


class StockLandedCost(models.Model):
    _inherit = 'stock.valuation.adjustment.lines'

    def _create_account_move_line(self, move_id, credit_account_id, debit_account_id, qty_out, already_out_account_id):
        """
        Generate the account.move.line values to track the landed cost.
        Afterwards, for the goods that are already out of stock, we should create the out moves
        """
        AccountMoveLine = []
        base_line = {
            'name': self.name,
            'product_id': self.product_id.id,
            'quantity': 0,
        }
        debit_line = dict(base_line, account_id=debit_account_id)
        credit_line = dict(base_line, account_id=credit_account_id)
        diff = self.additional_landed_cost
        curr_rounding = self.env.user.company_id.currency_id.rounding
        diff = float_round(diff, precision_rounding=curr_rounding)
        if diff > 0:
            debit_line['debit'] = diff
            credit_line['credit'] = diff
        else:
            # negative cost, reverse the entry
            debit_line['credit'] = -diff
            credit_line['debit'] = -diff
        AccountMoveLine.append([0, 0, debit_line])
        AccountMoveLine.append([0, 0, credit_line])

        rel_ids = self.env['stock.move.counter.move.rel'].search([('move_id', '=', self.move_id.id)])
        #Create account move lines for quants already out of stock
        if qty_out > 0:
            for i in rel_ids:
                move = i.counter_move_id
                if move.state == 'done' and move.partner_id and (move.location_dest_id.usage == 'customer' or move.location_id.usage == 'customer'):
                    origin = move.origin
                    product_qty = i.quantity
                    partner_id = move.partner_id.id
                    if move.location_dest_id.usage == 'customer':
                        # outgoing
                        debit_line = dict(debit_line,
                                          name=(self.name + ": " + str(qty_out) + _(' already out')),
                                          quantity=product_qty,
                                          account_id=already_out_account_id,
                                          partner_id=partner_id)
                        credit_line = dict(credit_line,
                                           name=(self.name + ": " + str(qty_out) + _(' already out')),
                                          quantity=product_qty,
                                          account_id=debit_account_id,
                                          partner_id=partner_id)
                    else:
                        # incoming
                        debit_line = dict(debit_line,
                                          name=(self.name + ": " + str(qty_out) + _(' already out')),
                                          quantity=product_qty,
                                          account_id=debit_account_id,
                                          partner_id=partner_id)
                        credit_line = dict(credit_line,
                                          name=(self.name + ": " + str(qty_out) + _(' already out')),
                                          quantity=product_qty,
                                          account_id=already_out_account_id,
                                          partner_id=partner_id)

                    diffx = diff * product_qty / self.quantity
                    diffx = float_round(diffx, precision_rounding=curr_rounding)
                    if diffx > 0:
                        debit_line['debit'] = diffx
                        credit_line['credit'] = diffx
                    else:
                        # negative cost, reverse the entry
                        debit_line['credit'] = -diffx
                        credit_line['debit'] = -diffx

                    AccountMoveLine.append([0, 0, debit_line])
                    AccountMoveLine.append([0, 0, credit_line])
        return AccountMoveLine
