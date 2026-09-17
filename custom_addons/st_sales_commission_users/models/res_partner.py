# -*- coding: utf-8 -*-
from odoo import fields, models


class ResPartner(models.Model):
    """Inherits res partner model."""
    _inherit = 'res.partner'

    affiliated = fields.Boolean(
        string='Affiliated',
        help='To differentiate partner is affiliated or not')
