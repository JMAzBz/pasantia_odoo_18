# -*- coding: utf-8 -*-

{
    "name": "POS Display Product Quantity",
    "summary": "Display available product stock directly in the POS screen.",
    "description": """
        This module enhances the Point of Sale interface by showing the available stock quantity for each product directly 
        on the POS product card. It helps POS users quickly view stock levels while processing orders, improving efficiency 
        and reducing stock-related errors.
        
    """,
    "author": "CodeSphere Tech",
    "website": "https://www.codespheretech.in/",
    "category": "Point of Sale",
    "version": "19.0.1.0.0",
    "sequence": 0,
    "currency": "USD",
    "price": "0",
    "depends": ["point_of_sale", ],
    "data": [
        'views/res_config_views.xml',
    ],
    "assets": {
        'point_of_sale._assets_pos': [
            'cst_pos_product_qty/static/src/app/models/product_card.js',
            'cst_pos_product_qty/static/src/app/models/product_card.xml',
        ],
    },
    "images": ["static/description/Banner.png"],
    "license": "LGPL-3",
    "installable": True,
    "application": False,
    "auto_install": False,
}
