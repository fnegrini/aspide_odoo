# -*- coding: utf-8 -*-
from odoo import api, fields, models, _
from odoo.exceptions import UserError

import re

class ResPartner(models.Model):
    _inherit = 'res.partner'

    aspide_entity = fields.Many2one('aspide.external.entity', 'Entity', ondelete='set null')

    aspide_person = fields.Many2one('aspide.external.person', 'Person', ondelete='set null')

    def aspide_update_by_entity(self):

        super(ResPartner,self).aspide_update_by_entity()

        if not self.aspide_entity.id:

            return

        #Tax framework
        if self.aspide_entity.simple:

            self.tax_framework = '1'

        elif self.aspide_entity.ind_mei:

            self.tax_framework = False
        
        else:

            self.tax_framework = '3'
            
        #Main cnae
        if self.aspide_entity.cnae_code:

            cnae_ids = self.env["l10n_br_fiscal.cnae"].search([("code_unmasked", "=", self.aspide_entity.cnae_code)])

            if len(cnae_ids) > 0:

                self.cnae_main_id = cnae_ids[0]

        #Secondary cnaes
        cnae_secondary_ids = []
        
        for cnae_secondary in self.aspide_entity.cnaes:

            cnae_ids = self.env["l10n_br_fiscal.cnae"].search([("code_unmasked", "=", cnae_secondary.code)])

            if len(cnae_ids) > 0:

                cnae_secondary_ids.append(cnae_ids[0].id)
        
        self.cnae_secondary_ids = [(6, 0, cnae_secondary_ids)]

        if self.aspide_entity.legal_nature:

            legal_nature_ids = self.env["l10n_br_fiscal.legal.nature"].search([("code_unmasked", "=", self.aspide_entity.legal_nature)], limit=1)

            if len(legal_nature_ids) > 0:
        
                self.legal_nature_id = legal_nature_ids[0]
        

        # Secondary IEs
        if len(self.aspide_entity.ies) > 0:

            #Remove previus IEs
            for sec_ie in self.state_tax_number_ids:

                sec_ie.unlink()
            
            for entity_ie in self.aspide_entity.ies:

                self.state_tax_number_ids.create({
                    'partner_id': self.id,
                    'l10n_br_ie_code': entity_ie.code,
                    'state_id': self.get_state_by_code(entity_ie.state).id
                    })

