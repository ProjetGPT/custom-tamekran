# -*- coding: utf-8 -*-


def migrate(cr, version):
    try:
        cr.execute("update sale_order set so_type_id = so_type")
    except:
        pass
