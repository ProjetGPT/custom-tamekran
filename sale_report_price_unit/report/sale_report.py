# -*- coding: utf-8 -*-
# © 2016 Eska Yazılım ve Danışmanlık A.Ş (www.eskayazilim.com.tr)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import models, fields


class SaleReport(models.Model):
    _inherit = "sale.report"

    price_unit = fields.Float(string='Unit Price', readonly=True)

    def _select(self):
        res = super(SaleReport, self)._select()
        return res + ",sum(l.price_unit / cr.rate) as price_unit"

