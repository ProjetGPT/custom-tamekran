# -*- coding: utf-8 -*-

from odoo import models, api


class AccountTaxRepartitionLine(models.Model):
    _inherit = 'account.tax.repartition.line'

    @api.model
    def sync_tax_repartition_multi_company(self, dest_company_id, src_id):
        tax_r = self.env['account.tax.repartition.line'].sudo().browse(src_id)
        if tax_r.invoice_tax_id:
            src_tax = self.env['account.tax'].sudo().browse(tax_r.invoice_tax_id.id)
            dest_tax = self.env['account.tax'].sudo().search([
                ('name', '=ilike', src_tax.name),
                ('company_id', '=', dest_company_id)
            ], limit=1)

            dest_tax_r = self.search([
                ('invoice_tax_id', '=', dest_tax.id),
                ('refund_tax_id', '=', False),
                ('company_id', '=', dest_company_id),
                ('repartition_type', '=', tax_r.repartition_type)
            ], limit=1)
            if dest_tax_r:
                return dest_tax_r.id

        if tax_r.refund_tax_id:
            src_tax = self.env['account.tax'].sudo().browse(tax_r.refund_tax_id.id)
            dest_tax = self.env['account.tax'].sudo().search([
                ('name', '=ilike', src_tax.name),
                ('company_id', '=', dest_company_id)
            ], limit=1)
            dest_tax_r = self.search([
                ('refund_tax_id', '=', dest_tax.id),
                ('invoice_tax_id', '=', False),
                ('company_id', '=', dest_company_id),
                ('repartition_type', '=', tax_r.repartition_type)
            ], limit=1)
            if dest_tax_r:
                return dest_tax_r.id

        return False
