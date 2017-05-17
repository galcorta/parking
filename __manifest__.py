# -*- coding: utf-8 -*-
{
    'name': "Parking Portal",

    'summary': """
        Parking Portal Administrator""",

    'description': """
        Portal for Parking project administration.
    """,

    'author': "MenuMovil",
    'website': "http://www.menumovil.com",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/master/openerp/addons/base/module/module_data.xml
    # for the full list
    'category': 'Other',
    'version': '1.0',

    # any module necessary for this one to work correctly
    'depends': [
        'base',
        'l10n_py_toponyms',
        'ussd_management',
        'base_geoengine',
    ],

    # always loaded
    'data': [
        'security/parking_portal_security.xml',
        'security/ir.model.access.csv',
        'views/resources.xml',
        'data/parking_module_data.xml',
        'data/parking_fixed_data.xml',
        'views/parking_view.xml',
        'views/parking_ticket_view.xml',
        'views/ticket_machine_view.xml',
        'views/price_schedule_view.xml',
        'views/price_schedule_detail_view.xml',
        'views/price_hour_view.xml',
        'views/zone_view.xml',
        'views/street_view.xml',
        'report/parking_analysis_view.xml',
    ],
    # only loaded in demonstration mode
    'demo': [
    ],
    'installable': True,
    'application': True,
    'auto_install': False,

}
