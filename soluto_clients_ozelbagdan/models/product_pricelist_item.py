# -*- coding: utf-8 -*-

from odoo import models, fields, api, _


class PricelistItem(models.Model):
    _inherit = 'product.pricelist.item'

    base = fields.Selection(
        selection_add=[
            ('current_cost', 'Güncel Maliyet'),
        ],
        ondelete={'current_cost': 'set default'}
    )

    def _compute_base_price(self, product, quantity, uom, date, currency):
        currency.ensure_one()
        
        # Eğer base 'current_cost' ise, güncel maliyet değerini kullan
        if self.base == 'current_cost':
            # Ürün varyantı için
            if product._name == 'product.product':
                price = product.current_cost
            # Ürün şablonu için
            else:
                # Tek varyantı olan ürünler için
                if len(product.product_variant_ids) == 1:
                    price = product.product_variant_ids.current_cost
                # Birden fazla varyantı olan ürünler için
                else:
                    # Eğer belirli bir varyant seçilmişse
                    if self.product_id:
                        price = self.product_id.current_cost
                    # Varyant seçilmemişse, varsayılan varyantın güncel maliyetini kullan
                    else:
                        price = product.product_variant_id.current_cost
            
            # Eğer güncel maliyet tanımlı değilse, standart maliyeti kullan
            if not price:
                price = product.standard_price
                
            # Para birimi dönüşümü
            if currency and self.currency_id != currency:
                price = self.currency_id._convert(
                    price, currency, self.env.company, date, round=False
                )
                
            return price
        
        # Diğer durumlar için orijinal metodu çağır
        return super(PricelistItem, self)._compute_base_price(product, quantity, uom, date, currency)
