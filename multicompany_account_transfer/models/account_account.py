# -*- coding: utf-8 -*-

from odoo import models, fields, api


class AccountAccount(models.Model):
    _inherit = 'account.account'

    @api.model
    def sync_account_multi_company(self, dest_company_id, src_account_id):
        source_account = self.env['account.account'].sudo().browse(src_account_id)

        dest_account = self.search([
            ('code', '=ilike', source_account.code),
            ('company_id', '=', dest_company_id)
        ], limit=1)
        if dest_account:
            return dest_account.id

        vals = source_account.copy_data({
            'company_id': dest_company_id
        })[0]

        if vals.get('tax_ids'):
            AccountTax = self.env['account.tax'].sudo()
            for tax in vals.get('tax_ids'):
                for _idx, tax_val in enumerate(tax[2]):
                    if tax_val:
                        tax[2][_idx] = AccountTax.sync_tax_multi_company(dest_company_id, tax_val)

        dest_account = self.with_company(dest_company_id).sudo().create(vals)

        if dest_account:
            return dest_account.id
        return False
