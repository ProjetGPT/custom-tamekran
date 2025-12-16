# -*- coding: utf-8 -*-

from odoo import models, fields, api, _


class VehiclePlate(models.Model):
    _name = 'vehicle.plate'
    _description = 'Araç Plaka Kayıtları'
    _order = 'name'
    
    name = fields.Char(
        string='Plaka',
        required=True,
        index=True
    )
    
    driver_name = fields.Char(
        string='Sürücü Adı Soyadı',
        help='Bu plakaya atanmış varsayılan sürücü'
    )
    
    vehicle_tare_weight = fields.Float(
        string='Araç Dara (KG)',
        digits=(16, 2),
        help='Kamyonun boş ağırlığı (dara)'
    )
    
    active = fields.Boolean(
        string='Aktif',
        default=True
    )
    
    note = fields.Text(
        string='Not'
    )
    
    _sql_constraints = [
        ('name_uniq', 'unique (name)', 'Bu plaka zaten sistemde kayıtlı!')
    ]
