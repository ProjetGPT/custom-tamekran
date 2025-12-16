from odoo import models, fields, api, _


class SalesOrder(models.Model):
    _inherit = 'sale.order'

    def compute_discount_amount(self):
        total = 0.0
        for order in self:
            for line in order.order_line:
                total += line.price_unit * ((line.discount or 0.0) / 100.0) * line.product_uom_qty
        return total



class SaleOrderLine(models.Model):
    _inherit = 'sale.order.line'

    net_sale_price = fields.Float('Net Sale Price', compute='_compute_amount', store=True, precompute=True, digits='Product Price')


    @api.depends('product_uom_qty', 'discount', 'price_unit', 'tax_id')
    def _compute_amount(self):
        res = super()._compute_amount()
        self._update_net_sale_price()
        return res

    def _update_net_sale_price(self):
        for line in self:
            tax_results = self.env['account.tax'].with_company(line.company_id)._compute_taxes([
                line._convert_to_tax_base_line_dict()
            ])
            totals = list(tax_results['totals'].values())[0]
            amount_untaxed = totals['amount_untaxed']
            netsaleprice = amount_untaxed / (line.product_uom_qty if line.product_uom_qty != 0 else 1.0)
            line.update({
                'net_sale_price': netsaleprice,
            })


    def get_total_percentage_of_taxes(self):
        total_percentage = 0
        for tax in self.tax_id:
            total_percentage += tax.amount
        return total_percentage
