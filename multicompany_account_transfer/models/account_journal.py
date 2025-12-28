# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import ValidationError


class AccountJournal(models.Model):
    _inherit = 'account.journal'

    is_sync_multicompany = fields.Boolean('Sync', default=False, copy=False)
    destination_company_id = fields.Many2one('res.company', copy=False)
    destination_journal_id = fields.Many2one('account.journal', copy=False)

    @api.constrains('destination_company_id')
    def _check_account_chart(self):
        for rec in self:
            if rec.destination_company_id and rec.destination_company_id.chart_template_id != rec.company_id.chart_template_id:
                raise ValidationError(_("Destination Company Account Chart Template Mismatch"))
