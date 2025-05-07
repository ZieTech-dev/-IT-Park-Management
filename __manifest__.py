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
        'web',
        'contacts',
        'crm',
    ],

    'data': [
        'security/it_park_security.xml',
        'security/portal_security.xml',
        'security/ir.model.access.csv',
        'views/client_views.xml',
        'views/equipment_views.xml',
        'views/software_views.xml',
        'views/contract_views.xml',
        'views/intervention_views.xml',
        'views/alert_views.xml',
        'views/menus.xml',
        'views/portal_templates.xml',
        'views/equipment_portal_templates.xml',
        'views/portal_contract_templates.xml',
        'data/ir_sequence_data.xml',
        'data/alert_cron.xml',
        'data/mail_templates.xml',
        'data/email_templates.xml',
        'data/cron_data.xml',
    ],
    
    'demo': [
        'demo/demo_data.xml',
        'demo/demo_data.py',
    ],
    
    'installable': True,
    'application': True,
    'auto_install': False,
    'post_init_hook': 'load_demo_data',
    'license': 'LGPL-3',
    
}

