# -*- coding: utf-8 -*-

from odoo import models, fields

class MrpProduction(models.Model):
    _inherit = 'mrp.production'

    vehicle_weight_ids = fields.One2many(
        'vehicle.weight',
        'production_id',
        string='Araç Yükleme Bilgileri',
        copy=False
    )
