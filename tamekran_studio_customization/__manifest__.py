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
        '__export__',
        'account',
        'sale',
        'analytic',
        'base',
        'calendar',
        'contacts',
        'crm',
        'accounting_tr_date_range',
        'delivery',
        'l10n_tr_account_document_purchase',
        'procurement_purchase_no_grouping',
        'product',
        'purchase',
        'sale',
        'sale_stock',
        'sales_team',
        'stock',
        'stock_landed_cost_invoice',
        'stock_landed_costs',
        'utm',
        'virtual_aging_partner_balance_report',
        'web_studio',
        'website_sale',
    ],
    'data': [
        'data/res_groups.xml',
        'data/ir_model.xml',
        'data/ir_model_fields.xml',
        'data/ir_ui_view.xml',
        'data/ir_actions_act_window.xml',
        'data/ir_actions_report.xml',
        'data/ir_actions_server.xml',
        'data/ir_ui_menu.xml',
        'data/ir_filters.xml',
        'data/base_automation.xml',
        'data/ir_model_access.xml',
    ],
    'application': False,
    'license': 'OPL-1',
}
