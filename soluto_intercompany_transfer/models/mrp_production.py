# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import UserError

class MrpProduction(models.Model):
    _inherit = 'mrp.production'

    def button_mark_done(self):
        """Override button_mark_done to auto-validate related sale order deliveries"""
        res = super(MrpProduction, self).button_mark_done()
        
        # Check if this production is linked to a sale order
        if self.env.context.get('skip_backorder'):
            for production in self:
                if production.origin:
                    # Find sale orders that match this production origin
                    sale_orders = self.env['sale.order'].search([
                        ('name', '=', production.origin)
                    ])

                    for sale_order in sale_orders:
                        # Check if this is an intercompany sale order
                        if sale_order.partner_id.is_intercompany_partner:
                            production._auto_validate_sale_deliveries(sale_order)
        
        return res
    
    def _auto_validate_sale_deliveries(self, sale_order):
        """Auto-validate deliveries for the related sale order with vehicle weight transfer"""
        self.ensure_one()
        
        # Find outgoing pickings that are ready to be validated
        outgoing_pickings = sale_order.picking_ids.filtered(
            lambda p: p.picking_type_id.code == 'outgoing' and p.state not in ('done', 'cancelled')
        )
        
        for picking in outgoing_pickings:
            try:
                # Copy vehicle weight information from production to picking
                self._copy_production_vehicle_weights_to_picking(picking)
                
                # Set quantities based on production quantities
                self._set_picking_quantities_from_production(picking)
                
                # Ensure picking is assigned (reserved) before validation
                if picking.state != 'assigned':
                    picking.sudo().action_assign()
                
                # Validate the picking with intercompany context to avoid wizard
                picking.with_context(
                    skip_backorder=True, 
                    intercompany_confirmed=True
                ).sudo().button_validate()
                
                # Log the action
                picking.message_post(
                    body=_("Delivery automatically validated due to production completion: %s with vehicle weight transfer") % self.name
                )
                
            except Exception as e:
                raise UserError("Failed to auto-validate delivery %s: %s" % (picking.name, str(e))) from e

    def _set_picking_quantities_from_production(self, picking):
        """Set picking quantities based on production quantities"""
        self.ensure_one()
        
        # Map production products to picking moves
        for move in picking.move_ids:
            # Find matching production move
            production_move = self
            
            if production_move:
                # Set the quantity based on what was actually produced
                produced_qty = sum(production_move.mapped('qty_producing'))
                
                # Set the move quantity first
                move.quantity = min(produced_qty, move.product_uom_qty)
                
                # If no move lines exist, create them
                
                # Update move lines with the produced quantities
                remaining_qty = move.quantity
                for move_line in move.move_line_ids:
                    if move_line.product_id == move.product_id and remaining_qty > 0:
                        line_qty = min(remaining_qty, move_line.quantity or move_line.product_uom_qty)
                        move_line.quantity = line_qty
                        remaining_qty -= line_qty
                        
                        if remaining_qty <= 0:
                            break

                move._action_assign()
    
    def _copy_production_vehicle_weights_to_picking(self, picking):
        """Copy vehicle weight information from production to picking"""
        self.ensure_one()
        
        if not self.vehicle_weight_ids:
            return
            
        # Copy each vehicle weight record from production to picking
        for production_vehicle_weight in self.vehicle_weight_ids:
            # Create new vehicle weight record for the picking
            vals = {
                'picking_id': picking.id,
                'production_id': None,  # Clear production_id for picking record
                'vehicle_plate_id': production_vehicle_weight.vehicle_plate_id.id,
                'driver_name': production_vehicle_weight.driver_name,
                'vehicle_tare_weight': production_vehicle_weight.vehicle_plate_id.vehicle_tare_weight,
                'exit_m3': production_vehicle_weight.exit_m3,
                'exit_weight': production_vehicle_weight.exit_weight or 0,
                'exit_date': fields.Datetime.now(),
                'notes': production_vehicle_weight.notes,
                'parent_vehicle_weight_id': production_vehicle_weight.id,
                'intercompany_flow_stage': 'source_delivery',
                'source_sale_order_id': picking.sale_id.id if picking.sale_id else None,
            }
            
            # Create the vehicle weight record
            self.env['vehicle.weight'].create(vals)
            
        # Log the vehicle weight transfer
        picking.message_post(
            body=_("Vehicle weight information copied from production %s") % self.name
        )