# -*- coding: utf-8 -*-

from odoo import _, api, fields, models


class SaleOrder(models.Model):
    _inherit = "sale.order"

    so_type_id = fields.Many2one("sale.order.type", string="Type")
