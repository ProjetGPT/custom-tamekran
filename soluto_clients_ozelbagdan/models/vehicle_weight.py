# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import UserError, ValidationError

class VehicleWeight(models.Model):
    _name = 'vehicle.weight'
    _description = 'Araç Tonaj Bilgileri'
    _order = 'exit_date desc, id desc'

    @api.model
    def default_get(self, fields_list):
        res = super(VehicleWeight, self).default_get(fields_list)
        if 'exit_m3' in fields_list and self.env.context.get('default_production_id') and not res.get('exit_m3'):
            production_id_val = self.env.context.get('default_production_id')
            if production_id_val:
                production = self.env['mrp.production'].browse(production_id_val)
                if production:
                    res['exit_m3'] = production.qty_produced
        return res

    name = fields.Char(
        string='Referans',
        copy=False,
        readonly=True,
        default=lambda self: _('New')
    )
    
    picking_id = fields.Many2one(
        'stock.picking',
        string='Teslimat',
        ondelete='cascade',
        index=True
    )
    
    production_id = fields.Many2one(
        'mrp.production',
        string='Üretim Emri',
        ondelete='cascade',
        index=True
    )
    
    vehicle_plate_id = fields.Many2one(
        'vehicle.plate',
        string='Araç Plakası',
        required=True
    )
    
    driver_name = fields.Char(
        string='Sürücü Adı'
    )
    
    vehicle_tare_weight = fields.Float(
        string='Araç Dara (KG)',
        digits=(16, 2),
        readonly=True,
        help='Kamyonun boş ağırlığı (dara)'
    )
    
    exit_m3 = fields.Float(
        string='Çıkış m³',
        digits=(16, 3)
    )
    
    entry_m3 = fields.Float(
        string='Giriş m³',
        digits=(16, 3)
    )
    
    exit_weight = fields.Float(
        string='Çıkış Tonajı (kg)',
        digits=(16, 2)
    )
    
    exit_date = fields.Datetime(
        string='Çıkış Tarihi'
    )
    
    entry_weight = fields.Float(
        string='Giriş Tonajı (kg)',
        digits=(16, 2)
    )
    
    entry_date = fields.Datetime(
        string='Giriş Tarihi'
    )
    
    net_weight = fields.Float(
        string='Net Tonaj (kg)',
        compute='_compute_net_weight',
        store=True,
        digits=(16, 2)
    )
    
    notes = fields.Text(
        string='Notlar'
    )
    
    # Intercompany İzlenebilirlik Alanları
    source_sale_order_id = fields.Many2one(
        'sale.order',
        string='Kaynak Satış Siparişi',
        help='Bu araç tonaj bilgisinin kaynaklandığı 1. şirket satış siparişi',
        readonly=True
    )
    
    purchase_order_id = fields.Many2one(
        'purchase.order',
        string='Satınalma Siparişi',
        help='2. şirketteki ilgili satınalma siparişi',
        readonly=True
    )
    
    target_sale_order_id = fields.Many2one(
        'sale.order',
        string='Hedef Satış Siparişi',
        help='2. şirketteki nihai müşteriye yapılan satış siparişi',
        readonly=True
    )
    
    intercompany_flow_stage = fields.Selection([
        ('production', 'Üretim'),
        ('source_delivery', '1. Şirket Teslimatı'),
        ('purchase_receipt', '2. Şirket Satınalma Girişi'),
        ('target_delivery', '2. Şirket Satış Çıkışı')
    ], string='Intercompany Akış Aşaması', readonly=True)
    
    parent_vehicle_weight_id = fields.Many2one(
        'vehicle.weight',
        string='Ana Araç Tonaj Kaydı',
        help='Bu kaydın türetildiği ana araç tonaj kaydı',
        readonly=True
    )
    
    child_vehicle_weight_ids = fields.One2many(
        'vehicle.weight',
        'parent_vehicle_weight_id',
        string='Türetilen Araç Tonaj Kayıtları',
        readonly=True
    )
    
    child_count = fields.Integer(
        string='Türetilen Kayıt Sayısı',
        compute='_compute_child_count',
        store=True
    )
    
    intercompany_flow_info = fields.Char(
        string='Intercompany Akış Bilgisi',
        compute='_compute_intercompany_flow_info',
        store=True
    )
    
    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if vals.get('name', _('New')) == _('New'):
                vals['name'] = self.env['ir.sequence'].next_by_code('vehicle.weight') or _('New')
            
            # Auto-set intercompany flow stage if not provided
            if not vals.get('intercompany_flow_stage'):
                if vals.get('production_id') and not vals.get('picking_id'):
                    vals['intercompany_flow_stage'] = 'production'
                elif vals.get('picking_id'):
                    picking = self.env['stock.picking'].browse(vals['picking_id'])
                    if picking.picking_type_code == 'outgoing':
                        if (picking.sale_id and picking.sale_id.partner_id.is_intercompany_partner):
                            vals['intercompany_flow_stage'] = 'source_delivery'
                        elif (picking.sale_id and picking.sale_id.intercompany_sale_order_id):
                            vals['intercompany_flow_stage'] = 'target_delivery'
                    elif picking.picking_type_code == 'incoming':
                        if (picking.purchase_id and picking.purchase_id.source_sale_order_id):
                            vals['intercompany_flow_stage'] = 'purchase_receipt'
        
        return super(VehicleWeight, self).create(vals_list)
    
    @api.depends('child_vehicle_weight_ids')
    def _compute_child_count(self):
        for record in self:
            record.child_count = len(record.child_vehicle_weight_ids)
    
    @api.depends('intercompany_flow_stage', 'source_sale_order_id', 'purchase_order_id', 'target_sale_order_id')
    def _compute_intercompany_flow_info(self):
        for record in self:
            info_parts = []
            if record.intercompany_flow_stage:
                stage_dict = dict(record._fields['intercompany_flow_stage'].selection)
                info_parts.append(stage_dict.get(record.intercompany_flow_stage, ''))
            
            if record.source_sale_order_id:
                info_parts.append(f"Kaynak: {record.source_sale_order_id.name}")
            if record.purchase_order_id:
                info_parts.append(f"Satınalma: {record.purchase_order_id.name}")
            if record.target_sale_order_id:
                info_parts.append(f"Hedef: {record.target_sale_order_id.name}")
            
            record.intercompany_flow_info = ' | '.join(info_parts) if info_parts else ''
    
    def action_view_child_records(self):
        """Action to view child vehicle weight records"""
        self.ensure_one()
        return {
            'name': _('Türetilen Araç Tonaj Kayıtları'),
            'type': 'ir.actions.act_window',
            'view_mode': 'tree,form',
            'res_model': 'vehicle.weight',
            'domain': [('parent_vehicle_weight_id', '=', self.id)],
            'context': {'default_parent_vehicle_weight_id': self.id},
        }
    
    def action_view_intercompany_flow(self):
        """Action to view complete intercompany flow"""
        self.ensure_one()
        
        # Find all related records in the flow
        all_records = self.env['vehicle.weight']
        
        # Find root record
        root_record = self
        while root_record.parent_vehicle_weight_id:
            root_record = root_record.parent_vehicle_weight_id
        
        # Collect all records in the flow
        def collect_children(record):
            result = record
            for child in record.child_vehicle_weight_ids:
                result |= collect_children(child)
            return result
        
        all_records = collect_children(root_record)
        
        return {
            'name': _('Intercompany Araç Tonaj Akışı'),
            'type': 'ir.actions.act_window',
            'view_mode': 'tree,form',
            'res_model': 'vehicle.weight',
            'domain': [('id', 'in', all_records.ids)],
            'context': {'group_by': 'intercompany_flow_stage'},
        }
    
    @api.depends('exit_weight', 'entry_weight', 'vehicle_tare_weight')
    def _compute_net_weight(self):
        for record in self:
            if record.picking_id and record.picking_id.picking_type_code == 'outgoing':
                record.net_weight = record.exit_weight - (record.entry_weight or 0)
            else:
                record.net_weight = record.entry_weight - (record.exit_weight or 0)

    def create_intercompany_vehicle_weight(self, target_picking, flow_stage, **kwargs):
        """Create a new vehicle weight record for intercompany flow"""
        self.ensure_one()

        # Debug log for vehicle_tare_weight
        import logging
        _logger = logging.getLogger(__name__)
        _logger.info("Creating intercompany vehicle weight - Source vehicle_tare_weight: %s", self.vehicle_tare_weight)

        vals = {
            'picking_id': target_picking.id,
            'vehicle_plate_id': self.vehicle_plate_id.id,
            'driver_name': self.driver_name,
            'vehicle_tare_weight': self.vehicle_tare_weight,
            'notes': self.notes,
            'parent_vehicle_weight_id': self.id,
            'intercompany_flow_stage': flow_stage,
            'source_sale_order_id': kwargs.get('source_sale_order_id'),
            'purchase_order_id': kwargs.get('purchase_order_id'),
            'target_sale_order_id': kwargs.get('target_sale_order_id'),
        }

        _logger.info("Vehicle weight vals before creation: %s", vals)

        # Akış aşamasına göre m³ ve tonaj değerlerini ayarla
        if flow_stage == 'purchase_receipt':
            # 1. şirket çıkışından 2. şirket girişine
            vals.update({
                'entry_m3': self.exit_m3,
                'entry_weight': self.exit_weight,
                'entry_date': fields.Datetime.now(),
            })
        elif flow_stage == 'target_delivery':
            # 2. şirket girişinden 2. şirket çıkışına
            vals.update({
                'exit_m3': self.entry_m3 or self.exit_m3,
                'exit_weight': self.entry_weight or self.exit_weight,
                'exit_date': fields.Datetime.now(),
            })

        return self.create(vals)
    
    @api.onchange('exit_weight')
    def _onchange_exit_weight(self):
        """Set exit date when exit weight is entered"""
        for record in self:
            if record.exit_weight and not record.exit_date:
                record.exit_date = fields.Datetime.now()
    
    @api.onchange('vehicle_plate_id')
    def _onchange_vehicle_plate_id(self):
        """Auto-fill driver name and tare weight when vehicle plate is selected"""
        if self.vehicle_plate_id:
            self.driver_name = self.vehicle_plate_id.driver_name
            self.vehicle_tare_weight = self.vehicle_plate_id.vehicle_tare_weight
            
            # Set intercompany flow stage based on context
            if self.production_id and not self.picking_id:
                self.intercompany_flow_stage = 'production'
            elif self.picking_id:
                if self.picking_id.picking_type_code == 'outgoing':
                    # Check if this is intercompany
                    if (self.picking_id.sale_id and 
                        self.picking_id.sale_id.partner_id.is_intercompany_partner):
                        self.intercompany_flow_stage = 'source_delivery'
                    elif (self.picking_id.sale_id and 
                          self.picking_id.sale_id.intercompany_sale_order_id):
                        self.intercompany_flow_stage = 'target_delivery'
                elif self.picking_id.picking_type_code == 'incoming':
                    if (self.picking_id.purchase_id and 
                        self.picking_id.purchase_id.source_sale_order_id):
                        self.intercompany_flow_stage = 'purchase_receipt'
    
    @api.onchange('entry_weight')
    def _onchange_entry_weight(self):
        """Set entry date when entry weight is entered"""
        for record in self:
            if record.entry_weight and not record.entry_date:
                record.entry_date = fields.Datetime.now()
    
    @api.constrains('exit_weight', 'entry_weight')
    def _check_weights(self):
        for record in self:
            # if record.exit_weight <= 0 and record.picking_id.picking_type_code == 'outgoing':
            #     raise ValidationError(_("Çıkış tonajı 0'dan büyük olmalıdır."))
            if record.entry_weight and record.entry_weight < 0:
                raise ValidationError(_("Giriş tonajı negatif olamaz."))
            if record.entry_weight and record.entry_weight > record.exit_weight and record.picking_id.picking_type_code == 'outgoing':
                raise ValidationError(_("Giriş tonajı çıkış tonajından büyük olamaz."))

    @api.constrains('entry_weight', 'picking_id')
    def _check_entry_weight_for_incoming_picking(self):
        for record in self:
            # if record.picking_id and record.picking_id.picking_type_code == 'incoming' and not record.entry_weight:
            #     raise ValidationError(_("Giriş teslimatları için Giriş Tonajı (kg) girilmesi zorunludur."))
            if record.entry_weight and record.entry_weight < record.exit_weight and record.picking_id.picking_type_code == 'incoming':
                raise ValidationError(_("Giriş tonajı çıkış tonajından küçük olamaz."))