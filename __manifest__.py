# -*- coding: utf-8 -*-
{
    'name': 'IT Park Management',

    'summary': 'Gestion de parc informatique pour prestataires IT',

    'description': """
        Module de gestion complète de parc informatique pour prestataires de services IT.
        - Gestion multi-client
        - Suivi matériel/logiciel
        - Interventions et incidents
        - Contrats de service
        - Facturation récurrente
        - Alertes automatiques
    """,

    'author': 'Paul Em',
    'website': 'https://paul-em-portfolio.onrender.com/',

   
    'category': 'Services/IT',
    'version': '1.0',

    
    'depends': [
        'base',
        'mail',
        'product',
        'stock',
        'account',
        'hr',
        'sale_subscription',  
        'helpdesk', 
        'portal',
    ],

    'data': [
        'security/it_park_security.xml',
        'security/ir.model.access.csv',
        'views/client_views.xml',
        'views/equipment_views.xml',
        'views/software_views.xml',
        'views/contract_views.xml',
        'views/intervention_views.xml',
        'views/alert_views.xml',
        'views/menus.xml',
        'views/portal_templates.xml',
        'data/ir_sequence_data.xml',
        'data/alert_cron.xml',
        'data/mail_templates.xml',
    ],
    
    'demo': [
        'demo/demo_data.xml',
    ],
    
    'installable': True,
    'application': True,
    'auto_install': False,
    'license': 'LGPL-3',
    
}

