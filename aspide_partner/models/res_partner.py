# -*- coding: utf-8 -*-
from odoo import api, fields, models, _
from odoo.exceptions import UserError

import re

class ResPartner(models.Model):
    _inherit = 'res.partner'

    aspide_entity = fields.Many2one('aspide.external.entity', 'Entity', ondelete='set null')

    aspide_person = fields.Many2one('aspide.external.person', 'Person', ondelete='set null')


    def aspide_check_entity(self):

        if not self.env.company.aspide_partner_entity:

            return

        if not self.vat:

            raise UserError(_('VAT is empty'))

        cnpj = re.sub(r'[^0-9]', '', self.vat)

        if len(cnpj) != 14:

            raise UserError(_('VAT format invalid'))

        self.aspide_entity = self.env['aspide.external.entity'].check_entity(cnpj, self.company_id)
        

    def aspide_check_person(self):

        if not self.env.company.aspide_partner_person:

            return

        if not self.vat:
            
            raise UserError(_('VAT is empty'))

        cpf = re.sub(r'[^0-9]', '', self.vat)

        if len(cpf) != 11:

            raise UserError(_('VAT format invalid'))

        self.aspide_person = self.env['aspide.external.person'].check_person(cpf, self.company_id)


    def aspide_check(self):

        self.aspide_entity = False
        self.aspide_person = False

        if self.is_company:

            return self.aspide_check_entity()
        
        else:

            return self.aspide_check_person()
    

    def get_state_by_code(self, code):

        condition = [
            ('country_id', '=', self.env['ir.model.data']._xmlid_lookup('base.br')[1]),
            ('code', '=', code)]

        states = self.env['res.country.state'].search(condition)
        
        if len(states) > 0 :

            return states[0]
        
        else:

            return False

    def aspide_update_by_entity(self):

        if not self.aspide_entity.id:

            raise UserError(_('Entity not set. Please Check Entity first'))
        

        self.name = self.aspide_entity.name or self.aspide_entity.name_adm
        self.complete_name = self.name
        self.commercial_company_name = self.name
        self.l10n_br_ie_code = self.aspide_entity.state_insc
        
        if self.aspide_entity.addr_type:
            self.street = (self.aspide_entity.addr_type or '') + ' ' + (self.aspide_entity.address or '') + ', ' + (self.aspide_entity.addr_number or '')
        else:
            self.street = (self.aspide_entity.address or '') + ', ' + (self.aspide_entity.addr_number or '')

        self.street2 = self.aspide_entity.addr_comp
        self.zip = self.aspide_entity.addr_zip_code
        self.city = self.aspide_entity.addr_city_name
        self.state_id = self.get_state_by_code(self.aspide_entity.addr_state)

        #Contacs fields -> only if empty
        if not self.phone:
            self.phone = self.aspide_entity.phone1
        
        if not self.mobile:
            self.mobile = self.aspide_entity.phone2
        
        if not self.email:
            self.email = self.aspide_entity.email
        
    def aspide_update_by_person(self):

        if not self.aspide_person.id:

            raise UserError(_('Person not set. Please Check Entity first'))

        self.name = self.aspide_person.name
        self.complete_name = self.name
    
    def aspide_update(self):

        if self.is_company:

            return self.aspide_update_by_entity()
        
        else:

            return self.aspide_update_by_person()        