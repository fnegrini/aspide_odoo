# -*- coding: utf-8 -*-
from datetime import datetime, timedelta

from odoo import models, fields, api, _

from .constants import ENTITY_TYPE, PARTNER_TYPE

from .constants import\
    ENTITY_SITUATION,\
    COMPANY_SIZE

class aspide_external_company(models.Model):
    _name = 'aspide.external.company'
    _description = "External Company"
    _order = 'timestamp desc'
    _rec_names_search = ['name', 'code']

    company_id = fields.Many2one('res.company', 'Company', default=lambda self: self.env.company, ondelete='cascade')

    code = fields.Char(string="Base CNPJ", size=8, index=True)

    timestamp = fields.Datetime(string="Extracted at")

    error_message = fields.Char(string="Error Message", size=200)
    
    name = fields.Char(string="Name", size=200)

    legal_nature = fields.Char(string="Legal Nature", size=4)
    
    legal_nature_id = fields.Integer(string='Legal Nature (Id)')

    legal_nature_name = fields.Char(string='Legal Nature (Name)')

    partner_qualification = fields.Char('Partner Qualification', size=2)
    
    partner_qualification_id = fields.Integer(string='Partner Qualification (Id)')

    partner_qualification_name = fields.Char(string='Partner Qualification (Name)')

    share_capital = fields.Float(string="Share Capital", digits=(13,2))
    
    company_size = fields.Selection(string="Company Size", selection=COMPANY_SIZE, default="00")
    
    simple = fields.Boolean(string="Simple Indicator")
    
    simple_start_date = fields.Date(string="Simple Start Date")

    simple_end_date = fields.Date(string="Simple End Date")
    
    ind_mei = fields.Boolean(string="MEI indicator")
    
    regime_fetched = fields.Boolean(string="Regime data fetched")

    partners_person_fetched = fields.Boolean(string="Partners (person) fetched")

    partners = fields.One2many('aspide.external.company.partner', 'external_company', string="Partners")
   
    branches = fields.One2many('aspide.external.company.branch', 'external_company', string="Entities")

    regimes = fields.One2many('aspide.external.company.regime', 'external_company', string="Regimes")

    partner_companies = fields.Many2many('aspide.external.company',\
        relation='aspide_external_company_company',
        column1='external_company',\
        column2='partner_external_company',
        string="Partner companies")

    partners_person = fields.One2many('aspide.external.company.partner.person', 'external_company', string="Partners (Person)")

    _sql_constraints = [
        ('unique_external_company', 'unique(company_id, code)', 'Company must be unique'),
    ]

    @api.depends('code')
    def _compute_display_name(self):
        
        for rec in self:
        
            rec.display_name = "%s - %s" % (rec.code, rec.name or '')


    def retrieve(self):

        pass

    def fetch_entity_for_branches(self):

        pass

    def fetch_regimes(self):

        pass

    def partner_search_companies(self):

        pass

    def search_partners_person(self):

        pass


class aspide_external_company_partner(models.Model):
    _name = 'aspide.external.company.partner'
    _description = "External Company - Partner"
    _order = 'external_company, name'
    
    external_company = fields.Many2one('aspide.external.company', 'Company', ondelete='cascade')
    
    type = fields.Selection(string="Partner Type", selection=PARTNER_TYPE)
    
    name = fields.Char(string="Name", size=150)
    
    code = fields.Char(string="Code", size=150, index=True)

    qualification = fields.Char('Qualification', size=2)
    
    qualification_id = fields.Integer(string='Qualification (Id)')

    qualification_name = fields.Char(string='Qualification (Name)', size=150)
    
    agegroup = fields.Char('Age Group', size=1)

    agegroup_id = fields.Integer(string='Age Group (Id)')

    agegroup_name = fields.Char(string='Age Group (Name)', size=150)
    
    share_percent = fields.Float(string="Share Percentage", digits=(7,4))
    
    start_date = fields.Date(string="Start Date")
    
    country_code = fields.Char(string="Country Code", size=3)
    
    country_name = fields.Char(string="Country Name", size=100)
    
    country_id = fields.Many2one('res.country', string='Country', ondelete='restrict')

    legal_agent_code = fields.Char(string="Legal Agent Code", size=150)

    legal_agent_name = fields.Char(string="Legal Agent Name", size=150)
    
    legal_agent_qualification = fields.Char('Legal Agent Qualification', size=2)
    
    legal_agent_qualification_id = fields.Integer(string='Legal Agent Qualification (Id)')

    legal_agent_qualification_name = fields.Char(string='Legal Agent Qualification (Name)', size=150)

    companies_searched = fields.Boolean(string="Search companies done")

    partner_companies = fields.One2many('aspide.external.company.partner.company', 'partner', string="Companies", ondelete='cascade')

    @api.model
    def _name_search(self, name, args=None, operator='ilike', limit=100, name_get_uid=None):
        args = args or []
        recs = []
        if name:
            recs = self.search([('code', operator, name)] + args, limit=limit)
        if not recs:
            recs = self.search([('name', operator, name)] + args, limit=limit)
        return [rec.id for rec in recs]


    @api.depends('external_company','code','name')
    def _compute_display_name(self):
        
        for rec in self:
        
            rec.display_name = "[%s] %s - %s" % (rec.external_company.code, rec.code, rec.name or '')
               

    def search_companies(self):

        pass


class aspide_external_company_partner_company(models.Model):
    _name = 'aspide.external.company.partner.company'
    _description = "External Company - Partner company"
    _order = 'partner, code'

    partner = fields.Many2one('aspide.external.company.partner', 'Partner', ondelete='cascade')

    #Company data
    code = fields.Char(string="Base CNPJ", size=8, index=True)

    external_company = fields.Many2one('aspide.external.company', 'External Company', ondelete='set null')

    #Partner data for relation

    qualification = fields.Char('Partner Qualification', size=2)
    
    qualification_id = fields.Integer(string='Partner Qualification (Id)')

    qualification_name = fields.Char(string='Partner Qualification (Name)')

    start_date = fields.Date(string="Start Date")

    share_percent = fields.Float(string="Share Percentage", digits=(7,4))




class aspide_external_company_branch(models.Model):
    _name = 'aspide.external.company.branch'
    _description = "External Company - Entity"
    _order = 'external_company, code'
    
    external_company = fields.Many2one('aspide.external.company', 'Company', ondelete='cascade')

    code = fields.Char(string="Code", size=14, index=True)
    
    name = fields.Char(string="Name", size=150)

    type = fields.Selection(string="Type", selection=ENTITY_TYPE, default="1")

    founded = fields.Date(string="Foundation Date")

    situation = fields.Selection(string="Situation", selection=ENTITY_SITUATION, default="01")
    
    situation_date = fields.Date(string="Situation Date");

    cnae_code = fields.Char(string="CNAE", size=7)
    
    cnae_id = fields.Integer(string='CNAE (Id)')
    
    cnae_name = fields.Char(string="CNAE (Name)")

    entity = fields.Many2one('aspide.external.entity', string="Entity", ondelete='set null')


    @api.depends('code','name')
    def _compute_display_name(self):
        
        for rec in self:
        
            rec.display_name = "%s - %s" % (rec.code, rec.name or '')
               

    def fetch_entity(self):

        pass



class aspide_external_company_regime(models.Model):
    _name = 'aspide.external.company.regime'
    _description = "External Company - Regime"
    _order = "external_company, year desc"
    
    
    external_company = fields.Many2one('aspide.external.company', 'Company', ondelete='cascade')

    year = fields.Integer(string="Year")

    scp_code = fields.Char(string="CNPJ SCP", size=14)

    regime = fields.Char(string="Regime", size=100)

    bookkeeping_count = fields.Integer(string="Bookkeeping count")



class aspide_external_company_partner_person(models.Model):
    _name = 'aspide.external.company.partner.person'
    _description = "External Company - Partner person"
    _order = "external_company, level, partner"
    
    
    external_company = fields.Many2one('aspide.external.company', 'Company', ondelete='cascade')

    level = fields.Integer(string="Level")

    partner = fields.Many2one('aspide.external.company.partner', 'Partner', ondelete='set null')

    partner_external_company = fields.Many2one('aspide.external.company', 'External Person Company', related='partner.external_company')
