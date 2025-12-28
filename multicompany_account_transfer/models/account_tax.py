# -*- coding: utf-8 -*-

from odoo import models, api


class AccountTax(models.Model):
    _inherit = 'account.tax'

    @api.model
    def sync_tax_multi_company(self, dest_company_id, src_tax_id):
        tax = self.env['account.tax'].sudo().browse(src_tax_id)

        dest_tax = self.search([
            ('name', '=ilike', tax.name),
            ('company_id', '=', dest_company_id)
        ], limit=1)
        if dest_tax:
            return dest_tax.id

        vals = tax.copy_data({'company_id': dest_company_id})[0]
        dest_tax = self.with_company(dest_company_id).sudo().create(vals)
        if dest_tax:
            return dest_tax.id
        return False
