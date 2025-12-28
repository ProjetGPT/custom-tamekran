# -*- coding: utf-8 -*-

from odoo import _, api, fields, models


class SaleAdvancePaymentInv(models.TransientModel):
    _inherit = "sale.advance.payment.inv"

    journal_id = fields.Many2one("account.journal", string="Journal", domain="[('type', '=', 'sale')]")
    order_id = fields.Many2one("sale.order")

    @api.model
    def default_get(self, fields_list):
        defaults = super(SaleAdvancePaymentInv, self).default_get(fields_list)

        if self._context.get("active_ids"):
            order = self.env["sale.order"].browse(self._context.get("active_ids"))[0]
            defaults["order_id"] = order.id

            if "journal_id" in fields_list:
                journal = order.team_id.journal_id
                if not defaults.get('journal_id', False) and journal:
                    defaults["journal_id"] = journal.id
                elif not defaults.get('journal_id', False) and not journal:
                    company_id = self._context.get("company_id", self.env.user.company_id.id)
                    domain = [("type", "=", "sale"), ("company_id", "=", company_id)]
                    journal = self.env["account.journal"].search(domain, limit=1)
                    defaults["journal_id"] = journal.id
        return defaults

    def create_invoices(self):
        new_self = self.with_context(default_journal_id=self.journal_id.id)
        return super(SaleAdvancePaymentInv, new_self).create_invoices()

    def _create_invoice(self, order, so_line, amount):
        new_self = self.with_context(default_journal_id=self.journal_id.id)
        invoice = super(SaleAdvancePaymentInv, new_self)._create_invoice(order, so_line, amount)
        return invoice
