# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import UserError


class StockPicking(models.Model):
    _inherit = 'stock.picking'

    vehicle_weight_ids = fields.One2many(
        'vehicle.weight', 
        'picking_id', 
        string='Araç Tonaj Bilgileri',
        copy=False
    )
    
    vehicle_count = fields.Integer(
        string='Araç Sayısı',
        compute='_compute_vehicle_count',
        store=True
    )
    
    total_exit_weight = fields.Float(
        string='Toplam Çıkış Tonajı (kg)',
        compute='_compute_total_weights',
        store=True,
        digits=(16, 2)
    )
    
    total_entry_weight = fields.Float(
        string='Toplam Giriş Tonajı (kg)',
        compute='_compute_total_weights',
        store=True,
        digits=(16, 2)
    )
    
    total_net_weight = fields.Float(
        string='Toplam Net Tonaj (kg)',
        compute='_compute_total_weights',
        store=True,
        digits=(16, 2)
    )
    
    @api.depends('vehicle_weight_ids')
    def _compute_vehicle_count(self):
        for record in self:
            record.vehicle_count = len(record.vehicle_weight_ids)
    
    @api.depends('vehicle_weight_ids.exit_weight', 'vehicle_weight_ids.entry_weight')
    def _compute_total_weights(self):
        for record in self:
            record.total_exit_weight = sum(record.vehicle_weight_ids.mapped('exit_weight'))
            record.total_entry_weight = sum(record.vehicle_weight_ids.mapped('entry_weight'))
            if record.picking_type_code == 'outgoing':
                record.total_net_weight = record.total_exit_weight - record.total_entry_weight
            else:
                record.total_net_weight = record.total_entry_weight - record.total_exit_weight
    
    def action_add_vehicle(self):
        """
        Action to add a new vehicle weight record
        """
        self.ensure_one()
        return {
            'name': _('Araç Tonaj Bilgisi Ekle'),
            'type': 'ir.actions.act_window',
            'view_mode': 'form',
            'res_model': 'vehicle.weight',
            'target': 'new',
            'context': {
                'default_picking_id': self.id,
            },
        }
    
    def action_view_vehicles(self):
        """
        Action to view all vehicle weight records for this picking
        """
        self.ensure_one()
        return {
            'name': _('Araç Tonaj Bilgileri'),
            'type': 'ir.actions.act_window',
            'view_mode': 'tree,form',
            'res_model': 'vehicle.weight',
            'domain': [('picking_id', '=', self.id)],
            'context': {
                'default_picking_id': self.id,
            },
        }
        
    def button_validate(self):
        """
        Override button_validate to update current_cost after delivery confirmation
        """
        result = super(StockPicking, self).button_validate()
        
        # After successful validation, update current_cost for all products in the delivery
        if result and self.state == 'done':
            products = self.move_ids.mapped('product_id')
            if products:
                # Teslimat içindeki ürünlerin bağlı olduğu ürün reçetelerindeki üretilecek ürünleri bul
                bom_products = self.env['product.product']
                
                # Tüm ürünler için BOM'ları kontrol et
                boms = self.env['mrp.bom'].search([
                    '|',
                    ('bom_line_ids.product_id', 'in', products.ids),
                    ('byproduct_ids.product_id', 'in', products.ids)
                ])
                
                # BOM'lardaki üretilecek ürünleri topla
                for bom in boms:
                    if bom.product_id:
                        bom_products |= bom.product_id
                    elif bom.product_tmpl_id:
                        bom_products |= bom.product_tmpl_id.product_variant_ids
                
                # Bulunan tüm ürünlerin güncel maliyetlerini güncelle
                if bom_products:
                    bom_products.update_current_cost()
                
        return result

    def action_open_vehicle_selection(self):
        self.ensure_one()
        return {
            'name': _('Üretimden Araç Seç'),
            'type': 'ir.actions.act_window',
            'view_mode': 'form',
            'res_model': 'select.production.vehicles',
            'target': 'new',
            'context': {
                'default_picking_id': self.id,
            },
        }
