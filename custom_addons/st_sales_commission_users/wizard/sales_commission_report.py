# -*- coding: utf-8 -*-
from odoo import fields, models


class SalesCommissionReport(models.TransientModel):
    """Creating sales commission report model."""
    _name = 'sales.commission.report'
    _description = 'Sales Commission Report'

    sales_person_id = fields.Many2one('res.users', string='Sales Person',
                                      help="Sales person")
    start_date = fields.Date(string='Start Date', help="Start date")
    end_date = fields.Date(string='End Date', help="End date")

    def action_print_report(self):
        """To create a report for sale commission for a sales person"""
        data = {
            'sales_person_id': self.sales_person_id.name,
            'start_date': self.start_date,
            'end_date': self.end_date,
        }
        return self.env.ref(
            'st_sales_commission_users.sales_commission_report_action'
        ).report_action(self, data=data)
