# -*- coding: utf-8 -*-
{
    'name': 'Sales Commission Users',
    'version': '19.0.1.0.1',
    'category': 'Sales',
    'summary': 'Auto-generate and track sales commissions for sales persons based on product, partner, and discount rules — with a printable commission report.',
    'description': """
    Sales Commission
    ================================
    1. Product-based Commission: Configure commission rules per product so commission lines are
       generated automatically whenever the product is sold.

    2. Discount-based Commission: Configure commission rules based on the discount percentage
       applied on a Sale Order line.

    3. Commission Lines: Auto-generated commission entries linked to the originating Sale Order,
       with the option to create a customer invoice directly from a commission line.

    4. Sales Commission Report: Wizard to filter by sales person and date range, and print a PDF
       report of commissions earned.
    """,
    'author': 'Steigend IT Solutions',
    'depends': ['sale_management', 'account'],
    'data': [
        'security/ir.model.access.csv',
        'wizard/sales_commission_report_views.xml',
        'views/commission_lines_views.xml',
        'views/res_partner_views.xml',
        'views/sale_order_views.xml',
        'views/sales_commission_views.xml',
        'views/sales_commission_menus.xml',
        'report/sales_commission_action.xml',
        'report/sales_commission_templates.xml',
    ],
    'images': ['static/description/banner.jpg'],
    'installable': True,
    'application': False,
    'auto_install': False,
    'license': 'LGPL-3',

}
