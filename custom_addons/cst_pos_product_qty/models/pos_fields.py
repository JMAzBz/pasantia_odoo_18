# -*- coding: utf-8 -*-

from odoo import api, fields, models, _


class PosConfig(models.Model):
    _inherit = "pos.config"

    show_product_qty = fields.Boolean(string='Display Product Quantity')


class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    pos_show_product_qty = fields.Boolean(related="pos_config_id.show_product_qty", readonly=False)
