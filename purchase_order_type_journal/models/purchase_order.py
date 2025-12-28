# -*- coding: utf-8 -*-

from odoo import models, fields


class PurchaseOrder(models.Model):
    _inherit = 'purchase.order'

    def get_default_purchaseorder_type(self):
        journal = self.env['purchase.order.type'].search([('is_default', '=', True)], limit=1)
        return journal

    po_type_id = fields.Many2one("purchase.order.type",
                                 default=lambda self: self.get_default_purchaseorder_type(),
                                 string="Type")

    def action_create_invoice(self):
        ctx = {}
        if self.po_type_id and self.po_type_id.journal_id:
            ctx = {
                'default_journal_id': self.po_type_id.journal_id.id
            }
        return super(PurchaseOrder, self.with_context(ctx)).action_create_invoice()
