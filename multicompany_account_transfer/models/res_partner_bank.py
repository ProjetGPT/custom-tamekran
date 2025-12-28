# -*- coding: utf-8 -*-

from odoo import models, fields, api, _


class ResPartnerBank(models.Model):
    _inherit = 'res.partner.bank'

    def sync_partner_bank_multi_company(self, dest_company_id, partner_bank_id):
        if not partner_bank_id:
            return False

        partner_bank = self.env['res.partner.bank'].sudo().browse(partner_bank_id)

        dest_partner_bank = self.env['res.partner.bank'].search([
            ('company_id', '=', dest_company_id),
            ('acc_number', '=', partner_bank.acc_number)
        ], limit=1)

        if dest_partner_bank:
            return dest_partner_bank.id

        return self.env['res.partner.bank'].sudo().create({
            'partner_id': partner_bank.partner_id.id,
            'company_id': dest_company_id,
            'acc_number': partner_bank.acc_number,
        }).id
