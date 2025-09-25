# -*- coding: utf-8 -*-

from odoo import models, fields, api, _

from .constants import PERSON_SITUATION

from .bus_utils import send_bus_notification


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


    def retrieve(self, user=False):

        try:

            aspide = self.company_id.get_aspide_connection()

            data = aspide.get_person(self.code)

            self.refresh_from_api(data)

            aspide.logout()

            if user:

                send_bus_notification(self.env, user.partner_id, \
                    subject = _('Retrieve person data'), \
                    body = _('Retreive data for person %s finished') % (self.display_name), \
                    type = 'success')

        except Exception as e:

            self.error_message = str(e)

            if user:
                
                send_bus_notification(self.env, user.partner_id, \
                    subject = _('Retrieve company data failed'), \
                    body = _('Retreive data for person %s failed. Error: %s') % (self.display_name, str(e)), \
                    type = 'danger')	

    def refresh_from_api(self, data):

        self.timestamp = data['timestamp']
        self.error_message = False
        self.name = data['name']
        self.situation = data['situation']
        self.birth = data['birth']
        self.death = data['death']

        self.refresh_companies_from_api(data['companies'])


    def refresh_companies_from_api(self, companies):

        self.companies.refresh(self)

        for company in companies:

            fields = {}

            fields['person'] = self.id
            fields['code'] = company['code']
            fields['name'] = company['name']
            fields['qualification'] = company['qualification']

            if company['qualification_id']:

                fields['qualification_id'] = company['qualification_id']['id']
                fields['qualification_name'] = company['qualification_id']['display_name']

            fields['start_date'] = company['start_date']
            fields['share_percent'] = company['share_percent']

            self.companies.create(fields)

        self.companies_searched = len(companies) > 0



    def search_companies(self, user=False):
        
        if self.companies_searched:
            return

        try:

            aspide = self.company_id.get_aspide_connection()

            data = aspide.get_person(self.code)

            self.refresh_companies_from_api(data['companies'])

            aspide.logout()

            self.companies_searched = True

            if user:

                send_bus_notification(self.env, user.partner_id, \
                    subject = _('Search companies for person'), \
                    body = _('Search companies for person %s finished') % (self.display_name), \
                    type = 'success')
					        
        except Exception as e:

            self.error_message = str(e)

            if user:
                
                send_bus_notification(self.env, user.partner_id, \
                    subject = _('Search companies for person failed'), \
                    body = _('Search companies for person %s failed. Error: %s') % (self.display_name, str(e)), \
                    type = 'danger')					


class aspide_external_person_company(models.Model):
    _name = 'aspide.external.person.company'
    _description = "External Person - Partner company"

    person = fields.Many2one('aspide.external.person', 'Person', ondelete='cascade')

    #Company data
    code = fields.Char(string="Base CNPJ", size=8, index=True)

    name = fields.Char(string="Name", size=150)

    external_company = fields.Many2one('aspide.external.company', 'External Company', ondelete='set null')

    #Partner data for relation

    qualification = fields.Char('Qualification', size=2)
    
    qualification_id = fields.Integer(string='Qualification (Id)')
    
    qualification_name = fields.Char(string='Qualification (Name)')

    start_date = fields.Date(string="Start Date")

    share_percent = fields.Float(string="Share Percentage", digits=(7,4))

    @api.model
    def refresh(self, person):
        sql = ('DELETE FROM %s WHERE person = %d' % (self._table, person.id))
        self._cr.execute(sql)
        self.env.cr.commit()


    def fetch_company(self):

        self.external_company = self.env['aspide.external.company'].check_external_company(self.code, self.person.company_id)