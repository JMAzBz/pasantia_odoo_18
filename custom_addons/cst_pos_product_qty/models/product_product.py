# -*- coding: utf-8 -*-

from odoo import api, fields, models, _


class ProductProduct(models.Model):
    _inherit = 'product.product'

    @api.model
    def _load_pos_data_fields(self, config_id):
        data = super()._load_pos_data_fields(config_id)
        data += ['qty_available', 'type', 'is_storable']
        return data
