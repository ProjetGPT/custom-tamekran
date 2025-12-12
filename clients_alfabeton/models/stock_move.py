from odoo import models, fields, api


class StockMove(models.Model):
    _inherit = 'stock.move'

    supplier_product_info = fields.Char('Supplier Product Info', compute='_compute_supplier_product_info')
    picking_id = fields.Many2one(copy=False)
    picking_date_done = fields.Datetime(related='picking_id.date_done', store=True)
    picked = fields.Boolean('Picked')
    
    def _get_src_account(self, accounts_data):
        """Override to use operation-specific accounts if available"""
        # Önce operasyon türü kontrolü yap
        if self._should_use_operation_accounts():
            operation_account = self._get_operation_account('input')
            if operation_account:
                return operation_account.id
        
        # Varsayılan davranışı kullan
        return super()._get_src_account(accounts_data)
    
    def _get_dest_account(self, accounts_data):
        """Override to use operation-specific accounts if available"""
        # Önce operasyon türü kontrolü yap
        if self._should_use_operation_accounts():
            operation_account = self._get_operation_account('output')
            if operation_account:
                return operation_account.id
        
        # Varsayılan davranışı kullan
        return super()._get_dest_account(accounts_data)
    
    def _get_accounting_data_for_valuation(self):
        """Override to use operation-specific valuation account if available"""
        journal_id, acc_src, acc_dest, acc_valuation = super()._get_accounting_data_for_valuation()
        
        # Operasyon türü kontrolü yap
        if self._should_use_operation_accounts():
            operation_valuation_account = self._get_operation_account('valuation')
            if operation_valuation_account:
                acc_valuation = operation_valuation_account.id
        
        return journal_id, acc_src, acc_dest, acc_valuation
    
    def _should_use_operation_accounts(self):
        """Check if operation-specific accounts should be used"""
        if not self.picking_id or not self.picking_id.picking_type_id:
            return False
        
        picking_type = self.picking_id.picking_type_id
        category = self.product_id.categ_id
        
        # Hem irsaliye türünde hem de kategori de operasyon türü tanımlı ve eşleşiyor mu?
        return (category.operation_type_id and
                category.operation_type_id.id == picking_type.id)
    
    def _get_operation_account(self, account_type):
        """Get operation-specific account based on type"""
        if not self.product_id or not self.product_id.categ_id:
            return False
        
        category = self.product_id.categ_id
        
        if account_type == 'input':
            return category.property_stock_account_input_operation_id
        elif account_type == 'output':
            return category.property_stock_account_output_operation_id
        elif account_type == 'valuation':
            return category.property_stock_valuation_account_operation_id
        
        return False
    
    def _account_entry_move(self, qty, description, svl_id, cost):
        """Override to create separate journal entry for valuation transfer before outgoing entry"""
        am_vals = []
        
        # Teslimat operasyonunda ekstra yevmiye kaydı oluştur (çıkış kaydından ÖNCE)
        if self._should_create_valuation_transfer_entry():
            transfer_entry = self._create_valuation_transfer_entry(qty, description, svl_id, cost)
            if transfer_entry:
                am_vals.append(transfer_entry)
        
        # Normal yevmiye kayıtlarını ekle
        am_vals.extend(super()._account_entry_move(qty, description, svl_id, cost))
        
        return am_vals
    
    def _should_create_valuation_transfer_entry(self):
        """Check if we should create extra valuation transfer entry"""
        # Operasyon hesapları kullanılıyor mu?
        if not self._should_use_operation_accounts():
            return False
        
        # Teslimat (outgoing) operasyonu mu?
        if not self.picking_id or not self.picking_id.picking_type_id:
            return False
        
        picking_type = self.picking_id.picking_type_id
        
        # Teslimat türü kontrolü (code == 'outgoing')
        return picking_type.code == 'outgoing'
    
    def _create_valuation_transfer_entry(self, qty, description, svl_id, cost):
        """Create separate journal entry for valuation transfer between accounts"""
        self.ensure_one()
        
        category = self.product_id.categ_id
        
        # Operasyon değerleme hesabı (153 - Borç)
        operation_valuation_account = category.property_stock_valuation_account_operation_id
        
        # Normal değerleme hesabı (150 - Alacak)
        accounts_data = self.product_id.product_tmpl_id.get_product_accounts()
        standard_valuation_account = accounts_data.get('stock_valuation', False)
        
        if not operation_valuation_account or not standard_valuation_account:
            return False
        
        # Tutarı hesapla (pozitif değer - çıkış işleminde cost negatif olabilir)
        transfer_cost = abs(cost)
        debit_value = self.company_id.currency_id.round(transfer_cost)
        credit_value = debit_value
        
        valuation_partner_id = self._get_partner_id_for_valuation_lines()
        
        line_vals = {
            'name': f"{description} - Değerleme Transferi",
            'product_id': self.product_id.id,
            'quantity': qty,
            'product_uom_id': self.product_id.uom_id.id,
            'ref': description,
            'partner_id': valuation_partner_id,
        }
        
        # Borç: Operasyon Değerleme Hesabı (153)
        debit_line = {
            **line_vals,
            'balance': debit_value,
            'account_id': operation_valuation_account.id,
        }
        
        # Alacak: Normal Değerleme Hesabı (150)
        credit_line = {
            **line_vals,
            'balance': -credit_value,
            'account_id': standard_valuation_account.id,
        }
        
        # Yevmiye kaydı hazırla
        journal_id, acc_src, acc_dest, acc_valuation = self._get_accounting_data_for_valuation()
        svl = self.env['stock.valuation.layer'].browse(svl_id)
        
        if self.env.context.get('force_period_date'):
            date = self.env.context.get('force_period_date')
        elif svl.account_move_line_id:
            date = svl.account_move_line_id.date
        else:
            date = fields.Date.context_today(self)
        
        return {
            'journal_id': journal_id,
            'line_ids': [(0, 0, debit_line), (0, 0, credit_line)],
            'partner_id': valuation_partner_id,
            'date': date,
            'ref': f"{description} - Değerleme Transferi",
            'stock_move_id': self.id,
            'move_type': 'entry',
            'company_id': self.company_id.id,
        }
