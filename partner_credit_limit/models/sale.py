# See LICENSE file for full copyright and licensing details.


from odoo import api, models, _
from odoo.exceptions import UserError


class SaleOrder(models.Model):
    _inherit = "sale.order"

    def check_limit(self):
        self.ensure_one()
        partner = self.partner_id
        moveline_obj = self.env['account.move.line']

        movelines = moveline_obj.sudo().search([
            ('partner_id', '=', partner.id),
            ('account_id.user_type_id.type', 'in', ['receivable', 'payable'])
        ])
        confirm_sale_order = self.search([
            ('partner_id', '=', partner.id),
            ('state', '=', 'sale')
        ])

        debit, credit = 0.0, 0.0
        amount_total = 0.0

        for status in confirm_sale_order:
            if status.invoice_status == 'to invoice':
                amount_total += status.amount_total

        for line in movelines:
            credit += line.credit
            debit += line.debit

        if (debit - credit) +  amount_total + self.amount_total > partner.credit_limit:
            available_credit_limit = partner.credit_limit - ((debit - credit) + amount_total)
            if not partner.over_credit:
                msg = 'Kullanılabilir Kredi Limit' \
                      ' Toplamı = %s \n "%s" Firmasının Kredi Limit Toplamı Aşıldı. Lütfen Kontrol Ediniz. ' \
                      '' % (available_credit_limit, self.partner_id.name)
                raise UserError(_('Satış Teklifini Onaylayamazsınız. \n' + msg))

        # partner_credit_limit = (partner.credit_limit - debit) + credit
        # available_credit_limit = ((partner_credit_limit - (amount_total - debit)) + self.amount_total)
        #
        # if (amount_total - debit) > partner_credit_limit:
        #     if not partner.over_credit:
        #         msg = 'Kullanılabilir Kredi Limit' \
        #               ' Toplamı = %s \n "%s" Firmasının Kredi Limit Toplamı Aşıldı. Lütfen Kontrol Ediniz. ' \
        #               '' % (available_credit_limit,
        #                     self.partner_id.name)
        #         raise UserError(_('Satış Teklifini Onaylayamazsınız. \n' + msg))
        #     partner.write({'credit_limit': credit - debit + self.amount_total})
        return True

    @api.multi
    def action_confirm(self):
        res = super(SaleOrder, self).action_confirm()
        for order in self:
            order.check_limit()
        return res

    @api.constrains('amount_total')
    def check_amount(self):
        for order in self:
            order.check_limit()
