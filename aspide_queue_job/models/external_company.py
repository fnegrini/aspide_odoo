# -*- coding: utf-8 -*-
from odoo import models, fields, api, _


class aspide_external_company(models.Model):
    _inherit = 'aspide.external.company'

    def action_retrieve(self):

        for record in self:

            record.with_delay(description=_('Retrieving data for Base CNPJ ') + record.code, identity_key=record._table+','+str(record.id)).retrieve(self.env.user)        


    def action_fetch_entity_for_branches(self):

        for record in self:

            record.with_delay(description=_('Retrieving Entities for Company ') + record.display_name, identity_key=record._table+','+str(record.id)).fetch_entity_for_branches(self.env.user)        


    def action_fetch_regimes(self):

        for record in self:

            record.with_delay(description=_('Retrieving Regimes Company ') + record.display_name, identity_key=record._table+','+str(record.id)).fetch_regimes(self.env.user)        


    def action_partner_search_companies(self):

        for record in self:

            record.with_delay(description=_('Retrieving partner companies for Company ') + record.display_name, identity_key=record._table+','+str(record.id)).partner_search_companies(self.env.user)        


    def action_search_partners_person(self):

        for record in self:

            record.with_delay(description=_('Retrieving partners (person) for Company ') + record.display_name, identity_key=record._table+','+str(record.id)).search_partners_person(self.env.user)        
