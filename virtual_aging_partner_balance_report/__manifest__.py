# -*- coding: utf-8 -*-
# © 2016 Projet Yazılım ve Danışmanlık A.Ş (www.bulutkobi.io)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
{
    "name": "Virtual Aging Partner Balance Report",
    "version": "1.0",
    "summary": "Virtual Aging Partner Balance Report",
    'sequence': 1453,
    'description': """
Bu modül Virtual Aging Partner Balance Report.
    """,
    'category': 'Muhasebe Çözümleri',
    'author': 'Projetgrup',
    'maintainer': 'Projetgrup BulutKOBI',
    'website': 'https://www.bulutkobi.io',
    "depends": [
        'account_reports',
    ],
    "data": ['data/ir_cron.xml',
             'security/vapbr_security.xml',
             'security/ir.model.access.csv',
             'views/virtual_aging_partner_balance_report_view.xml',
             ],
    'application': False,
    'installable': True,
    'auto_install': False,
}
