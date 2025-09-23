# -*- coding: utf-8 -*-
from datetime import datetime, timedelta
from odoo import models, fields, api, _
from .constants import PERSON_SITUATION



class aspide_external_person(models.Model):
    _name = 'aspide.external.person'
    _description = "External Person"
    _order = 'timestamp desc'
    _rec_names_search = ['name', 'code']

    company_id = fields.Many2one('res.company', 'Company', default=lambda self: self.env.company, ondelete='cascade')

    code = fields.Char(string="CPF", size=11, index=True)

    timestamp = fields.Datetime(string="Extracted at")

    error_message = fields.Char(string="Error Message", size=200)
    
    name = fields.Char(string="Name", size=200)
    
    situation = fields.Selection(string="Situation", selection=PERSON_SITUATION)
    
    birth = fields.Date(string="Birth Date");
    
    death = fields.Integer(string="Death")

    companies_searched = fields.Boolean(string="Search companies done")

    companies = fields.One2many('aspide.external.person.company', 'person', string="Companies")
    
    _sql_constraints = [
        ('unique_entity', 'unique(company_id, code)', 'Person must be unique'),
    ]
    

    @api.depends('code','name')
    def _compute_display_name(self):
        
        for rec in self:
        
            rec.display_name = "%s - %s" % (rec.code, rec.name or '')


    def retrieve(self):

        pass


    def search_companies(self):

        pass



class aspide_external_person_company(models.Model):
    _name = 'aspide.external.person.company'
    _description = "External Person - Partner company"

    person = fields.Many2one('aspide.external.person', 'Person', ondelete='cascade')

    #Company data
    code = fields.Char(string="Base CNPJ", size=8, index=True)

    external_company = fields.Many2one('aspide.external.company', 'External Company', ondelete='set null')

    #Partner data for relation

    qualification = fields.Char('Qualification', size=2)
    
    qualification_id = fields.Integer(string='Qualification (Id)')
    
    qualification_name = fields.Char(string='Qualification (Name)')

    start_date = fields.Date(string="Start Date")

    share_percent = fields.Float(string="Share Percentage", digits=(7,4))

