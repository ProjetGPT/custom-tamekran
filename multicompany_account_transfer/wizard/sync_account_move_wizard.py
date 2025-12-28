# -*- coding: utf-8 -*-

from odoo import models, fields


class SyncAccountMoveWizard(models.Model):
    _name = 'sync.account.move.wizard'

    date_from = fields.Date('Date From')
    date_to = fields.Date('Date To')
    source_company_id = fields.Many2one('res.company')
    sync_move_delete = fields.Boolean('Sync Move Delete', default=False)
    error_log = fields.Text('Error Log')

    def action_generate(self):
        journals = self.env['account.journal'].sudo().search([
            ('company_id', '=', self.source_company_id.id),
            ('is_sync_multicompany', '=', True)
        ])
        destination_company_ids = journals.mapped('destination_company_id').ids

        if self.sync_move_delete:
            self.env['account.move'].sudo().search([
                ('company_id', 'in', destination_company_ids),
                ('date', '>=', self.date_to),
                ('date', '<=', self.date_from),
                ('destination_move_id', '!=', False)
            ]).unlink()

        moves = self.env['account.move'].sudo().search([
            ('company_id', '=', self.source_company_id.id),
            ('date', '>=', self.date_to),
            ('date', '<=', self.date_from),
            ('journal_id', 'in', journals.ids),
            ('destination_move_id', '=', False),
            ('state', '=', 'posted')
        ])
        error_log = []
        for move in moves:
            res = move._sync_move(True)
            if res:
                error_log.append("Move Id:%s - Move Name:%s - Error:%s" % (move.id, move.name, res))

        self.error_log = False

        if len(error_log) > 0:
            self.error_log = "\n".join(error_log)
            return {
                'type': 'ir.actions.act_window',
                'view_mode': 'form',
                'res_model': 'sync.account.move.wizard',
                'target': 'new',
                'res_id': self.id
            }
