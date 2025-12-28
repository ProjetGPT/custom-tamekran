# -*- coding: utf-8 -*-

{
    "name": "Sale Order Type Journal",
    "summary": "Manage Multiple Sale Order Types",
    "version": "1.1",
    'author': 'Quanimo',
    "website": "https://www.quanimo.com",
    "category": "Account",
    "depends": ["sale"],
    "license": "LGPL-3",
    "data": [
        "security/ir.model.access.csv",

        "views/sale_order_type.xml",
        "views/sale_order.xml",
        "views/sale_team_view.xml",

        "wizard/sale_make_invoice_advance_views.xml",
    ],
    'application': False,
    'installable': True,
    'auto_install': False,
}
