# -*- coding: utf-8 -*-
{
    'name': "ÁSPIDE - Integração com contatos - Localização Brasil",

    'summary': "ÁSPIDE - Integração com Portal de dados CNPJ e certidões - Integração com contatos - Localização Brasil",

    'description': """
        ÁSPIDE - Integração com Portal de dados CNPJ e certidões - Integração com contatos Odoo - Localização Brasil
    """,

    'author': "Artios",
    'website': "https://www.artios.com.br",
    'category': 'Accounting',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['aspide_partner', 'l10n_br_fiscal'],

    # always loaded
    'data': [
        'security/security.xml',     
        'security/ir.model.access.csv',
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
