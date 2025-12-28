# -*- coding: utf-8 -*-

from odoo import _, api, fields, models
from odoo.exceptions import UserError


class SaleOrderType(models.Model):
    _name = "sale.order.type"

    name = fields.Char()
    is_default = fields.Boolean()
    journal_id = fields.Many2one("account.journal", domain=[("type", "=", "sale")])

    def write(self, vals):
        if "is_default" in vals and vals.get("is_default", False):
            other_types = self.env["sale.order.type"].search([
                ("is_default", "=", True),
                ("id", "!=", self.id)
            ])
            if other_types:
                raise UserError(_("You cannot have more than one default type."))
        return super(SaleOrderType, self).write(vals)

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if "is_default" in vals and vals.get("is_default", False):
                other_types = self.env["sale.order.type"].search([
                    ("is_default", "=", True),
                    ("id", "!=", self.id)
                ])
                if other_types:
                    raise UserError(_("You cannot have more than one default type."))
        return super(SaleOrderType, self).create(vals_list)
