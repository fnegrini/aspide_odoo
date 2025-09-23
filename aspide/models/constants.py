# -*- coding: utf-8 -*-

from odoo import _

ENTITY_TYPE = \
    [
     ('1', _('Main Company')), #Matriz
     ('2', _('Branch')), #Filial    
    ]

ENTITY_SITUATION = \
    [
        ('01', _('Null')), #NULA
        ('02', _('Active')), #ATIVA
        ('03', _('Suspend')), #SUSPENSA
        ('04', _('Uncapable')), #INAPTA
        ('08', _('Closed')), #BAIXADA  
    ]

PARTNER_TYPE = \
    [
        ('1', _('Legal Entity')), #PESSOA JURÍDICA
        ('2', _('Person')), #PESSOA FISICA
        ('3', _('Foreigner')), #ESTRANGEIRO
     ] 
     
COMPANY_SIZE = \
    [
        ('00', _('Not set')), #NAO INFORMADO
        ('01', _('Tiny')), #MICRO EMPRESA
        ('03', _('Small')), #EMPRESA DE PEQUENO PORTE
        ('05', _('Others')), #DEMAIS
    ]

IE_STATUS = \
    [
        ('1', _('None restriction')), #Sem restrição
        ('2', _('Blocked as UF receiver')), #Bloqueado como destinatário na UF
        ('3', _('Denied operation as UF receiver')), #Vedada operação como destinatário na UF
     ]

IE_TYPE = \
    [
        ('1', _('Normal SI')), #IE Normal
        ('2', _('Tax substitute SI')), #IE Substituto Tributário
        ('3', _('Not contributor SI')), #IE Não Contribuinte
        ('4', _('Rural Producer SI')), #IE de Produtor Rural
    ]

PERSON_SITUATION = \
    [
        ('0', _('Regular')),
        ('2', _('Suspensa')),
        ('3', _('Titular Falecido')),
        ('4', _('Pendente de Regularização')),
        ('5', _('Cancelada por Multiplicidade')),
        ('8', _('Nula')),
        ('9', _('Cancelada de Ofício')),

    ]