# -*- coding: utf-8 -*-
{
    'name': "Service Maintenance",
    'summary': "",
    'description': "",
    'author': 'Daffodil Software Ltd.',
    'website': 'https://daffodilsoft.com',
    'category': 'Education',
    'license': 'LGPL-3',
    'version': '17.0',
    'depends': [
        'base',
        'product',
        'hr',
        "purchase", 
        "product", 
        "purchase_stock",
        
    ],
    "data": [
        ##Data
        'data/product_service_type.xml',
        'data/ir_sequence.xml',
        
        ##Security
        'security/ir.model.access.csv',
        'security/security_purchase_request.xml',
        
        ##Views
        'views/vehicle_type_views.xml',
        'views/driver_views.xml',
        'views/product_service_type_views.xml',
        # 'views/procurement.xml',
        'views/purchase_request_view.xml',
        'views/bill_history_views.xml',
        'views/ir_actions_client.xml',   
        'views/product.xml',
        'views/fuel_requisition_views.xml',
        'views/service_log_views.xml',
        'views/res_config_settings_views.xml',
        'views/service_type_views.xml',
        
        ##Inherited Views
        
        ##Wizard 
        'wizard/payment_wizard_views.xml',
        'wizard/report_wizard_view.xml',
        
        ##Reports
        'reports/fuel_requisition_report.xml',
        'reports/service_log_report.xml',
        'reports/purchase_requests_report.xml',
        
        ##Menus
        'views/menus.xml',

        ##Templates
        
    ],
    'assets': {
        'web.assets_backend': [
            'dsl_service_maintenance/static/src/components/**/*.xml',
            'dsl_service_maintenance/static/src/components/**/*.js',
        ],
    },
    'demo': [],
    'icon': '/dsl_service_maintenance/static/description/icon.png',
    'contributors': [
        'Rasel Ali',
        'Sohel Rana',
        'Imran Chowdhury',
    ],
}
