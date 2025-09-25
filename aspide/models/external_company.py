# -*- coding: utf-8 -*-
from datetime import datetime, timedelta

from odoo import models, fields, api, _

from .bus_utils import send_bus_notification

from .constants import\
    ENTITY_SITUATION,\
    COMPANY_SIZE,\
    ENTITY_TYPE,\
    PARTNER_TYPE

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

    partner_companies_fetched = fields.Boolean(string="Partners companies fetched")

    partners_person_fetched = fields.Boolean(string="Partners (person) fetched")

    partners = fields.One2many('aspide.external.company.partner', 'external_company', string="Partners")
   
    branches = fields.One2many('aspide.external.company.branch', 'external_company', string="Entities")

    regimes = fields.One2many('aspide.external.company.regime', 'external_company', string="Regimes")

    partner_companies = fields.One2many('aspide.external.company.company', 'external_company', string="Partner Companies")

    partners_person = fields.One2many('aspide.external.company.partner.person', 'external_company', string="Partners (Person)")

    _sql_constraints = [
        ('unique_external_company', 'unique(company_id, code)', 'Company must be unique'),
    ]

    @api.depends('code')
    def _compute_display_name(self):
        
        for rec in self:
        
            rec.display_name = "%s - %s" % (rec.code, rec.name or '')


    def refresh_from_api(self, data):

        self.timestamp = data['timestamp']
        self.error_message = False
        self.name = data['name']
        self.legal_nature = data['legal_nature']

        if data['legal_nature_id']:

            self.legal_nature_id = data['legal_nature_id']['id']
            self.legal_nature_name = data['legal_nature_id']['display_name']

        self.partner_qualification = data['partner_qualification']

        if data['partner_qualification_id']:

            self.partner_qualification_id = data['partner_qualification_id']['id']
            self.partner_qualification_name = data['partner_qualification_id']['display_name']

        self.share_capital = data['share_capital']
        self.company_size = data['company_size']
        self.simple = data['simple']
        self.simple_start_date = data['simple_start_date']
        self.simple_end_date = data['simple_end_date']
        self.ind_mei = data['ind_mei']

        self.regime_fetched = False
        self.partners_person_fetched = False

        self.refresh_partners_from_api(data['partners'])

        self.refresh_branches_from_api(data['branches'])

        self.refresh_partner_companies_from_api(data['partner_companies'])

        self.refresh_partners_person_from_api(data['partners_person'])

        self.refresh_regimes_from_api(data['regimes'])



    def refresh_partner_companies_from_api(self, partner_companies):

        self.partner_companies.refresh(self)

        for partner_company in partner_companies:

            fields = {}

            fields['external_company'] = self.id
            fields['code'] = partner_company['code']
            fields['name'] = partner_company['name']

            self.partner_companies.create(fields)

        self.partner_companies_fetched = len(partner_companies) > 0


    def refresh_branches_from_api(self, branches):

        self.branches.refresh(self)

        for branch in branches:

            fields = {}

            fields['external_company'] = self.id

            fields['code'] = branch['code']
            fields['name'] = branch['name']
            fields['situation'] = branch['situation']
            fields['situation_date'] = branch['situation_date']
            fields['cnae_code'] = branch['cnae_code']
            
            if branch['cnae_id']:

                fields['cnae_id'] = branch['cnae_id']['id']
                fields['cnae_name'] = branch['cnae_id']['display_name']
            
            self.branches.create(fields)


    def refresh_partners_from_api(self, partners):

        self.partners.refresh(self)

        for partner in partners:

            fields = {}

            fields['external_company'] = self.id

            fields['type'] = partner['type']
            fields['name'] = partner['name'] or self.name
            fields['code'] = partner['code']
            fields['qualification'] = partner['qualification']

            if partner['qualification_id']:

                fields['qualification_id'] = partner['qualification_id']['id']
                fields['qualification_name'] = partner['qualification_id']['display_name']
            
            fields['agegroup'] = partner['agegroup']

            if partner['agegroup_id']:

                fields['agegroup_id'] = partner['agegroup_id']['id']
                fields['agegroup_name'] = partner['agegroup_id']['display_name']
            
            fields['share_percent'] = partner['share_percent']

            fields['start_date'] = partner['start_date']
            fields['country_code'] = partner['country_code']
            fields['country_name'] = partner['country_name']
            fields['legal_agent_code'] = partner['legal_agent_code']
            fields['legal_agent_name'] = partner['legal_agent_name']
            fields['legal_agent_qualification'] = partner['legal_agent_qualification']

            if partner['legal_agent_qualification_id']:

                fields['legal_agent_qualification_id'] = partner['legal_agent_qualification_id']['id']
                fields['legal_agent_qualification_name'] = partner['legal_agent_qualification_id']['display_name']
            
            new_partner = self.partners.create(fields)

            for partner_company in partner['partner_companies']:

                partner_company_fields = {}
                partner_company_fields['partner'] = new_partner.id
                partner_company_fields['code'] = partner_company['code']
                partner_company_fields['name'] = partner_company['name']
                partner_company_fields['qualification'] = partner_company['qualification']

                if partner_company['qualification_id']:

                    partner_company_fields['qualification_id'] = partner_company['qualification_id']['id']
                    partner_company_fields['qualification_name'] = partner_company['qualification_id']['display_name']

                partner_company_fields['start_date'] = partner_company['start_date']
                partner_company_fields['share_percent'] = partner_company['share_percent']

                new_partner.partner_companies.create(partner_company_fields)

            
    def retrieve(self, user=False):

        try:

            aspide = self.company_id.get_aspide_connection()

            company_data = aspide.get_company(self.code)

            self.refresh_from_api(company_data)

            aspide.logout()

            if user:

                send_bus_notification(self.env, user.partner_id, \
                    subject = _('Retrieve company data'), \
                    body = _('Retreive data for company %s finished') % (self.display_name), \
                    type = 'success')

        except Exception as e:

            self.error_message = str(e)

            if user:
                
                send_bus_notification(self.env, user.partner_id, \
                    subject = _('Retrieve company data failed'), \
                    body = _('Retreive data for company %s failed. Error: %s') % (self.display_name, str(e)), \
                    type = 'danger')


    @api.model
    def check_external_company(self, code, company_id):

        if company_id:
            company = company_id
        else:
            company = self.env.company
        
        external_companies = self.search([('company_id','=', company.id), ('code', '=', code)])

        if len(external_companies) > 0:

            return external_companies[0]
        
        else:

            external_company = self.create({'company_id': company.id, 'code': code})

            external_company.retrieve()

            return external_company


    def fetch_entity_for_branches(self, user=False):

        for branch in self.branches:

            if not branch.entity.id:

                branch.entity = branch.entity.check_entity(branch.code, self.company_id)

        if user:

            send_bus_notification(self.env, user.partner_id, \
                subject = _('Fetch entities of company'), \
                body = _('Fetch entities of company %s finished') % (self.display_name), \
                type = 'success')

    def fetch_regimes(self, user=False):

        if self.regime_fetched:

            return

        try:

            aspide = self.company_id.get_aspide_connection()

            data = aspide.get_company_regime(self.code)

            self.refresh_regimes_from_api(data)

            self.regime_fetched = True

            aspide.logout()

            if user:

                send_bus_notification(self.env, user.partner_id, \
                    subject = _('Fetch company regimes'), \
                    body = _('Fetch regimes of company %s finished') % (self.display_name), \
                    type = 'success')

        except Exception as e:

            self.error_message = str(e)

            if user:
                
                send_bus_notification(self.env, user.partner_id, \
                    subject = _('Fetch company regimes failed'), \
                    body = _('Fetch regimes of company %s failed. Error: %s') % (self.display_name, str(e)), \
                    type = 'danger')


    def refresh_regimes_from_api(self, regimes):

        self.regimes.refresh(self)

        for regime in regimes:

            fields = {}

            fields['external_company'] = self.id
            fields['year'] = regime['year']
            fields['scp_code'] = regime['scp_code']
            fields['regime'] = regime['regime']
            fields['bookkeeping_count'] = regime['bookkeeping_count']

            self.regimes.create(fields)
        
        self.regime_fetched = len(regimes) > 0


    def partner_search_companies(self, user=False):

        if self.partner_companies_fetched:

            return

        try:

            aspide = self.company_id.get_aspide_connection()

            data = aspide.get_company_partner_companies(self.code)

            self.refresh_partners_from_api(data['partners'])

            self.refresh_partner_companies_from_api(data['partner_companies'])

            self.partner_companies_fetched = True

            aspide.logout()

            if user:

                send_bus_notification(self.env, user.partner_id, \
                    subject = _('Search partner companies'), \
                    body = _('Search partner companies of company %s finished') % (self.display_name), \
                    type = 'success')

        except Exception as e:

            self.error_message = str(e)

            if user:
                
                send_bus_notification(self.env, user.partner_id, \
                    subject = _('Search partner companies failed'), \
                    body = _('Search partner companies of company %s failed. Error: %s') % (self.display_name, str(e)), \
                    type = 'danger')

    def search_partners_person(self, user=False):

        if self.partners_person_fetched:

            return

        try:

            aspide = self.company_id.get_aspide_connection()

            data = aspide.search_partners_person(self.code)

            self.refresh_partners_person_from_api(data['partners_person'])

            self.partners_person_fetched = True

            aspide.logout()

            if user:

                send_bus_notification(self.env, user.partner_id, \
                    subject = _('Search partners (person)'), \
                    body = _('Search partners (person) for company %s finished') % (self.display_name), \
                    type = 'success')

        except Exception as e:

            self.error_message = str(e)

            if user:
                
                send_bus_notification(self.env, user.partner_id, \
                    subject = _('Search partners (person) failed'), \
                    body = _('Search partners (person) for company %s failed. Error: %s') % (self.display_name, str(e)), \
                    type = 'danger')


    def refresh_partners_person_from_api(self, partners_person):

        self.partners_person.refresh(self)

        for partner_person in partners_person:

            fields = {}

            fields['external_company'] = self.id
            fields['level'] = partner_person['level']
            fields['partner_code'] = partner_person['partner_code']
            fields['partner_name'] = partner_person['partner_name']
            fields['partner_external_company_code'] = partner_person['partner_external_company_code']
            fields['partner_external_company_name'] = partner_person['partner_external_company_name']

            self.partners_person.create(fields)

        self.partners_person_fetched = len(partners_person) > 0



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
               

    @api.model
    def refresh(self, external_company):
        sql = ('DELETE FROM %s WHERE external_company = %d' % (self._table, external_company.id))
        self._cr.execute(sql)
        self.env.cr.commit()

    def search_companies(self):

        pass


class aspide_external_company_partner_company(models.Model):
    _name = 'aspide.external.company.partner.company'
    _description = "External Company - Partner company"
    _order = 'partner, code'

    partner = fields.Many2one('aspide.external.company.partner', 'Partner', ondelete='cascade')

    #Company data
    code = fields.Char(string="Base CNPJ", size=8, index=True)

    name = fields.Char(string='Name', size=150)

    external_company = fields.Many2one('aspide.external.company', 'External Company', ondelete='set null')

    #Partner data for relation

    qualification = fields.Char('Partner Qualification', size=2)
    
    qualification_id = fields.Integer(string='Partner Qualification (Id)')

    qualification_name = fields.Char(string='Partner Qualification (Name)')

    start_date = fields.Date(string="Start Date")

    share_percent = fields.Float(string="Share Percentage", digits=(7,4))


    def fetch_company(self):

        self.external_company = self.env['aspide.external.company'].check_external_company(self.code, self.partner.external_company.company_id)




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
               

    @api.model
    def refresh(self, external_company):
        sql = ('DELETE FROM %s WHERE external_company = %d' % (self._table, external_company.id))
        self._cr.execute(sql)
        self.env.cr.commit()


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


    @api.model
    def refresh(self, external_company):
        sql = ('DELETE FROM %s WHERE external_company = %d' % (self._table, external_company.id))
        self._cr.execute(sql)
        self.env.cr.commit()


class aspide_external_company_partner_person(models.Model):
    _name = 'aspide.external.company.partner.person'
    _description = "External Company - Partner person"
    _order = "external_company, level, partner_code"
    
    
    external_company = fields.Many2one('aspide.external.company', 'Company', ondelete='cascade')

    level = fields.Integer(string="Level")

    partner_code = fields.Char(string="CPF", size=11)

    partner_name = fields.Char(string="Partner Name", size=150)

    partner_external_company_code = fields.Char(string="Base CNPJ", size=11)

    partner_external_company_name = fields.Char(string="Company Name", size=150)

    partner_external_company = fields.Many2one('aspide.external.company', 'Person Company')


    @api.model
    def refresh(self, external_company):
        sql = ('DELETE FROM %s WHERE external_company = %d' % (self._table, external_company.id))
        self._cr.execute(sql)
        self.env.cr.commit()


    def fetch_partner_company(self):

        self.partner_external_company = self.env['aspide.external.company'].check_external_company(self.partner_external_company_code, self.external_company.company_id)



class aspide_external_company_company(models.Model):
    _name = 'aspide.external.company.company'
    _description = "External Company - Partner Company"
    _order = 'external_company, code'
    
    external_company = fields.Many2one('aspide.external.company', 'Company', ondelete='cascade')

    code = fields.Char(string="Base CNPJ", size=14, index=True)
    
    name = fields.Char(string="Name", size=150)

    partner_external_company = fields.Many2one('aspide.external.company', 'Partner Company', ondelete='set null')


    @api.model
    def refresh(self, external_company):
        sql = ('DELETE FROM %s WHERE external_company = %d' % (self._table, external_company.id))
        self._cr.execute(sql)
        self.env.cr.commit()


    def fetch_company(self):

        self.partner_external_company = self.env['aspide.external.company'].check_external_company(self.code, self.external_company.company_id)