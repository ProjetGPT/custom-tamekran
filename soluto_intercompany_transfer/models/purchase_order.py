# -*- coding: utf-8 -*-

from odoo import models, fields

class PurchaseOrder(models.Model):
    _inherit = 'purchase.order'

    source_sale_order_id = fields.Many2one(
        'sale.order',
        string='Source Sale Order',
        readonly=True,
        copy=False,
        help='The original sale order that triggered this intercompany purchase order.'
    )

    def action_view_source_sale_order(self):
        self.ensure_one()
        return {
            'type': 'ir.actions.act_window',
            'res_model': 'sale.order',
            'view_mode': 'form',
            'res_id': self.source_sale_order_id.id,
            'target': 'current',
            'context': self.env.context,
        }
