# -*- coding: utf-8 -*-
{
    'name': 'Studio customizations',
    'version': '11.0.1.0',
    'category': 'Studio',
    'description': u"""

This module has been generated by Odoo Studio.
It contains the apps created with Studio and the customizations of existing apps.

""",
    'author': 'IŞIKLAR LED',
    'depends': [
        'account',
        'sale',
        'analytic',
        'base',
        'calendar',
        'contacts',
        'crm',
        'accounting_tr_date_range',
        'delivery',
        'product',
        'purchase',
        'stock',
        'website_sale',
        'uom'
    ],
    'data': [
        'data/ir_model.xml',
        'data/ir_model_fields.xml',
        'data/ir_model_access.xml',
        'data/ir_actions_server.xml',
        # 'data/base_automation.xml',
        'data/res_groups.xml',
        'data/ir_actions_act_window.xml',
        'data/ir_ui_menu.xml',
        'data/ir_ui_view_final.xml',
        'data/ir_actions_report.xml',
        # 'data/ir_ui_view.xml',
        # 'data/ir_actions_act_window2.xml',
        'data/ir_filters.xml',
    ],
    'application': False,
    'license': 'OPL-1',
}
