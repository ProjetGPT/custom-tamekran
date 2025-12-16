# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.tools import float_round


class ProductTemplate(models.Model):
    _inherit = 'product.template'

    current_cost = fields.Float(
        string='Güncel Maliyet',
        digits='Product Price',
        help='Teslimat onaylandığında hesaplanan güncel maliyet değeri. Bu değer tüm şirketlerde ortaktır.',
        company_dependent=False,
        compute='_compute_current_cost',
        store=True,
    )
    
    @api.depends('product_variant_ids', 'product_variant_ids.current_cost')
    def _compute_current_cost(self):
        """
        Compute current_cost based on the variants' current_cost
        """
        unique_variants = self.filtered(lambda template: len(template.product_variant_ids) == 1)
        for template in unique_variants:
            template.current_cost = template.product_variant_ids.current_cost
        for template in (self - unique_variants):
            template.current_cost = 0.0


class ProductProduct(models.Model):
    _inherit = 'product.product'

    current_cost = fields.Float(
        string='Güncel Maliyet',
        digits='Product Price',
        help='Teslimat onaylandığında hesaplanan güncel maliyet değeri. Bu değer tüm şirketlerde ortaktır.',
        company_dependent=False,
    )

    def calculate_current_cost(self):
        """
        Calculate current cost based on the first company's cost records.
        This function uses the same logic as action_bom_cost but returns the value
        instead of updating standard_price.
        """
        self.ensure_one()
        
        # Always use the first company for cost calculation
        first_company = self.env['res.company'].search([], limit=1, order='id')
        
        # Switch to the first company's environment
        self_with_company = self.with_company(first_company)
        
        # Find BOMs using the first company
        bom = self_with_company.env['mrp.bom']._bom_find(self_with_company)[self_with_company]
        
        if bom:
            # Calculate cost using the same logic as _compute_bom_price
            return self_with_company._compute_bom_price(bom)
        else:
            # Check if product is a byproduct
            bom = self_with_company.env['mrp.bom'].search([
                ('byproduct_ids.product_id', '=', self.id)
            ], order='sequence, product_id, id', limit=1)
            
            if bom:
                price = self_with_company._compute_bom_price(bom, byproduct_bom=True)
                if price:
                    return price
        
        # If no BOM found, return current standard price
        return self.standard_price

    def update_current_cost(self):
        """
        Update the current_cost field with the calculated value.
        """
        for product in self:
            cost = product.calculate_current_cost()
            if cost:
                product.current_cost = cost
        return True
