# -*- coding: utf-8 -*-

from odoo import models, fields, _


class Company(models.Model):
    _inherit = 'res.company'
    
    #ASPIDE Partner integration

    aspide_partner_person = fields.Boolean(string="Integrate persons")

    aspide_partner_entity = fields.Boolean(string="Integrate entities", default=True)