# -*- coding: utf-8 -*-

from odoo import models, fields, api, _


class ConfirmIntercompanyPicking(models.TransientModel):
    _name = 'confirm.intercompany.picking'
    _description = 'Intercompany Picking Confirmation'

    picking_id = fields.Many2one(
        'stock.picking',
        string='Teslimat',
        required=True
    )
    
    message = fields.Html(
        string='Mesaj',
        compute='_compute_message',
        readonly=True
    )
    
    @api.depends('picking_id')
    def _compute_message(self):
        for wizard in self:
            wizard = wizard.sudo()
            company_name = ""
            if wizard.picking_id.sale_id and wizard.picking_id.sale_id.source_sale_order_id:
                # This is a sale order created from another company's sale order
                company_name = wizard.picking_id.sale_id.source_sale_order_id.company_id.name
            elif wizard.picking_id.purchase_id and wizard.picking_id.purchase_id.source_sale_order_id:
                # This is a purchase order created from another company's sale order
                company_name = wizard.picking_id.purchase_id.source_sale_order_id.company_id.name
            
            wizard.message = _("""
                <div class="alert alert-warning" role="alert">
                    <p><strong>Dikkat!</strong></p>
                    <p>Bu kayıt <strong>%s</strong> şirketindeki bir satış kaydına bağlı çalışmaktadır.</p>
                    <p>Manuel işlem yapmak bağlantıyı kopartabilir, yapmak istediğinizden emin misiniz?</p>
                </div>
            """) % company_name
    
    def action_confirm(self):
        """Confirm the picking with intercompany context"""
        self.ensure_one()
        return self.picking_id.with_context(intercompany_confirmed=True).button_validate()
    
    def action_cancel(self):
        """Cancel the operation"""
        return {'type': 'ir.actions.act_window_close'}
