# -*- coding: utf-8 -*-

{
    'name': "Multi Company Account Transfer",
    'version': "1.0",
    'summary': "Multi Company Account Transfer",
    'website': 'https://www.quanimo.com',
    'category': "Account",
    'author': 'Quanimo',
    'sequence': 1453,
    'depends': [
        'account',
    ],
    'data': [
        'security/ir.model.access.csv',
        'views/account_journal.xml',
        'wizard/sync_account_move_wizard.xml'
    ],
    'demo': [],
    'application': True,
    'license': 'AGPL-3',

}
