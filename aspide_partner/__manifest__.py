# -*- coding: utf-8 -*-
{
    'name': "ÁSPIDE - Integração com contatos",

    'summary': "ÁSPIDE - Integração com Portal de dados CNPJ e certidões - Integração com contatos",

    'description': """
        ÁSPIDE - Integração com Portal de dados CNPJ e certidões - Integração com contatos Odoo
    """,

    'author': "Artios",
    'website': "https://www.artios.com.br",
    'category': 'Accounting',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['aspide', 'l10n_br'],

    # always loaded
    'data': [
        'security/security.xml',     
        'security/ir.model.access.csv',
        'views/core.xml',
        'views/company.xml',
        'views/res_partner.xml',
        'data/data.xml',
    ],
	
    # only loaded in demonstration mode
    'demo': [
        'demo/demo.xml',
    ],
    
    'application': True,
    'installable': True,
    'license': 'Other proprietary',
}
