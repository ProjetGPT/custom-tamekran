# -*- coding: utf-8 -*-

from odoo import models


class AccountFiscalPosition(models.Model):
    _inherit = 'account.fiscal.position'

    def sync_fiscal_position_multi_company(self, dest_company_id, src_fp_id):
        source_fp = self.env['account.fiscal.position'].sudo().browse(src_fp_id)

        dest_fiscal_position = self.env['account.fiscal.position'].sudo().search([
            ('name', '=', source_fp.name),
            ('company_id', '=', dest_company_id)
        ], limit=1)

        if dest_fiscal_position:
            return dest_fiscal_position.id
        else:
            return self.env['account.fiscal.position'].sudo().create({
                'name': source_fp.name,
                'company_id': dest_company_id,
            }).id
