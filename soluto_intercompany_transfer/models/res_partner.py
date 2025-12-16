# -*- coding: utf-8 -*-

from odoo import models, fields


class ResPartner(models.Model):
    _inherit = 'res.partner'

    is_intercompany_partner = fields.Boolean(
        string='Is Intercompany Trigger Partner',
        help='Check this box if this partner is used to trigger intercompany operations.'
    )
    target_company_id = fields.Many2one(
        'res.company',
        string='Target Company',
        help='The company where the new orders will be created.'
    )
