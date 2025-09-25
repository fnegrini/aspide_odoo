# -*- coding: utf-8 -*-
from datetime import datetime, timedelta
from odoo import models, fields, api, _




class aspide_external_person(models.Model):
    _inherit = 'aspide.external.person'


    def action_retrieve(self):

        for record in self:

            record.with_delay(description=_('Retrieving data for CPF ') + record.code, identity_key=record._table+','+str(record.id)).retrieve(self.env.user)        


    def action_search_companies(self):

        for record in self:

            record.with_delay(description=_('Searching companies for person ') + record.display_name, identity_key=record._table+','+str(record.id)).search_companies(self.env.user)        
