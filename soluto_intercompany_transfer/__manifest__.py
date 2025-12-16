{
    'name': 'Soluto Intercompany Transfer',
    'version': '17.0.1.0.0',
    'summary': 'Automates order creation between companies.',
    'author': 'Cascade, Soluto',
    'website': 'https://www.soluto.com.tr',
    'category': 'Sales',
    'license': 'AGPL-3',
    'depends': [
        'sale_management',
        'purchase',
        'stock',
        'mrp',
    ],
    'data': [
        'security/ir.model.access.csv',
        'views/res_partner_views.xml',
        'views/sale_order_views.xml',
        'views/purchase_order_views.xml',
        'wizards/confirm_intercompany_picking_views.xml',
    ],
    'installable': True,
    'application': False,
}
