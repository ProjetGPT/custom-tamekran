# -*- coding: utf-8 -*-
{
    'name': "Özel Bağdan Müşteri Geliştirmeleri",
    'summary': """
        Özel Bağdan firması için özel geliştirmeleri içerir.""",
    'description': """
                           Üretim yapan firmanın teslimat aşamasında tırların çıkış tonajı ve giriş tonajının takibini sağlayan modül.
                       """,
    'author': "Soluto Bilişim Teknolojileri A.Ş.",
    'website': "http://www.soluto.com.tr",
    'category': 'Tools',
    'version': '1.0',
    'license': "Other proprietary",
    'depends': ['base', 'stock', 'sale_management', 'purchase', 'product', 'mrp_account', 'sale_mrp',
                'account', 'report_xlsx', 'soluto_intercompany_transfer'],
    'data': [
        'security/ir.model.access.csv',
        'views/stock_picking_views.xml',
        'views/vehicle_weight_views.xml',
        'views/product_views.xml',
        'views/mrp_production_views.xml',
        'views/account_move_views.xml',
        'views/sale_views.xml',
        'views/stock_quant_views.xml',
        'wizards/select_production_vehicles_views.xml',
        'wizards/stock_change_product_qty_views.xml',
        'report/sale_report_templates.xml',
        'report/sale_report.xml',
    ],
    'assets': {'web.assets_backend': [
        'soluto_clients_ozelbagdan/static/src/forecasted_buttons.xml',
    ]},
    'installable': True,
    'auto_install': False,
    'application': False,
}
