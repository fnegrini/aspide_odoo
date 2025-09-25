# -*- coding: utf-8 -*-

from odoo import models, fields, api, _


class aspide_external_entity(models.Model):
    _inherit = 'aspide.external.entity'
    _description = "External Entity"

    def action_retrieve(self):

        for record in self:

            record.with_delay(description=_('Retrieving data for CNPJ ') + record.code, identity_key=record._table+','+str(record.id)).retrieve(self.env.user)        


    def action_fetch_external_company(self):

        for record in self:
            
            record.with_delay(description=_('Fetching company for Entity ') + record.display_name, identity_key=record._table+','+str(record.id)).fetch_external_company(self.env.user)        
