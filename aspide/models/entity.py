# -*- coding: utf-8 -*-
from datetime import datetime, timedelta

from odoo import models, fields, api, _

from .bus_utils import send_bus_notification

from .constants import \
    ENTITY_TYPE,\
    PARTNER_TYPE,\
    ENTITY_SITUATION,\
    COMPANY_SIZE,\
    IE_TYPE,\
    IE_STATUS

IGNORED_FIELDS = [
    'id',
    'display_name',
    ]


class aspide_external_entity(models.Model):
    _name = 'aspide.external.entity'
    _description = "External Entity"
    _order = 'timestamp desc'
    _rec_names_search = ['name', 'code']

    company_id = fields.Many2one('res.company', 'Company', default=lambda self: self.env.company, ondelete='cascade')

    code = fields.Char(string="CNPJ", size=14, index=True)

    timestamp = fields.Datetime(string="Extracted at")

    error_message = fields.Char(string="Error Message", size=200)
    
    name = fields.Char(string="Name", size=200)
    
    type = fields.Selection(string="Type", selection=ENTITY_TYPE, default="1")
    
    name_adm = fields.Char(string="Administrative Name", size=200)

    situation = fields.Selection(string="Situation", selection=ENTITY_SITUATION, default="01")
    
    situation_date = fields.Date(string="Situation Date");
    
    situation_reason = fields.Char('Situation Reason', size=2)
    
    situation_reason_id = fields.Integer(string='Situation Reason (Id)')

    situation_reason_name = fields.Char(string="Situation Reason (Name)", size=100)
    
    foreign_city = fields.Char(string="Foreign city", size=100)
    
    country_code = fields.Char(string="Country Code", size=3)
    
    country_name = fields.Char(string="Country Name", size=100)
    
    country_id = fields.Many2one('res.country', string='Country')
    
    legal_nature = fields.Char(string="Legal Nature", size=4)
    
    legal_nature_id = fields.Integer(string='Legal Nature (Id)')

    legal_nature_name = fields.Char(string="Legal Nature (Name)")
    
    start_date = fields.Date(string="Start Date")
    
    cnae_code = fields.Char(string="CNAE", size=7)
    
    cnae_id = fields.Integer(string='CNAE (Id)')
    
    cnae_name = fields.Char(string="CNAE (Name)")

    state_insc = fields.Char(string="SI", size=50, index=True)

    addr_type = fields.Char(string="Address Type", size=20)
    
    address = fields.Char(string="Address", size=60)
    
    addr_number = fields.Char(string="Address Number", size=6)
    
    addr_comp = fields.Char(string="Address Complement", size=156)
    
    addr_district = fields.Char(string="District", size=50)
    
    addr_zip_code = fields.Char(string="Zip Code", size=8)
    
    addr_state = fields.Char(string="Country state", size=2)

    addr_state_id = fields.Integer(string='Country state (Id)')
    
    addr_state_name = fields.Char(string="Country state (Name)")

    addr_state_ibge = fields.Char(string="State IBGE", size=2)
    
    addr_city_code = fields.Char(string="City TOM Code", size=4)

    addr_city_id = fields.Integer(string="City (Id)", size=4)

    addr_city_ibge_code = fields.Char(string="City IBGE Code", size=5)
    
    addr_city_name = fields.Char(string="City Name", size=50)
        
    phone1 = fields.Char(string="Phone 1", size=12)
    
    phone2 = fields.Char(string="Phone 2", size=12)
    
    fax = fields.Char(string="Fax", size=12)
    
    email = fields.Char(string="E-mail", size=115)
    
    partner_qualification = fields.Char('Partner Qualification', size=2)
    
    partner_qualification_id = fields.Integer(string='Partner Qualification (Id)')

    partner_qualification_name = fields.Char(string='Partner Qualification (Name)', size=150)

    share_capital = fields.Float(string="Share Capital", digits=(13,2))
    
    company_size = fields.Selection(string="Company Size", selection=COMPANY_SIZE, default="00")
    
    simple = fields.Boolean(string="Simple Indicator")
    
    simple_start_date = fields.Date(string="Simple Start Date")

    simple_end_date = fields.Date(string="Simple End Date")
    
    ind_mei = fields.Boolean(string="MEI indicator")
    
    special_situation = fields.Char(string="Special Situation", size=23)
    
    special_situation_date = fields.Date(string="Special Situation Date")

    external_company = fields.Many2one('aspide.external.company', 'External Company', ondelete='set null')

    partners = fields.One2many('aspide.external.entity.partner', 'entity', string="Partners")

    cnaes = fields.One2many('aspide.external.entity.cnae', 'entity', string="Secondary CNAES")
    
    ies = fields.One2many('aspide.external.entity.ie', 'entity', string="State Insc")


    _sql_constraints = [
        ('unique_entity', 'unique(company_id, code)', 'Entity must be unique'),
    ]

    @api.model
    def _name_search(self, name, args=None, operator='ilike', limit=100):
        args = args or []
        recs = []
        if name:
            recs = self.search([('code', operator, name)] + args, limit=limit)
        if not recs:
            recs = self.search([('name', operator, name)] + args, limit=limit)
        if not recs:
            recs = self.search([('name_adm', operator, name)] + args, limit=limit)       
        
        return [rec.id for rec in recs]


    @api.model
    def check_entity(self, code, company_id=False):

        if company_id:
            company = company_id
        else:
            company = self.env.company
        
        entities = self.search([('company_id','=', company.id), ('code', '=', code)])

        if len(entities) > 0:

            return entities[0]
        
        else:

            entity = self.create({'company_id': company.id, 'code': code})

            entity.retrieve()

            return entity


    @api.depends('code','name','name_adm')
    def _compute_display_name(self):
        
        for rec in self:
        
            rec.display_name = "%s - %s" % (rec.code, rec.name or rec.name_adm or '')
    

    def refresh_from_api(self, entity_data):

        entity_fields = {}
        
        if self.timestamp and self.timestamp != fields.Datetime.from_string(entity_data['timestamp']):

                send_bus_notification(self.env, self.env.user.partner_id, \
                    subject = _('Entity data synchronized'), \
                    body = _('Entity %s synchronized data with ÁSPIDE') % (self.display_name), \
                    type = 'success')

        entity_fields['code'] = entity_data['code']  
        entity_fields['timestamp'] = entity_data['timestamp']
        # entity_fields['timestamp'] = entity_fields.Datetime.now()
        entity_fields['error_message'] = False
        entity_fields['name'] = entity_data['name']
        entity_fields['type'] = entity_data['type']
        entity_fields['name_adm'] = entity_data['name_adm']

        entity_fields['situation'] = entity_data['situation']
        entity_fields['situation_date'] = entity_data['situation_date']
        entity_fields['situation_reason'] = entity_data['situation_reason']

        if entity_data['situation_reason_id']:

            entity_fields['situation_reason_id'] = entity_data['situation_reason_id']['id']
            entity_fields['situation_reason_name'] = entity_data['situation_reason_id']['display_name']

        entity_fields['foreign_city'] = entity_data['foreign_city']
        entity_fields['country_code'] = entity_data['country_code']
        entity_fields['country_name'] = entity_data['country_name']
        #entity_fields['country_id'] = #TODO - Fetch local id
        
        entity_fields['legal_nature'] = entity_data['legal_nature']
        
        if entity_data['legal_nature_id']:

            entity_fields['legal_nature_id'] = entity_data['legal_nature_id']['id']
            entity_fields['legal_nature_name'] = entity_data['legal_nature_id']['display_name']

        entity_fields['start_date'] = entity_data['start_date']
        entity_fields['cnae_code'] = entity_data['cnae_code']

        if entity_data['cnae_id']:
            entity_fields['cnae_id'] = entity_data['cnae_id']['id']
            entity_fields['cnae_name'] = entity_data['cnae_id']['display_name']

        entity_fields['state_insc'] = entity_data['state_insc']
        entity_fields['addr_type'] = entity_data['addr_type']
        entity_fields['address'] = entity_data['address']
        entity_fields['addr_number'] = entity_data['addr_number']
        entity_fields['addr_comp'] = entity_data['addr_comp']
        entity_fields['addr_district'] = entity_data['addr_district']
        entity_fields['addr_zip_code'] = entity_data['addr_zip_code']
        entity_fields['addr_state'] = entity_data['addr_state']

        if entity_data['state_id']:
            entity_fields['addr_state_id'] = entity_data['state_id']['id']
            entity_fields['addr_state_name'] = entity_data['state_id']['display_name']

        entity_fields['addr_state_ibge'] = entity_data['addr_ibge_state']        
        entity_fields['addr_city_code'] = entity_data['addr_city_code']
        entity_fields['addr_city_ibge_code'] = entity_data['addr_city_ibge_code']

        if entity_data['city']:

            entity_fields['addr_city_id'] = entity_data['city']['id']
            entity_fields['addr_city_name'] = entity_data['city']['display_name']

        entity_fields['phone1'] = entity_data['phone1']
        entity_fields['phone2'] = entity_data['phone2']
        entity_fields['fax'] = entity_data['fax']
        entity_fields['email'] = entity_data['email']

        entity_fields['partner_qualification'] = entity_data['partner_qualification']

        if entity_data['partner_qualification_id']:
            entity_fields['partner_qualification_id'] = entity_data['partner_qualification_id']['id']
            entity_fields['partner_qualification_name'] = entity_data['partner_qualification_id']['display_name']

        entity_fields['share_capital'] = entity_data['share_capital']
        entity_fields['company_size'] = entity_data['company_size']
        entity_fields['simple'] = entity_data['simple']
        entity_fields['simple_start_date'] = entity_data['simple_start_date']
        entity_fields['simple_end_date'] = entity_data['simple_end_date']
        entity_fields['ind_mei'] = entity_data['ind_mei']
        entity_fields['special_situation'] = entity_data['special_situation']
        entity_fields['special_situation_date'] = entity_data['special_situation_date']

        self.write(entity_fields)

        self.refresh_partners_from_api(entity_data['partners'])

        self.refresh_cnaes_from_api(entity_data['cnaes'])

        self.refresh_ies_from_api(entity_data['ies'])


    def refresh_ies_from_api(self, ies):

        self.ies.refresh(self)

        for ie in ies:

            fields = {}

            fields['entity'] = self.id
            fields['state'] = ie['state']
            
            if ie['state_id']:

                fields['state_id'] = ie['state_id']['id']
                fields['state_name'] = ie['state_id']['display_name']
            
            fields['code'] = ie['code']
            fields['enabled'] = ie['enabled']
            fields['date'] = ie['date']
            fields['type'] = ie['type']
            fields['status'] = ie['status']

            self.ies.create(fields)


    def refresh_cnaes_from_api(self, cnaes):

        self.cnaes.refresh(self)

        for cnae in cnaes:

            fields = {}

            fields['entity'] = self.id
            fields['code'] = cnae['code']

            if cnae['cnae_id']:

                fields['cnae_id'] = cnae['cnae_id']['id']
                fields['cnae_name'] = cnae['cnae_id']['display_name']
            
            self.cnaes.create(fields)
            

    def refresh_partners_from_api(self, partners):

        self.partners.refresh(self)

        for partner in partners:

            fields = {}

            fields['entity'] = self.id

            fields['type'] = partner['type']
            fields['name'] = partner['name']
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
            
            self.partners.create(fields)
            

    def retrieve(self, user=False):
        
        try:

            aspide = self.company_id.get_aspide_connection()

            entity_data = aspide.get_entity(self.code)

            self.refresh_from_api(entity_data)

            aspide.logout()

            if user:

                send_bus_notification(self.env, user.partner_id, \
                    subject = _('Retrieve entity data'), \
                    body = _('Retreive data for Entity %s finished') % (self.display_name), \
                    type = 'success')
        
        except Exception as e:

            self.error_message = str(e)

            if user:

                send_bus_notification(self.env, user.partner_id, \
                    subject = _('Retrieve entity data failed'), \
                    body = _('Retreive data for Entity %s failed. Error: %s') % (self.display_name, str(e)), \
                    type = 'danger')


    def fetch_external_company(self, user=False):

        self.external_company = self.external_company.check_external_company(self.code[:8], self.company_id)

        if user:

            send_bus_notification(self.env, user.partner_id, \
                subject = _('Fetch company for entity'), \
                body = _('Fetch company for Entity %s finished') % (self.display_name), \
                type = 'success')


class aspide_external_entity_partner(models.Model):
    _name = 'aspide.external.entity.partner'
    _description = "External Entity - Partner"
    
    entity = fields.Many2one('aspide.external.entity', 'Entity', ondelete='cascade')
    
    type = fields.Selection(string="Partner Type", selection=PARTNER_TYPE)
    
    name = fields.Char(string="Name", size=150)
    
    code = fields.Char(string="Code", size=150, index=True)

    qualification = fields.Char('Qualification', size=2)
    
    qualification_id = fields.Integer(string='Qualification (Id)')
    
    qualification_name = fields.Char(string='Qualification (Name)')

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


    @api.model
    def _name_search(self, name, args=None, operator='ilike', limit=100):
        args = args or []
        recs = []
        if name:
            recs = self.search([('code', operator, name)] + args, limit=limit)
        if not recs:
            recs = self.search([('name', operator, name)] + args, limit=limit)
        return [rec.id for rec in recs]


    @api.depends('code','name','entity')
    def _compute_display_name(self):
        
        for rec in self:
        
            rec.display_name = "[%s] %s - %s" % (rec.entity.code, rec.code, rec.name or '')


    @api.model
    def refresh(self, entity):
        sql = ('DELETE FROM %s WHERE entity = %d' % (self._table, entity.id))
        self._cr.execute(sql)
        self.env.cr.commit()


class aspide_external_entity_cnae(models.Model):
    _name = 'aspide.external.entity.cnae'
    _description = "External Entity - Secondary CNAE"
    
    entity = fields.Many2one('aspide.external.entity', 'Entity', ondelete='cascade')
    
    code = fields.Char(string="CNAE Code", size=7, index=True)
    
    cnae_id = fields.Integer(string='CNAE (Id)')
    
    cnae_name = fields.Char(string='CNAE (Name)', size=150)

    @api.depends('code')
    def _compute_display_name(self):
        
        for rec in self:
        
            rec.display_name = "%s" % (rec.code)


    @api.model
    def refresh(self, entity):
        sql = ('DELETE FROM %s WHERE entity = %d' % (self._table, entity.id))
        self._cr.execute(sql)
        self.env.cr.commit()


class aspide_external_entity_ie(models.Model):
    _name = 'aspide.external.entity.ie'
    _description = "External Entity - State Insc"
    
    entity = fields.Many2one('aspide.external.entity', 'Entity', ondelete='cascade')

    state = fields.Char(string="State", size=2)

    state_id = fields.Integer(string='State (Id)')

    state_name = fields.Char(string='State (Name)', size=100)

    code = fields.Char(string="SI", size=50, index=True)
    
    enabled = fields.Boolean(string='Enabled')

    date = fields.Date(string="Date");

    type = fields.Selection(IE_TYPE, string = "SI Type", help="SI Type")

    status = fields.Selection(IE_STATUS, string = "SI Status", help="SI Status")


    @api.depends('code')
    def _compute_display_name(self):
        
        for rec in self:
        
            rec.display_name = "%s" % (rec.code)
            

    @api.model
    def refresh(self, entity):
        sql = ('DELETE FROM %s WHERE entity = %d' % (self._table, entity.id))
        self._cr.execute(sql)
        self.env.cr.commit()

