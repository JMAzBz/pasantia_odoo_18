# -*- coding: utf-8 -*-
from odoo import fields, models


class DiscountBasedSalesCommission(models.Model):
    """Creating a discount based sales commission model."""
    _name = "discount.based.sales.commission"
    _description = " Discount Based Sales Commission"

    sale_commission_id = fields.Many2one("sales.commission",
                                         string='Sales Commission',
                                         help="Sales commission")
    discount = fields.Float(string='Discount %', help="Discount %")
    commission = fields.Float(string='Commission %', help="Commission %")
