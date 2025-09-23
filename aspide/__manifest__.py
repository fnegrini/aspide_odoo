# -*- coding: utf-8 -*-
{
    'name': "ÁSPIDE",

    'summary': "ÁSPIDE - Integração com Portal de dados CNPJ e certidões",

    'description': """
        ÁSPIDE - Integração com Portal de dados CNPJ e certidões
    """,

    'author': "Artios",
    'website': "https://www.artios.com.br",
    'category': 'Accounting',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['base'],

    # always loaded
    'data': [
        'security/security.xml',     
        'security/ir.model.access.csv',
        'views/core.xml',
        'views/company.xml',
        'views/entity.xml',
        'views/external_company.xml',
        'views/person.xml',
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
