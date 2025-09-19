# -*- coding: utf-8 -*-

from odoo import models, fields, _

from .api_utils import api_client

class Company(models.Model):
    _inherit = 'res.company'
    
    #ASPIDE Logon params

    aspide_url = fields.Char(string='ÁSPIDE - URL', help='https://aspide.tec.br')

    aspide_database = fields.Char(string='ÁSPIDE - Database', help='aspide')

    aspide_user = fields.Char(string="ÁSPIDE - User", help='example@yourcompany.com')

    aspide_password = fields.Char(string='ÁSPIDE - Password')

    aspide_ssh = fields.Boolean(string="ÁSPIDE - SSH", default=True)


    def aspide_test_connection(self):
        

        client = api_client(self.aspide_url, self.aspide_database, self.aspide_user, self.aspide_password, self.aspide_ssh)

        try:
            
            client.authenticate()

            return {

                    'type': 'ir.actions.client',
                    'tag': 'display_notification',
                    'params': {
                        'title': _('ÁSPIDE connection status'),
                        'message': _("Connection success!"),
                        'type': 'success',

                    },

                }
        
        except Exception as e:

            return {

                    'type': 'ir.actions.client',
                    'tag': 'display_notification',
                    'params': {
                        'title': _('ÁSPIDE connection status'),
                        'message': _("Connection failed. Server message: ") + str(e),
                        'type': 'danger',

                    },

                }            