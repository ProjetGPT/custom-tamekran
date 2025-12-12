from odoo import models, fields, api


class ProductCategory(models.Model):
    _inherit = 'product.category'

    # Operasyon Türü Alanı
    operation_type_id = fields.Many2one(
        'stock.picking.type', 'Operasyon Türü',
        help="Bu kategori için özel muhasebe hesaplarının kullanılacağı operasyon türü")
    
    # Operasyon Türüne Özel Hesap Property'leri
    property_stock_account_input_operation_id = fields.Many2one(
        'account.account', 'Operasyon Stok Giriş Hesabı', company_dependent=True,
        domain="[('deprecated', '=', False)]", check_company=True,
        help="Operasyon türü seçildiğinde kullanılacak stok giriş hesabı")
    
    property_stock_account_output_operation_id = fields.Many2one(
        'account.account', 'Operasyon Stok Çıkış Hesabı', company_dependent=True,
        domain="[('deprecated', '=', False)]", check_company=True,
        help="Operasyon türü seçildiğinde kullanılacak stok çıkış hesabı")
    
    property_stock_valuation_account_operation_id = fields.Many2one(
        'account.account', 'Operasyon Stok Değerleme Hesabı', company_dependent=True,
        domain="[('deprecated', '=', False)]", check_company=True,
        help="Operasyon türü seçildiğinde kullanılacak stok değerleme hesabı")
    
    @api.onchange('operation_type_id')
    def _onchange_operation_type_id(self):
        """Operasyon türü seçildiğinde hesap alanlarını temizle"""
        if self.operation_type_id:
            self.property_stock_account_input_operation_id = False
            self.property_stock_account_output_operation_id = False
            self.property_stock_valuation_account_operation_id = False