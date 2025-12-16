# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.fields import Command

class SaleOrder(models.Model):
    _inherit = 'sale.order'

    final_customer_id = fields.Many2one(
        'res.partner',
        string='Final Customer',
        help='The customer for the sales order that will be created in the target company.'
    )
    final_customer_transfer_id = fields.Many2one(
        'res.partner',
        string='Final Customer Transfer',
        help='The customer for the sales order that will be created in the target company.'
    )

    intercompany_sale_order_id = fields.Many2one(
        'sale.order',
        string='Intercompany Sales Order',
        readonly=True,
        copy=False
    )

    intercompany_purchase_order_id = fields.Many2one(
        'purchase.order',
        string='Intercompany Purchase Order',
        readonly=True,
        copy=False
    )

    source_sale_order_id = fields.Many2one(
        'sale.order',
        string='Source Sale Order',
        readonly=True,
        copy=False,
        help='The original sale order that triggered this intercompany order.'
    )

    is_intercompany_order = fields.Boolean(
        string='Is Intercompany Order',
        compute='_compute_is_intercompany_order',
        store=False
    )

    def action_view_intercompany_sale_order(self):
        self.ensure_one()
        return {
            'type': 'ir.actions.act_window',
            'res_model': 'sale.order',
            'view_mode': 'form',
            'res_id': self.intercompany_sale_order_id.id,
            'target': 'current',
            'context': self.env.context,
        }

    def action_view_intercompany_purchase_order(self):
        self.ensure_one()
        return {
            'type': 'ir.actions.act_window',
            'res_model': 'purchase.order',
            'view_mode': 'form',
            'res_id': self.intercompany_purchase_order_id.id,
            'target': 'current',
            'context': self.env.context,
        }

    def action_view_source_sale_order(self):
        self.ensure_one()
        return {
            'type': 'ir.actions.act_window',
            'res_model': 'sale.order',
            'view_mode': 'form',
            'res_id': self.source_sale_order_id.id,
            'target': 'current',
            'context': self.env.context,
        }

    @api.model
    def _prepare_intercompany_so_vals(self, original_order):
        target_company_id = original_order.partner_id.target_company_id.id
        so_lines = []
        
        for line in original_order.order_line:
            # Find matching taxes in target company by name
            
            so_lines.append((0, 0, {
                'product_id': line.product_id.id,
                'product_uom_qty': line.product_uom_qty,
                'price_unit': line.price_unit,
                # 'tax_id': [(6, 0, target_taxes.ids)],
            }))
        
        return {
            'company_id': target_company_id,
            'partner_id': original_order.final_customer_id.id,
            'source_sale_order_id': original_order.id,
            'order_line': so_lines,
        }

    @api.model
    def _prepare_intercompany_po_vals(self, original_order, source_company_partner):
        target_company_id = original_order.partner_id.target_company_id.id
        po_lines = []
        for line in original_order.order_line:

            po_lines.append((0, 0, {
                'product_id': line.product_id.id,
                'product_qty': line.product_uom_qty,
                'price_unit': line.price_unit,
                # 'taxes_id': [(6, 0, supplier_taxes.ids)],  # Use product's supplier taxes
            }))
        
        return {
            'company_id': target_company_id,
            'partner_id': source_company_partner.id,
            'source_sale_order_id': original_order.id,
            'order_line': po_lines,
        }

    @api.depends('partner_id.is_intercompany_partner')
    def _compute_is_intercompany_order(self):
        for order in self:
            order.is_intercompany_order = order.partner_id.is_intercompany_partner if order.partner_id else False

    @api.onchange('final_customer_id')
    def _onchange_final_customer_id(self):
        """Auto-fill final_customer_transfer_id based on final_customer_id delivery address"""
        if self.final_customer_id:
            # Look for delivery type address for the final customer
            delivery_address = self.final_customer_id.child_ids.filtered(
                lambda c: c.type == 'delivery'
            )
            
            if delivery_address:
                # If delivery address exists, use the first one
                self.final_customer_transfer_id = delivery_address[0]
            else:
                # If no delivery address, use the final customer itself
                self.final_customer_transfer_id = self.final_customer_id
        else:
            # If no final customer selected, clear the transfer field
            self.final_customer_transfer_id = False

    def action_confirm(self):
        res = super(SaleOrder, self).action_confirm()
        for order in self.filtered(lambda o: o.partner_id.is_intercompany_partner):
            target_company = order.partner_id.target_company_id
            if not target_company:
                continue

            # Find the partner representing the source company in the target company's contacts
            source_company_partner = self.env['res.partner'].search([
                ('vat', '=', order.company_id.vat),
                ('company_id', '=', target_company.id)
            ], limit=1)
            if not source_company_partner:
                # If not found, create it
                source_company_partner = self.env['res.partner'].sudo().with_company(target_company.id).create({
                    'name': order.company_id.name,
                    'company_id': target_company.id,
                    'vat': order.company_id.vat,
                })

            # Create Intercompany SO
            so_vals = self._prepare_intercompany_so_vals(order)
            inter_so = self.env['sale.order'].sudo().with_company(target_company.id).create(so_vals)

            # Create Intercompany PO
            po_vals = self._prepare_intercompany_po_vals(order, source_company_partner)
            inter_po = self.env['purchase.order'].sudo().with_company(target_company.id).create(po_vals)

            # Link them to the original order
            order.write({
                'intercompany_sale_order_id': inter_so.id,
                'intercompany_purchase_order_id': inter_po.id,
            })
        return res

    def action_cancel(self):
        """Override action_cancel to handle intercompany cancellations"""
        # Handle intercompany cancellations before the actual cancellation
        for order in self.filtered(lambda o: o.partner_id.is_intercompany_partner):
            order.sudo()._handle_intercompany_sale_cancellation()
        
        return super(SaleOrder, self).action_cancel()

    def _handle_intercompany_sale_cancellation(self):
        """Handle sale order cancellation for intercompany orders"""
        self.ensure_one()
        
        if not (self.intercompany_purchase_order_id and self.intercompany_sale_order_id):
            return
            
        intercompany_po = self.intercompany_purchase_order_id
        intercompany_so = self.intercompany_sale_order_id
        
        # Check if any delivery is done
        delivery_pickings = self.picking_ids.filtered(
            lambda p: p.picking_type_id.code == 'outgoing'
        )
        
        has_done_delivery = any(p.state == 'done' for p in delivery_pickings)
        
        if has_done_delivery:
            self._handle_sale_cancellation_with_done_delivery(intercompany_po, intercompany_so)
        else:
            self._handle_sale_cancellation_without_delivery(intercompany_po, intercompany_so)

    def _handle_sale_cancellation_with_done_delivery(self, intercompany_po, intercompany_so):
        """Handle cancellation when original sale has done deliveries"""
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
            self._create_purchase_return_from_sale(intercompany_po)
            
            # Cancel the purchase order
            intercompany_po.sudo().action_cancel()
            self._log_intercompany_action(
                intercompany_po,
                _("Purchase order cancelled due to cancellation from %s by %s") % (
                    self.env.company.name, self.env.user.name
                )
            )
        
        # Create return for the original delivery
        self._create_sale_return_from_sale()

    def _handle_sale_cancellation_without_delivery(self, intercompany_po, intercompany_so):
        """Handle cancellation when original sale has no done deliveries"""
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
            intercompany_po.sudo().button_cancel()
            self._log_intercompany_action(
                intercompany_po,
                _("Purchase order cancelled due to cancellation from %s by %s") % (
                    self.env.company.name, self.env.user.name
                )
            )

    def _create_purchase_return_from_sale(self, purchase_order):
        """Create return picking for purchase order from sale cancellation"""
        incoming_pickings = purchase_order.picking_ids.filtered(
            lambda p: p.picking_type_id.code == 'incoming' and p.state == 'done'
        )
        
        for picking in incoming_pickings:
            return_picking = self._create_return_picking(picking)
            if return_picking:
                self._log_intercompany_action(
                    return_picking,
                    _("Return automatically created and validated due to sale cancellation from %s") % self.env.company.name
                )

    def _create_sale_return_from_sale(self):
        """Create return picking for this sale order"""
        outgoing_pickings = self.picking_ids.filtered(
            lambda p: p.picking_type_id.code == 'outgoing' and p.state == 'done'
        )
        
        for picking in outgoing_pickings:
            return_picking = self._create_return_picking(picking)
            if return_picking:
                self._log_intercompany_action(
                    return_picking,
                    _("Return automatically created and validated due to sale cancellation")
                )

    def _create_return_picking(self, original_picking):
        """Create and validate a return picking"""
        if original_picking.state != 'done':
            return False
            
        # Create return picking
        return_picking_type = original_picking.picking_type_id.return_picking_type_id
        if not return_picking_type:
            # Find appropriate return picking type
            if original_picking.picking_type_id.code == 'outgoing':
                return_picking_type = self.env['stock.picking.type'].search([
                    ('code', '=', 'incoming'),
                    ('warehouse_id', '=', original_picking.picking_type_id.warehouse_id.id)
                ], limit=1)
            elif original_picking.picking_type_id.code == 'incoming':
                return_picking_type = self.env['stock.picking.type'].search([
                    ('code', '=', 'outgoing'),
                    ('warehouse_id', '=', original_picking.picking_type_id.warehouse_id.id)
                ], limit=1)
        
        if not return_picking_type:
            return False
        
        return_picking = original_picking.copy({
            'name': '/',
            'origin': _('Return of %s') % original_picking.name,
            'picking_type_id': return_picking_type.id,
            'location_id': original_picking.location_dest_id.id,
            'location_dest_id': original_picking.location_id.id,
            'move_ids': []
        })
        
        # Create return moves
        for move in original_picking.move_ids.filtered(lambda m: m.state == 'done' and m.quantity > 0):
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
        
        # Auto-validate the return
        for move in return_picking.move_ids:
            for move_line in move.move_line_ids:
                move_line.quantity = move_line.quantity
        return_picking.sudo().button_validate()
        
        return return_picking

    def _log_intercompany_action(self, record, message):
        """Log intercompany actions in the chatter"""
        record.message_post(
            body=message,
            message_type='notification',
            subtype_xmlid='mail.mt_note'
        )
