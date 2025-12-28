# -*- coding: utf-8 -*-
import logging

from odoo import models, fields, _
from odoo.exceptions import ValidationError

_logger = logging.getLogger(__name__)


class AccountMove(models.Model):
    _inherit = 'account.move'

    destination_move_id = fields.Many2one('account.move', copy=False)

    def button_draft(self):
        res = super(AccountMove, self).button_draft()
        if self.destination_move_id:
            self.destination_move_id.sudo().unlink()
        return res

    def button_cancel(self):
        res = super(AccountMove, self).button_cancel()
        if self.destination_move_id:
            self.destination_move_id.sudo().unlink()
        return res

    def _sync_move(self, auto_commit=False):
        try:
            if not self.journal_id.is_sync_multicompany or not self.journal_id.destination_journal_id:
                return []

            dest_company_id = self.journal_id.destination_journal_id.company_id.id
            vals = self.with_context(sync_move=True).copy_data({
                'journal_id': self.journal_id.destination_journal_id.id,
                'company_id': dest_company_id,
                'sale_ids': False,
                'purchase_id': False,
            })[0]

            if hasattr(self, 'document_number'):
                vals.update({
                    'document_number': self.document_number
                })

            AccountAccount = self.env['account.account'].sudo()
            AccountTax = self.env['account.tax'].sudo()
            AccountTaxR = self.env['account.tax.repartition.line'].sudo()
            AccountFP = self.env['account.fiscal.position'].sudo()

            for line in vals.get('line_ids', []):
                line_val = line[2]

                if not line_val.get('account_id'):
                    continue

                if line_val.get('sale_order_id', False):
                    line_val.update(sale_order_id=False)
                if line_val.get('sale_line_id', False):
                    line_val.update(sale_line_id=False)

                if line_val.get('purchase_order_id', False):
                    line_val.update(purchase_order_id=False)
                if line_val.get('purchase_line_id', False):
                    line_val.update(purchase_line_id=False)

                line_val.update(move_id=False)
                line_val.update(account_id=AccountAccount.sync_account_multi_company(dest_company_id, line_val.get('account_id')))

                for tax in line_val.get('tax_ids'):
                    for _idx, tax_val in enumerate(tax[2]):
                        if tax_val:
                            tax[2][_idx] = AccountTax.sync_tax_multi_company(dest_company_id, tax_val)
                if line_val.get('tax_repartition_line_id', False):
                    accoun_tax_rep = AccountTaxR.sync_tax_repartition_multi_company(
                        dest_company_id,
                        line_val.get('tax_repartition_line_id')
                    )
                    if not accoun_tax_rep:
                        raise ValidationError(_('Tax Repartition Line not found %s:' % line_val.get('tax_repartition_line_id')))

                    line_val.update(tax_repartition_line_id=accoun_tax_rep)

            if vals.get('fiscal_position_id', False):
                fiscal_position_id = AccountFP.sync_fiscal_position_multi_company(
                    dest_company_id,
                    vals.get('fiscal_position_id')
                )
                vals.update({
                    'fiscal_position_id': fiscal_position_id or False
                })

            if vals.get('partner_bank_id', False):
                partner_bank_id = self.env['res.partner.bank'].sync_partner_bank_multi_company(
                    dest_company_id,
                    vals.get('partner_bank_id')
                )
                vals.update({
                    'partner_bank_id': partner_bank_id or False
                })

            vals.update({
                'name': self.name,
                'invoice_date': self.invoice_date,
                'date': self.date,
                'ref': self.ref,
                'invoice_date_due': self.invoice_date_due,
                'type_name': self.type_name,
                'user_id': self.user_id,
            })

            dest_move = self.with_company(dest_company_id).sudo().create(vals)
            if dest_move:
                self.destination_move_id = dest_move.id

            if auto_commit:
                self.env.cr.commit()
        except Exception as e:
            _logger.error("Multi Company Sync= %s" % str(e))
            self.env.cr.rollback()
            return str(e)

        return False
