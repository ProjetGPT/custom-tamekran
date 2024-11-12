# -*- coding: utf-8 -*-
# © 2016 Eska Yazılım ve Danışmanlık A.Ş (www.eskayazilim.com.tr)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import models, fields


class SaleReport(models.Model):
    _inherit = "sale.report"

    parent_categ_id = fields.Many2one(comodel_name='product.category',
                                      string='Parent Category of Product',
                                      readonly=True)

    def _select(self):
        res = super(SaleReport, self)._select()
        return res + ",cat.parent_id as parent_categ_id"

    def _from(self):
        res = super(SaleReport, self)._from()
        return res + "join product_category cat on t.categ_id = cat.id"

    def _group_by(self):
        res = super(SaleReport, self)._group_by()
        return res + ",cat.parent_id"
