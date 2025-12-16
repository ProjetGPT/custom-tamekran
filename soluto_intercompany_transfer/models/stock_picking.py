# -*- coding: utf-8 -*-

import logging
from odoo import models, fields, api, _
from odoo.fields import Command
from odoo.exceptions import UserError

_logger = logging.getLogger(__name__)

class StockPicking(models.Model):
    _inherit = 'stock.picking'

    def button_validate(self):
        """Override button_validate to handle intercompany delivery confirmations"""
        # Check if this is linked to an intercompany order
        for picking in self:
            if self.sudo()._is_intercompany_linked_picking() and not self.env.context.get('intercompany_confirmed'):
                return {
                    'type': 'ir.actions.act_window',
                    'name': _('Intercompany Confirmation'),
                    'res_model': 'confirm.intercompany.picking',
                    'view_mode': 'form',
                    'target': 'new',
                    'context': {'default_picking_id': picking.id}
                }
        
        res = super(StockPicking, self).button_validate()
        
        # Check if this is a delivery from an intercompany sale order
        for picking in self:
            if picking.sale_id and picking.sale_id.partner_id.is_intercompany_partner:
                picking._handle_intercompany_delivery_confirmation()
        
        return res

    def _is_intercompany_linked_picking(self):
        """Check if picking is linked to an intercompany order"""
        self.ensure_one()
        # Check sale order link (this picking is from an intercompany sale order)
        if self.sale_id and self.sale_id.source_sale_order_id:
            return True
        # Check purchase order link (this picking is from an intercompany purchase order)
        if self.purchase_id and self.purchase_id.source_sale_order_id:
            return True
        return False

    def _update_intercompany_po_prices(self, intercompany_po):
        """Update intercompany purchase order prices based on source picking unit costs"""
        self.ensure_one()
        
        # Create a mapping of product_id to unit_cost from source picking moves
        product_unit_costs = {}
        for move in self.move_ids_without_package:
            if move.product_id and hasattr(move, 'stock_valuation_layer_ids'):
                # Get the unit cost from valuation layers
                valuation_layers = move.stock_valuation_layer_ids
                if valuation_layers:
                    # Use the latest valuation layer's unit cost
                    latest_layer = valuation_layers.sorted('create_date', reverse=True)[0]
                    if latest_layer.unit_cost:
                        product_unit_costs[move.product_id.id] = abs(latest_layer.unit_cost)
        
        # Update purchase order line prices
        if product_unit_costs:
            for po_line in intercompany_po.sudo().order_line:
                if po_line.product_id.id in product_unit_costs:
                    unit_cost = product_unit_costs[po_line.product_id.id]
                    po_line.sudo().write({'price_unit': unit_cost})
                    _logger.info(
                        "Updated PO line price for product %s: %s -> %s",
                        po_line.product_id.name,
                        po_line.price_unit,
                        unit_cost
                    )

    def _update_intercompany_so_prices(self, sale_order):
        """Update sale order prices based on source picking unit costs"""
        self.ensure_one()
        
        # Create a mapping of product_id to unit_cost from source picking moves
        product_unit_costs = {}
        for move in self.move_ids_without_package:
            if move.product_id and hasattr(move, 'stock_valuation_layer_ids'):
                # Get the unit cost from valuation layers
                valuation_layers = move.stock_valuation_layer_ids
                if valuation_layers:
                    # Use the latest valuation layer's unit cost
                    latest_layer = valuation_layers.sorted('create_date', reverse=True)[0]
                    if latest_layer.unit_cost:
                        product_unit_costs[move.product_id.id] = abs(latest_layer.unit_cost)
        
        # Update sale order line prices
        if product_unit_costs:
            for so_line in sale_order.sudo().order_line:
                if so_line.product_id.id in product_unit_costs:
                    unit_cost = product_unit_costs[so_line.product_id.id]
                    so_line.sudo().write({'price_unit': unit_cost})
                    _logger.info(
                        "Updated SO line price for product %s: %s -> %s",
                        so_line.product_id.name,
                        so_line.price_unit,
                        unit_cost
                    )

    def _handle_intercompany_delivery_confirmation(self):
        """Handle delivery confirmation for intercompany orders with partial delivery support"""
        self.ensure_one()
        sale_order = self.sale_id
        
        if not (sale_order.intercompany_purchase_order_id and sale_order.intercompany_sale_order_id):
            return
            
        # Get the intercompany purchase order
        intercompany_po = sale_order.sudo().intercompany_purchase_order_id
        intercompany_so = sale_order.sudo().intercompany_sale_order_id

        # Update sale order line prices based on source picking unit costs
        self._update_intercompany_so_prices(sale_order)
        
        # Update purchase order line prices based on source picking unit costs
        self._update_intercompany_po_prices(intercompany_po)
        
        # Confirm the purchase order if not already confirmed
        if intercompany_po.state in ('draft', 'sent'):
            intercompany_po.sudo().button_confirm()
            self._log_intercompany_action(
                intercompany_po, 
                _("Purchase order automatically confirmed due to delivery confirmation from %s") % sale_order.company_id.name
            )
        
        # Find and validate the incoming picking (receipt) from the purchase order
        incoming_pickings = intercompany_po.picking_ids.filtered(
            lambda p: p.picking_type_id.code == 'incoming' and p.state not in ('done', 'cancel')
        )
        
        # Get delivered quantities from the current picking (source company)
        delivered_quantities = {}
        for move in self.move_ids.filtered(lambda m: m.state == 'done'):
            product_id = move.product_id.id
            delivered_qty = move.quantity
            if product_id in delivered_quantities:
                delivered_quantities[product_id] += delivered_qty
            else:
                delivered_quantities[product_id] = delivered_qty
        
        for incoming_picking in incoming_pickings:
            # Set quantities for move lines based on delivered quantities
            for move in incoming_picking.move_ids:
                if incoming_picking.state == 'assigned':
                    product_id = move.product_id.id
                    delivered_qty = delivered_quantities.get(product_id, 0)
                    
                    if delivered_qty > 0:
                        # Calculate how much we can receive (not more than what's available)
                        remaining_qty = move.product_uom_qty - delivered_qty
                        qty_to_receive = min(delivered_qty, remaining_qty)
                        
                        if qty_to_receive > 0:
                            # Update move lines with the delivered quantity
                            if move.move_line_ids:
                                # Update existing move lines
                                total_assigned = 0
                                for move_line in move.move_line_ids:
                                    if total_assigned < qty_to_receive:
                                        line_qty = qty_to_receive
                                        move_line.quantity = line_qty
                                        total_assigned += line_qty
                                    else:
                                        move_line.quantity = 0
                            else:
                                # Create new move line if none exists
                                self.env['stock.move.line'].create({
                                    'move_id': move.id,
                                    'product_id': move.product_id.id,
                                    'product_uom_id': move.product_uom.id,
                                    'location_id': move.location_id.id,
                                    'location_dest_id': move.location_dest_id.id,
                                    'quantity': qty_to_receive,
                                    'picking_id': incoming_picking.id,
                                })
                    else:
                        # No delivery for this product, set quantity to 0
                        for move_line in move.move_line_ids:
                            move_line.quantity = 0
            
            # Validate the incoming picking if there are quantities to receive
            has_quantities = any(
                move_line.quantity > 0 
                for move in incoming_picking.move_ids 
                for move_line in move.move_line_ids
            )
            
            if has_quantities:
                incoming_picking.with_context(skip_backorder=True, intercompany_confirmed=True).sudo().button_validate()
                
                # Copy vehicle weight information from source picking to target picking
                self._copy_vehicle_weight_info(incoming_picking)

                self._log_intercompany_action(
                    incoming_picking,
                    _("Receipt automatically validated with partial quantities due to delivery confirmation from %s") % self.company_id.name
                )

                # Check if intercompany sale order is already confirmed
                if intercompany_so.state not in ('sale', 'done'):
                    intercompany_so.sudo().action_confirm()
                    self._log_intercompany_action(
                        intercompany_so,
                        _("Sale order automatically confirmed due to delivery confirmation from %s") % self.company_id.name
                    )
                else:
                    self._log_intercompany_action(
                        intercompany_so,
                        _("Sale order already confirmed - state: %s") % intercompany_so.state
                    )
                # todo bu kısım 2. bir teslimat olacağı zaman çalışmıyor.
                # Handle outgoing delivery for intercompany sale order
                self._handle_intercompany_outgoing_delivery(intercompany_so)

            else:
                self._log_intercompany_action(
                    incoming_picking,
                    _("No quantities to receive for this delivery from %s") % self.company_id.name
                )

    def action_cancel(self):
        """Override action_cancel to handle intercompany cancellations"""
        # Handle intercompany cancellations before the actual cancellation
        for picking in self:
            if picking.sale_id and picking.sale_id.partner_id.is_intercompany_partner:
                picking._handle_intercompany_delivery_cancellation()
        
        return super(StockPicking, self).action_cancel()

    def _handle_intercompany_delivery_cancellation(self):
        """Handle delivery cancellation for intercompany orders"""
        self.ensure_one()
        sale_order = self.sale_id
        
        if not (sale_order.intercompany_purchase_order_id and sale_order.intercompany_sale_order_id):
            return
            
        intercompany_po = sale_order.intercompany_purchase_order_id
        intercompany_so = sale_order.intercompany_sale_order_id
        
        # Check if this delivery is already done
        if self.state == 'done':
            self._handle_done_delivery_cancellation(sale_order, intercompany_po, intercompany_so)
        else:
            self._handle_draft_delivery_cancellation(sale_order, intercompany_po, intercompany_so)

    def _handle_done_delivery_cancellation(self, original_so, intercompany_po, intercompany_so):
        """Handle cancellation when the original delivery is already done"""
        # Cancel intercompany sale order if its delivery is not done
        intercompany_delivery_pickings = intercompany_so.picking_ids.filtered(
            lambda p: p.picking_type_id.code == 'outgoing'
        )
        
        for delivery_picking in intercompany_delivery_pickings:
            if delivery_picking.state != 'done':
                # Cancel the intercompany sale order
                if intercompany_so.state != 'cancel':
                    intercompany_so.sudo().action_cancel()
                    self._log_intercompany_action(
                        intercompany_so,
                        _("Sale order cancelled due to cancellation from %s by %s") % (
                            self.env.company.name, self.env.user.name
                        )
                    )
                break
        
        # Cancel intercompany purchase order and create return
        if intercompany_po.state != 'cancel':
            # Create return for received products
            self._create_purchase_return(intercompany_po)
            
            # Cancel the purchase order
            intercompany_po.sudo().action_cancel()
            self._log_intercompany_action(
                intercompany_po,
                _("Purchase order cancelled due to cancellation from %s by %s") % (
                    self.env.company.name, self.env.user.name
                )
            )
        
        # Create return for the original delivery
        self._create_sale_return(original_so)

    def _handle_draft_delivery_cancellation(self, original_so, intercompany_po, intercompany_so):
        """Handle cancellation when the original delivery is not done yet"""
        # Simply cancel both intercompany orders
        if intercompany_so.state != 'cancel':
            intercompany_so.sudo().action_cancel()
            self._log_intercompany_action(
                intercompany_so,
                _("Sale order cancelled due to cancellation from %s by %s") % (
                    self.env.company.name, self.env.user.name
                )
            )
        
        if intercompany_po.state != 'cancel':
            intercompany_po.sudo().action_cancel()
            self._log_intercompany_action(
                intercompany_po,
                _("Purchase order cancelled due to cancellation from %s by %s") % (
                    self.env.company.name, self.env.user.name
                )
            )

    def _create_purchase_return(self, purchase_order):
        """Create return picking for purchase order"""
        incoming_pickings = purchase_order.picking_ids.filtered(
            lambda p: p.picking_type_id.code == 'incoming' and p.state == 'done'
        )
        
        for picking in incoming_pickings:
            return_picking = picking._create_returns()
            if return_picking:
                # Auto-validate the return
                for move in return_picking.move_ids:
                    for move_line in move.move_line_ids:
                        move_line.quantity = move_line.quantity
                return_picking.sudo().button_validate()
                
                self._log_intercompany_action(
                    return_picking,
                    _("Return automatically created and validated due to cancellation from %s") % self.env.company.name
                )

    def _create_sale_return(self, sale_order):
        """Create return picking for sale order"""
        outgoing_pickings = sale_order.picking_ids.filtered(
            lambda p: p.picking_type_id.code == 'outgoing' and p.state == 'done'
        )
        
        for picking in outgoing_pickings:
            return_picking = picking._create_returns()
            if return_picking:
                # Auto-validate the return
                for move in return_picking.move_ids:
                    for move_line in move.move_line_ids:
                        move_line.quantity = move_line.quantity
                return_picking.sudo().button_validate()
                
                self._log_intercompany_action(
                    return_picking,
                    _("Return automatically created and validated due to cancellation from %s") % self.env.company.name
                )

    def _log_intercompany_action(self, record, message):
        """Log intercompany actions in the chatter"""
        record.message_post(
            body=message,
            message_type='notification',
            subtype_xmlid='mail.mt_note'
        )

    def _create_returns(self):
        """Create a return picking for this picking"""
        if self.state != 'done':
            return False
            
        # Create return picking
        return_picking_type = self.picking_type_id.return_picking_type_id
        if not return_picking_type:
            # Find appropriate return picking type
            if self.picking_type_id.code == 'outgoing':
                return_picking_type = self.env['stock.picking.type'].search([
                    ('code', '=', 'incoming'),
                    ('warehouse_id', '=', self.picking_type_id.warehouse_id.id)
                ], limit=1)
            elif self.picking_type_id.code == 'incoming':
                return_picking_type = self.env['stock.picking.type'].search([
                    ('code', '=', 'outgoing'),
                    ('warehouse_id', '=', self.picking_type_id.warehouse_id.id)
                ], limit=1)
        
        if not return_picking_type:
            return False
        
        return_picking = self.copy({
            'name': '/',
            'origin': _('Return of %s') % self.name,
            'picking_type_id': return_picking_type.id,
            'location_id': self.location_dest_id.id,
            'location_dest_id': self.location_id.id,
            'move_ids': []
        })
        
        # Create return moves
        for move in self.move_ids.filtered(lambda m: m.state == 'done' and m.quantity > 0):
            return_move = move.copy({
                'picking_id': return_picking.id,
                'location_id': move.location_dest_id.id,
                'location_dest_id': move.location_id.id,
                'product_uom_qty': move.quantity,
                'state': 'draft',
                'move_orig_ids': Command.link(move.id),
                'move_dest_ids': []
            })
        
        return_picking.sudo().action_confirm()
        return_picking.sudo().action_assign()
        
        return return_picking

    def _copy_vehicle_weight_info(self, target_picking):
        """Copy vehicle weight information from source picking to target picking with intercompany traceability"""
        if not self.vehicle_weight_ids:
            return
            
        # Determine flow stage and related orders
        flow_stage = 'purchase_receipt'  # Default for incoming picking
        source_sale_order = None
        purchase_order = None
        target_sale_order = None
        
        if target_picking.picking_type_code == 'incoming':
            flow_stage = 'purchase_receipt'
            purchase_order = target_picking.purchase_id
            if purchase_order and purchase_order.source_sale_order_id:
                source_sale_order = purchase_order.source_sale_order_id
                target_sale_order = source_sale_order.intercompany_sale_order_id
        elif target_picking.picking_type_code == 'outgoing':
            flow_stage = 'target_delivery'
            if target_picking.sale_id and target_picking.sale_id.intercompany_sale_order_id:
                target_sale_order = target_picking.sale_id
                # Find the source through purchase order connection
                if hasattr(target_sale_order, 'source_purchase_order_id'):
                    purchase_order = target_sale_order.source_purchase_order_id
                    if purchase_order and purchase_order.source_sale_order_id:
                        source_sale_order = purchase_order.source_sale_order_id
            
        # Copy each vehicle weight record to the target picking
        for vehicle_weight in self.vehicle_weight_ids:
            # Use the new intercompany vehicle weight creation method
            vehicle_weight.with_company(target_picking.company_id.id).create_intercompany_vehicle_weight(
                target_picking=target_picking,
                flow_stage=flow_stage,
                source_sale_order_id=source_sale_order.id if source_sale_order else None,
                purchase_order_id=purchase_order.id if purchase_order else None,
                target_sale_order_id=target_sale_order.id if target_sale_order else None
            )
            
        self._log_intercompany_action(
            target_picking,
            _("Vehicle weight information copied from %s delivery with intercompany traceability") % self.company_id.name
        )
    
    def _handle_intercompany_outgoing_delivery(self, intercompany_sale_order):
        """Handle outgoing delivery creation and vehicle weight copying for intercompany sale order"""
        if not intercompany_sale_order:
            _logger.info("No intercompany sale order provided")
            return
            
        # Find outgoing pickings for the intercompany sale order
        outgoing_pickings = intercompany_sale_order.picking_ids.filtered(
            lambda p: p.picking_type_id.code == 'outgoing' and p.state not in ('done', 'cancelled')
        )
        
        # Find the corresponding incoming picking that was just validated
        incoming_pickings = intercompany_sale_order.source_sale_order_id.intercompany_purchase_order_id.picking_ids.filtered(
            lambda p: p.picking_type_id.code == 'incoming' and p.state == 'done'
        )
        
        _logger.info("Outgoing pickings found: %s, Incoming pickings found: %s", 
                    len(outgoing_pickings), len(incoming_pickings))
        
        if not incoming_pickings or not outgoing_pickings:
            _logger.warning("Missing pickings - incoming: %s, outgoing: %s", 
                          len(incoming_pickings), len(outgoing_pickings))
            return
            
        # Get the latest incoming picking (the one just validated)
        latest_incoming = incoming_pickings.sorted('write_date', reverse=True)[0]
        
        _logger.info("Latest incoming picking: %s, Vehicle weights: %s", 
                    latest_incoming.name, len(latest_incoming.vehicle_weight_ids))
        
        for outgoing_picking in outgoing_pickings:
            # Copy vehicle weight information from incoming to outgoing
            if latest_incoming.vehicle_weight_ids:
                _logger.info("Copying %s vehicle weight records to outgoing picking %s", 
                           len(latest_incoming.vehicle_weight_ids), outgoing_picking.name)
                for incoming_vehicle_weight in latest_incoming.vehicle_weight_ids:
                    # Create outgoing vehicle weight record
                    new_weight = incoming_vehicle_weight.create_intercompany_vehicle_weight(
                        target_picking=outgoing_picking,
                        flow_stage='target_delivery',
                        source_sale_order_id=incoming_vehicle_weight.source_sale_order_id.id if incoming_vehicle_weight.source_sale_order_id else None,
                        purchase_order_id=incoming_vehicle_weight.purchase_order_id.id if incoming_vehicle_weight.purchase_order_id else None,
                        target_sale_order_id=intercompany_sale_order.id
                    )
                    _logger.info("Created vehicle weight record %s for outgoing picking %s", 
                               new_weight.name, outgoing_picking.name)
            else:
                _logger.warning("No vehicle weight records found in incoming picking %s", latest_incoming.name)
            
            # Set quantities based on what was received in the incoming picking
            self._set_outgoing_quantities_from_incoming(outgoing_picking, latest_incoming)
            
            # Ensure picking is assigned before validation
            if outgoing_picking.state != 'assigned':
                outgoing_picking.sudo().action_assign()

            # bu kısım yapılmayacak.
            # # Validate the outgoing picking with context to avoid wizard and loops
            # try:
            #     outgoing_picking.with_context(
            #         skip_backorder=True,
            #         intercompany_confirmed=True,
            #         intercompany_auto_delivery=True
            #     ).button_validate()
            #
            #     # Log the action
            #     self._log_intercompany_action(
            #         outgoing_picking,
            #         _("Outgoing delivery automatically validated with vehicle weight transfer from incoming receipt")
            #     )
            #
            # except Exception as e:
            #     # Log error but don't stop the process
            #     self._log_intercompany_action(
            #         outgoing_picking,
            #         _("Failed to auto-validate outgoing delivery: %s") % str(e)
            #     )
    
    def _set_outgoing_quantities_from_incoming(self, outgoing_picking, incoming_picking):
        """Set outgoing picking quantities based on incoming picking quantities"""
        # Map incoming receipt products to outgoing picking moves
        for out_move in outgoing_picking.move_ids:
            # Find matching incoming move
            incoming_move = incoming_picking.move_ids.filtered(
                lambda m: m.product_id == out_move.product_id
            )
            
            if incoming_move:
                # Get the quantity that was actually received
                received_qty = sum(incoming_move.mapped('quantity'))
                
                # Set the outgoing move quantity
                out_move.quantity = min(received_qty + out_move.quantity, out_move.product_uom_qty)
                
                # # Update move lines with the received quantities
                # if out_move.move_line_ids:
                #     remaining_qty = out_move.quantity
                #     for move_line in out_move.move_line_ids:
                #         if move_line.product_id == out_move.product_id and remaining_qty > 0:
                #             line_qty = min(remaining_qty, move_line.quantity or move_line.product_uom_qty)
                #             move_line.quantity = line_qty
                #             remaining_qty -= line_qty
                #
                #             if remaining_qty <= 0:
                #                 break
                
                # Ensure assignment
                out_move._action_assign()
