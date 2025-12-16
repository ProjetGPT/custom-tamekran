# -*- coding: utf-8 -*-

from odoo import models, fields, api, _

class SelectProductionVehicles(models.TransientModel):
    _name = 'select.production.vehicles'
    _description = 'Üretimden Araç Seçme Sihirbazı'

    picking_id = fields.Many2one('stock.picking', readonly=True)
    available_vehicle_weight_ids = fields.Many2many(
        'vehicle.weight',
        string='Seçilebilir Araçlar',
        compute='_compute_available_vehicles',
        domain="[('picking_id', '=', False)]"
    )
    selected_vehicle_weight_ids = fields.Many2many(
        'vehicle.weight',
        'select_production_vehicles_vehicle_weight_rel',
        'wizard_id', 'vehicle_weight_id',
        string='Seçilen Araçlar'
    )

    @api.depends('picking_id')
    def _compute_available_vehicles(self):
        self.ensure_one()
        sale_order = None
        if self.picking_id and self.picking_id.origin:
            # stock.picking modelindeki 'origin' alanının satış siparişi adını içerdiği varsayılır
            sale_order = self.env['sale.order'].search([('name', '=', self.picking_id.origin)], limit=1)
        
        if not sale_order:
            self.available_vehicle_weight_ids = []
            return

        # Find production orders linked to the sale order
        production_orders = self.env['mrp.production'].search([('origin', 'ilike', sale_order.name)])

        if not production_orders:
            self.available_vehicle_weight_ids = []
            return

        # Find vehicle weights linked to those production orders that are not yet linked to a picking
        available_vehicles = self.env['vehicle.weight'].search([
            ('production_id', 'in', production_orders.ids),
            ('picking_id', '=', False)
        ])
        self.available_vehicle_weight_ids = available_vehicles

    def action_select_vehicles(self):
        self.ensure_one()
        if self.selected_vehicle_weight_ids:
            # Link the selected vehicles to the current picking
            self.picking_id.vehicle_weight_ids |= self.selected_vehicle_weight_ids
        return {'type': 'ir.actions.act_window_close'}
