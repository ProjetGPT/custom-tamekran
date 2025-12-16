from odoo import fields, api, models, _


class IskomtoReport(models.AbstractModel):
    _name = 'report.soluto_clients_ozelbagdan.rsozb_iskonto1_xlsx'
    _inherit = 'report.report_xlsx.abstract'
    _description = 'Report Xlsx'

    def generate_xlsx_report(self, workbook, data, partners):
        seq = 1
        for obj in partners:
            i = 0
            sheet = workbook.add_worksheet("Report %d" % seq)
            seq = seq + 1
            bold = workbook.add_format({"bold": True, 'text_wrap': True, "border": 1})
            border = workbook.add_format({"border": 1})
            center_bold = workbook.add_format({"bold": True, 'align': 'center', 'text_wrap': True, "border": 1})
            center = workbook.add_format({'align': 'center', 'text_wrap': True, "border": 1})
            align_left = workbook.add_format({'align': 'left', 'text_wrap': True, "border": 1})
            align_left_large_border = workbook.add_format({'align': 'left', 'text_wrap': True, "border": 2})
            align_right = workbook.add_format({'align': 'right', 'text_wrap': True, "border": 1})
            align_right_large_border = workbook.add_format({'align': 'right', 'text_wrap': True, "border": 2})
            sheet.write(i, 0, _('Sequence'), center_bold)  # Satır Sutun
            sheet.set_column('A:A', 5)
            sheet.write(i, 1, _('Product Code'), center_bold)
            sheet.set_column('B:B', 15)
            sheet.write(i, 2, _('Product Name'), center_bold)
            sheet.set_column('C:C', 40)
            sheet.write(i, 3, _('KDV'), center_bold)
            sheet.set_column('D:D', 10)
            sheet.write(i, 4, _('Quantity'), center_bold)
            sheet.set_column('E:E', 10)
            sheet.write(i, 5, _('Unit'), center_bold)
            sheet.set_column('F:F', 10)


            sheet.write(i, 6, _('List Price'), center_bold)
            sheet.set_column('G:G', 10)
            sheet.write(i, 7, _('DSC(%)'), center_bold)
            sheet.set_column('H:H', 10)

            sheet.write(i, 8, _('Net Unit Price'), center_bold)
            sheet.set_column('I:I', 18)
            sheet.write(i, 9, _('Net Total'), center_bold)      # net toplam
            sheet.set_column('J:J', 15)
            sheet.write(i, 10, _('Currency Type'), center_bold)
            sheet.set_column('K:K', 15)
            total_net_sale_price = 0
            for line in obj.order_line:
                total_net_sale_price += line.net_sale_price * line.product_uom_qty
                currency_id = line.currency_id
                currency_symbol = line.currency_id.symbol

                i = i + 1
                sheet.write(i, 0, i, align_left)
                sheet.write(i, 1, line.product_id.default_code, border)
                sheet.write(i, 2, line.product_id.name, border)
                sheet.write(i, 3, f"%{int(line.get_total_percentage_of_taxes())}", center)
                sheet.write(i, 4, line.product_uom_qty, center)
                sheet.write(i, 5, line.product_uom.name, center)
                sheet.write(i, 6, line.product_id.list_price, center)
                sheet.write(i, 7, line.discount, center)
                sheet.write(i, 8, line.net_sale_price, align_right)
                sheet.write(i, 9, line.net_sale_price * line.product_uom_qty, align_right)
                sheet.write(i, 10, currency_id.name, align_right)

            sheet.write(i + 3, 8, _('Net Total'), align_left_large_border)
            sheet.write(i + 3, 9, total_net_sale_price, align_right_large_border)
            sheet.write(i + 3, 10, obj.currency_id.name, align_right_large_border)

            sheet.write(i + 4, 8, _('Discount Amount'), align_left_large_border)
            sheet.write(i + 4, 9, round(obj.compute_discount_amount(), 2), align_right_large_border)
            sheet.write(i + 4, 10, obj.currency_id.name, align_right_large_border)

            # sheet.write(i + 5, 8, _('Discount 2'), align_left_large_border)
            # sheet.write(i + 5, 9, round(obj.amount_discount2, 2), align_right_large_border)
            # sheet.write(i + 5, 10, obj.currency_id.name, align_right_large_border)

            sheet.write(i + 5, 8, _('KDV'), align_left_large_border)
            sheet.write(i + 5, 9, obj.amount_tax, align_right_large_border)
            sheet.write(i + 5, 10, obj.currency_id.name, align_right_large_border)

            sheet.write(i + 6, 8, _('Amount Total'), align_left_large_border)
            sheet.write(i + 6, 9, obj.amount_total, align_right_large_border)
            sheet.write(i + 6, 10, obj.currency_id.name, align_right_large_border)

class IskomtosuzReport(models.AbstractModel):
    _name = 'report.soluto_clients_ozelbagdan.rsozb_iskontosuz_xlsx'
    _inherit = 'report.report_xlsx.abstract'
    _description = 'Report Xlsx'

    def generate_xlsx_report(self, workbook, data, partners):
        seq = 1
        for obj in partners:
            i = 0
            sheet = workbook.add_worksheet("Report %d" % seq)
            seq = seq + 1
            bold = workbook.add_format({"bold": True, 'text_wrap': True, "border": 1})
            border = workbook.add_format({"border": 1})
            center_bold = workbook.add_format({"bold": True, 'align': 'center', 'text_wrap': True, "border": 1})
            center = workbook.add_format({'align': 'center', 'text_wrap': True, "border": 1})
            align_left = workbook.add_format({'align': 'left', 'text_wrap': True, "border": 1})
            align_left_large_border = workbook.add_format({'align': 'left', 'text_wrap': True, "border": 2})
            align_right = workbook.add_format({'align': 'right', 'text_wrap': True, "border": 1})
            align_right_large_border = workbook.add_format({'align': 'right', 'text_wrap': True, "border": 2})
            sheet.write(i, 0, _('Sequence'), center_bold)  # Satır Sutun
            sheet.set_column('A:A', 5)
            sheet.write(i, 1, _('Product Code'), center_bold)
            sheet.set_column('B:B', 15)
            sheet.write(i, 2, _('Product Name'), center_bold)
            sheet.set_column('C:C', 40)

            sheet.write(i, 3, _('KDV'), center_bold)
            sheet.set_column('D:D', 10)

            # sheet.write(i, 3, _('KDV(%)'), center_bold)
            sheet.write(i, 4, _('Quantity'), center_bold)
            sheet.set_column('E:E', 10)
            # sheet.set_column('D:D', 10)
            sheet.write(i, 5, _('Unit'), center_bold)
            sheet.set_column('F:F', 10)
            sheet.write(i, 6, _('Net Unit Price'), center_bold)
            sheet.set_column('G:G', 18)
            sheet.write(i, 7, _('Net Total'), center_bold)
            sheet.set_column('H:H', 15)
            sheet.write(i, 8, _('Currency Type'), center_bold)
            sheet.set_column('I:I', 15)
            total_net_sale_price = 0
            for line in obj.order_line:
                total_net_sale_price += line.net_sale_price * line.product_uom_qty
                currency_id = line.currency_id
                currency_symbol = line.currency_id.symbol

                i = i + 1
                sheet.write(i, 0, i, align_left)
                sheet.write(i, 1, line.product_id.default_code, border)
                sheet.write(i, 2, line.product_id.name, border)

                sheet.write(i, 3, f"%{int(line.get_total_percentage_of_taxes())}", center)

                sheet.write(i, 4, line.product_uom_qty, center)
                sheet.write(i, 5, line.product_uom.name, center)
                # sheet.write(i, 3, line.discount, center)
                sheet.write(i, 6, line.net_sale_price, align_right)
                sheet.write(i, 7, line.price_subtotal, align_right)
                sheet.write(i, 8, currency_id.name, align_right)

            sheet.write(i + 3, 6, _('Net Total'), align_left_large_border)
            sheet.write(i + 3, 7, total_net_sale_price, align_right_large_border)
            sheet.write(i + 3, 8, obj.currency_id.name, align_right_large_border)

            sheet.write(i + 4, 6, _('KDV'), align_left_large_border)
            sheet.write(i + 4, 7, obj.amount_tax, align_right_large_border)
            sheet.write(i + 4, 8, obj.currency_id.name, align_right_large_border)

            sheet.write(i + 5, 6, _('Amount Total'), align_left_large_border)
            sheet.write(i + 5, 7, obj.amount_total, align_right_large_border)
            sheet.write(i + 5, 8, obj.currency_id.name, align_right_large_border)


class IskontoReportLine(models.AbstractModel):
    _name = 'report.soluto_clients_ozelbagdan.rslozb_iskonto1_xlsx'
    _inherit = 'report.report_xlsx.abstract'
    _description = 'Report Xlsx'

    def generate_xlsx_report(self, workbook, data, partners):
        i = 0
        sheet = workbook.add_worksheet("Report")
        bold = workbook.add_format({"bold": True, 'text_wrap': True})
        center_bold = workbook.add_format({"bold": True, 'align': 'center', 'text_wrap': True})
        align_left = workbook.add_format({'align': 'left', 'text_wrap': True})
        sheet.write(i, 0, _('Sequence'), bold)  # Satır Sutun
        sheet.set_column('A:A', 5)
        sheet.write(i, 1, _('Product Code'), bold)
        sheet.set_column('B:B', 20)
        sheet.write(i, 2, _('Product Name'), center_bold)
        sheet.set_column('C:C', 40)
        sheet.write(i, 3, _('Quantity'), bold)
        sheet.set_column('D:D', 10)
        sheet.write(i, 4, _('Unit Name'), bold)
        sheet.set_column('E:E', 15)
        sheet.write(i, 5, _('List Price'), bold)
        sheet.set_column('F:F', 15)
        sheet.write(i, 6, _('Discount(%)'), bold)
        sheet.set_column('G:G', 10)
        sheet.write(i, 7, _('Unit Price'), bold)
        sheet.set_column('H:H', 15)
        sheet.write(i, 8, _('Total Amount'), bold)
        sheet.set_column('I:I', 15)
        sheet.write(i, 9, _('Currency'), bold)
        sheet.set_column('J:J', 15)

        for obj in partners:
            currency_id = obj.currency_id
            currency_symbol = obj.currency_id.symbol
            # if currency_id.position == 'after':
            #     list_price = str(obj.product_id.list_price) + currency_symbol
            #     price_unit = str(obj.price_unit) + currency_symbol
            #     price_subtotal = str(obj.price_subtotal) + currency_symbol
            # if currency_id.position == 'before':
            #     list_price = currency_symbol + str(obj.product_id.list_price)
            #     price_unit = currency_symbol + str(obj.price_unit)
            #     price_subtotal = currency_symbol + str(obj.price_subtotal)

            i = i + 1
            sheet.write(i, 0, i)
            sheet.write(i, 1, obj.product_id.default_code)
            sheet.write(i, 2, obj.product_id.name)
            sheet.write(i, 3, obj.product_uom_qty, align_left)
            sheet.write(i, 4, obj.product_uom.name)
            sheet.write(i, 5, obj.list_price, align_left)
            sheet.write(i, 6, obj.discount, align_left)
            sheet.write(i, 7, obj.net_sale_price, align_left)
            sheet.write(i, 8, obj.price_subtotal, align_left)
            sheet.write(i, 9, currency_id.name, align_left)


class IskontosuzReportLine(models.AbstractModel):
    _name = 'report.soluto_clients_ozelbagdan.rslozb_iskontosuz_xlsx'
    _inherit = 'report.report_xlsx.abstract'
    _description = 'Report Xlsx'

    def generate_xlsx_report(self, workbook, data, partners):
        i = 0
        sheet = workbook.add_worksheet("Report")
        bold = workbook.add_format({"bold": True, 'text_wrap': True})
        center_bold = workbook.add_format({"bold": True, 'align': 'center', 'text_wrap': True})
        align_left = workbook.add_format({'align': 'left', 'text_wrap': True})
        sheet.write(i, 0, _('Sequence'), bold)  # Satır Sutun
        sheet.set_column('A:A', 5)
        sheet.write(i, 1, _('Product Code'), bold)
        sheet.set_column('B:B', 20)
        sheet.write(i, 2, _('Product Name'), center_bold)
        sheet.set_column('C:C', 40)
        sheet.write(i, 3, _('Quantity'), bold)
        sheet.set_column('D:D', 10)
        sheet.write(i, 4, _('Unit Name'), bold)
        sheet.set_column('E:E', 15)
        sheet.write(i, 5, _('Unit Price'), bold)
        sheet.set_column('F:F', 15)
        sheet.write(i, 6, _('Total Amount'), bold)
        sheet.set_column('G:G', 15)
        sheet.write(i, 7, _('Currency'), bold)
        sheet.set_column('H:H', 15)

        for obj in partners:
            currency_id = obj.currency_id
            currency_symbol = obj.currency_id.symbol
            # if currency_id.position == 'after':
            #     price_unit = str(obj.price_unit) + currency_symbol
            #     price_subtotal = str(obj.price_subtotal) + currency_symbol
            # if currency_id.position == 'before':
            #     price_unit = currency_symbol + str(obj.price_unit)
            #     price_subtotal = currency_symbol + str(obj.price_subtotal)

            i = i + 1
            sheet.write(i, 0, i)
            sheet.write(i, 1, obj.product_id.default_code)
            sheet.write(i, 2, obj.product_id.name)
            sheet.write(i, 3, obj.product_uom_qty, align_left)
            sheet.write(i, 4, obj.product_uom.name)
            sheet.write(i, 5, obj.net_sale_price, align_left)
            sheet.write(i, 6, obj.price_subtotal, align_left)
            sheet.write(i, 7, currency_id.name)

