# -*- coding: utf-8 -*-
from odoo import models, fields, api, _

class ITContract(models.Model):
    """Extend the IT Contract model with portal-specific functionality"""
    _inherit = 'it.contract'
    
    portal_access_url = fields.Char('URL d\'accès au portail', compute='_compute_portal_url')
    
    def _compute_portal_url(self):
        """Compute the URL for portal access to this contract"""
        base_url = self.env['ir.config_parameter'].sudo().get_param('web.base.url')
        for contract in self:
            contract.portal_access_url = f'{base_url}/my/it/contract/{contract.id}'
            
    def action_approve_via_portal(self):
        """Action executed when a client approves a contract via the portal"""
        self.ensure_one()
        if self.state == 'waiting_approval':
            self.write({'state': 'active'})
            self.message_post(
                body=_("Contrat approuvé via le portail par %s") % self.env.user.name,
                message_type='notification'
            )
        return True