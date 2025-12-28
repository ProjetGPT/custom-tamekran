# -*- coding: utf-8 -*-

from odoo import _, api, fields, models


class SaleAdvancePaymentInv(models.TransientModel):
    _inherit = "sale.advance.payment.inv"

    @api.model
    def default_get(self, fields_list):
        defaults = super(SaleAdvancePaymentInv, self).default_get(fields_list)
        active_ids = self._context["active_ids"]
        if active_ids:
            order = self.env["sale.order"].browse(self._context.get("active_ids"))[0]
            if order and order.so_type_id:
                journal_id = order.so_type_id.journal_id
                if journal_id:
                    defaults["journal_id"] = journal_id.id
        return defaults
