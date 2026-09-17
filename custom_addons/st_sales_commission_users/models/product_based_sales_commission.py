# -*- coding: utf-8 -*-
from odoo import fields, models


class ProductBasedSalesCommission(models.Model):
    """Creating product based sales commission model."""
    _name = "product.based.sales.commission"
    _description = " Product Based Sales Commission"

    sale_commission_id = fields.Many2one("sales.commission",
                                         help="Sales commission",
                                         string='Sale Commission')
    product_id = fields.Many2one('product.product', string='Product',
                                 help="Product")
    commission = fields.Float(string='Commission %', help="Commission %")
