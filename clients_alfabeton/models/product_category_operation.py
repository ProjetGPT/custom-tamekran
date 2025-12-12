# -*- coding: utf-8 -*-
from odoo import models, fields, api


class ProductCategoryOperation(models.Model):
    _name = 'product.category.operation'
    _description = 'Ürün Kategori Operasyon Seçimleri'
    _rec_name = 'display_name'

    category_id = fields.Many2one(
        'product.category', 'Ürün Kategorisi',
        required=True, ondelete='cascade')
    
    operation_type_id = fields.Many2one(
        'stock.picking.type', 'Operasyon Türü',
        required=True, ondelete='cascade')
    
    # Muhasebe Hesapları
    stock_valuation_account_id = fields.Many2one(
        'account.account', 'Stok Değerleme Hesabı',
        domain="[('deprecated', '=', False)]", check_company=True,
        required=True, help="Bu operasyon türü için kullanılacak stok değerleme hesabı")
    
    stock_input_account_id = fields.Many2one(
        'account.account', 'Stok Giriş Hesabı',
        domain="[('deprecated', '=', False)]", check_company=True,
        required=True, help="Bu operasyon türü için kullanılacak stok giriş hesabı")
    
    stock_output_account_id = fields.Many2one(
        'account.account', 'Stok Çıkış Hesabı',
        domain="[('deprecated', '=', False)]", check_company=True,
        required=True, help="Bu operasyon türü için kullanılacak stok çıkış hesabı")
    
    company_id = fields.Many2one(
        'res.company', 'Şirket',
        default=lambda self: self.env.company,
        required=True)
    
    active = fields.Boolean('Aktif', default=True)
    
    display_name = fields.Char('Görünen Ad', compute='_compute_display_name', store=True)
    
    @api.depends('category_id', 'operation_type_id')
    def _compute_display_name(self):
        for record in self:
            if record.category_id and record.operation_type_id:
                record.display_name = f"{record.category_id.name} - {record.operation_type_id.name}"
            else:
                record.display_name = "Yeni Kayıt"
    
    @api.constrains('category_id', 'operation_type_id', 'company_id')
    def _check_unique_category_operation(self):
        for record in self:
            existing = self.search([
                ('category_id', '=', record.category_id.id),
                ('operation_type_id', '=', record.operation_type_id.id),
                ('company_id', '=', record.company_id.id),
                ('id', '!=', record.id)
            ])
            if existing:
                raise models.ValidationError(
                    f"Bu kategori ({record.category_id.name}) ve operasyon türü ({record.operation_type_id.name}) "
                    f"kombinasyonu zaten mevcut!")
    
    _sql_constraints = [
        ('unique_category_operation_company', 
         'unique(category_id, operation_type_id, company_id)',
         'Aynı kategori ve operasyon türü kombinasyonu bir şirkette sadece bir kez tanımlanabilir!')
    ]
