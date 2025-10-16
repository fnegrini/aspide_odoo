# -*- coding: utf-8 -*-

from odoo import models, fields, api, _

from ..models.constants import ENTITY_TYPE, ENTITY_SITUATION, COMPANY_SIZE, ENTITY_CNAE



class aspide_external_entity_search_wizard(models.TransientModel):
    _name = 'aspide.external.entity.search.wizard'
    _description = "External Entity Search Wizard"
    
    state = fields.Selection([('init', 'Initial'), ('done', 'Done')], 'state', default='init')
        
    name = fields.Char(string="Name search", size=100)

    country_state = fields.Many2one('res.country.state', string="State")

    city = fields.Char(string="City", size=100)

    cnaes = fields.One2many('aspide.external.entity.search.wizard.cnae', 'wizard', string="CNAEs")

    entities = fields.One2many('aspide.external.entity.search.wizard.entity', 'wizard', string="External Entities")
    
    def fetch_params(self):

        params = {'name': self.name}

        if self.country_state.id:
            params['addr_state'] = self.country_state.code

        if self.city:
            params['addr_city_name'] = self.city
        
        if len(self.cnaes) > 0:

            cnaes = []

            for cnae in self.cnaes:

                cnaes.append(cnae.cnae)
            
            params['cnae_code'] = cnaes

        return params


    def process(self):

        self.ensure_one()

        aspide = self.env.company.get_aspide_connection()
        
        self.state = 'done'

        search_params = self.fetch_params()

        entities_json = aspide.search_entities(search_params)
        
        for entity_json in entities_json:

            fields = {'wizard': self.id}

            fields.update(entity_json)

            self.entities.create(fields)
            
        return {

            'name': _('Search entities finished'),    
            'type': 'ir.actions.act_window',
            'res_model': 'aspide.external.entity.search.wizard',
            'view_mode': 'form',
            'view_type': 'form',
            'res_id': self.id,
            'views': [(False, 'form')],
            'target': 'new',
            'nodestroy': True,
        }



class aspide_external_entity_search_wizard_cnae(models.TransientModel):
    _name = 'aspide.external.entity.search.wizard.cnae'
    _description = "External Entity Search Wizard - CNAE"

    wizard = fields.Many2one('aspide.external.entity.search.wizard', string="Wizard")

    cnae = fields.Selection(string="CNAE", selection=ENTITY_CNAE)



class aspide_external_entity_search_wizard_entity(models.TransientModel):
    _name = 'aspide.external.entity.search.wizard.entity'
    _description = "External Entity Search Wizard - Entity"

    wizard = fields.Many2one('aspide.external.entity.search.wizard', string="Wizard")

    #----------------------------------------------------------------------------------
    # Entity Data
    #----------------------------------------------------------------------------------

    code = fields.Char(string="CNPJ", size=14)

    name = fields.Char(string="Name", size=200)

    company_name = fields.Char(string="Name Adm", size=200)
    
    type = fields.Selection(string="Type", selection=ENTITY_TYPE, default="1")
    
    situation = fields.Selection(string="Situation", selection=ENTITY_SITUATION, default="01")
    
    situation_date = fields.Date(string="Situation Date");
    
    situation_reason = fields.Char('Situation Reason', size=2)
    
    foreign_city = fields.Char(string="Foreign city", size=100)
    
    country_code = fields.Char(string="Country Code", size=3)
            
    start_date = fields.Date(string="Start Date")
    
    cnae_code = fields.Char(string="CNAE Code", size=7)

    cnae_name = fields.Char(string="CNAE Name", size=200)

    cnae_others = fields.Char(string="Other CNAE Codes", size=1000)

    addr_type = fields.Char(string="Address Type", size=20)
    
    address = fields.Char(string="Address", size=60)
    
    addr_number = fields.Char(string="Address Number", size=6)
    
    addr_comp = fields.Char(string="Address Complement", size=156)
    
    addr_district = fields.Char(string="District", size=50)
    
    addr_zip_code = fields.Char(string="Zip Code", size=8)
    
    addr_state = fields.Char(string="State", size=2)
    
    addr_city_code = fields.Char(string="City Code", size=4)

    addr_city_name = fields.Char(string="City Name", size=100)
    
    phone1_ddd = fields.Char(string="DDD Phone 1", size=5)

    phone1 = fields.Char(string="Phone 1", size=12)

    phone2_ddd = fields.Char(string="DDD Phone 2", size=5)

    phone2 = fields.Char(string="Phone 2", size=12)
    
    fax_ddd = fields.Char(string="DDD Fax", size=5)

    fax = fields.Char(string="Fax", size=12)
    
    email = fields.Char(string="E-mail", size=115)
    
    special_situation = fields.Char(string="Special Situation", size=100)
    
    special_situation_date = fields.Date(string="Special Situation Date")

    #----------------------------------------------------------------------------------
    # Company data
    #----------------------------------------------------------------------------------
    
    company_name = fields.Char(string="Company Name", size=200)
    
    legal_nature = fields.Char(string="Legal Nature Code", size=4)

    legal_nature_name = fields.Char(string="Legal Nature Name", size=100)

    partner_qualification = fields.Char('Partner Qualification', size=2)
    
    share_capital = fields.Float(string="Share Capital", digits=(13,2))
    
    company_size = fields.Selection(string="Company Size", selection=COMPANY_SIZE, default="00")

    federative_entity = fields.Char(string="Federative Entity",size=200)


    #----------------------------------------------------------------------------------
    # Simple Data
    #----------------------------------------------------------------------------------

    simple = fields.Boolean(string="Simple Indicator")
    
    simple_start_date = fields.Date(string="Simple Start Date")

    simple_end_date = fields.Date(string="Simple End Date")
    
    ind_mei = fields.Boolean(string="MEI indicator")
    
    mei_start_date = fields.Date(string="Simple Start Date")
    
    mei_end_date = fields.Date(string="Simple Start Date")


    def import_entity(self):

        self.env['aspide.external.entity'].check_entity(self.code)

        return {

            'name': _('Search entities finished'),    
            'type': 'ir.actions.act_window',
            'res_model': 'aspide.external.entity.search.wizard',
            'view_mode': 'form',
            'view_type': 'form',
            'res_id': self.wizard.id,
            'views': [(False, 'form')],
            'target': 'new',
            'nodestroy': True,
        }