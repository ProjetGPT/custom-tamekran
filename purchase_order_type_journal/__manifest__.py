# -*- coding: utf-8 -*-
{
    'name': 'Purchase Order Type Journal',
    'version': '1.0',
    'description': """ Purchase Order Type Journal """,
    'summary': """ Purchase Order Type Journal """,
    'author': 'Quanimo',
    'website': 'www.quanimo.com',
    'category': 'Inventory/Purchase',
    'depends': ['purchase'],
    'license': 'LGPL-3',
    "data": [
        "security/ir.model.access.csv",

        "views/purchase_order_views.xml",
        "views/purchase_order_type.xml"
    ],
    'application': False,
    'installable': True,
    'auto_install': False,
}
