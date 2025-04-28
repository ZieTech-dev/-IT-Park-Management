from odoo import models, fields, api, _
from datetime import datetime


class ITClient(models.Model):
    _name = 'it.client'
    _description = 'Client IT'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _order = 'name'

    name = fields.Char(string='Nom du client', required=True, tracking=True)
    reference = fields.Char(string='Référence', readonly=True, copy=False, default=lambda self: _('Nouveau'))
    partner_id = fields.Many2one('res.partner', string='Contact associé', required=True, tracking=True,
                                domain=[('is_company', '=', True)])
    active = fields.Boolean(default=True, tracking=True)
    
    # Adresse
    street = fields.Char(related='partner_id.street', string='Rue', readonly=False)
    street2 = fields.Char(related='partner_id.street2', string='Rue 2', readonly=False)
    zip = fields.Char(related='partner_id.zip', string='Code postal', readonly=False)
    city = fields.Char(related='partner_id.city', string='Ville', readonly=False)
    state_id = fields.Many2one(related='partner_id.state_id', string='État/Province', readonly=False)
    country_id = fields.Many2one(related='partner_id.country_id', string='Pays', readonly=False)
    
    # Contacts
    contact_ids = fields.One2many('it.client.contact', 'client_id', string='Contacts')
    
    # Sites/Localisations
    site_ids = fields.One2many('it.client.site', 'client_id', string='Sites')
    
    # Relations avec d'autres modèles
    equipment_ids = fields.One2many('it.equipment', 'client_id', string='Équipements')
    software_ids = fields.One2many('it.software', 'client_id', string='Logiciels')
    contract_ids = fields.One2many('it.contract', 'client_id', string='Contrats')
    intervention_ids = fields.One2many('it.intervention', 'client_id', string='Interventions')
    
    # Statistiques
    equipment_count = fields.Integer(string='Nombre d\'équipements', compute='_compute_counts')
    software_count = fields.Integer(string='Nombre de logiciels', compute='_compute_counts')
    contract_count = fields.Integer(string='Nombre de contrats', compute='_compute_counts')
    intervention_count = fields.Integer(string='Nombre d\'interventions', compute='_compute_counts')
    active_contract_count = fields.Integer(string='Contrats actifs', compute='_compute_counts')
    
    #ajout
    company_id = fields.Many2one('res.company', string='Entreprise', default=lambda self: self.env.company)
    
    @api.model
    def create(self, vals):
        if vals.get('reference', _('Nouveau')) == _('Nouveau'):
            vals['reference'] = self.env['ir.sequence'].next_by_code('it.client') or _('Nouveau')
        return super(ITClient, self).create(vals)
    
    @api.depends('equipment_ids', 'software_ids', 'contract_ids', 'intervention_ids')
    def _compute_counts(self):
        for client in self:
            client.equipment_count = len(client.equipment_ids)
            client.software_count = len(client.software_ids)
            client.contract_count = len(client.contract_ids)
            client.intervention_count = len(client.intervention_ids)
            client.active_contract_count = len(client.contract_ids.filtered(lambda c: c.state == 'active'))
    
    def action_view_equipment(self):
        self.ensure_one()
        return {
            'name': _('Équipements'),
            'view_mode': 'list,form',
            'res_model': 'it.equipment',
            'domain': [('client_id', '=', self.id)],
            'type': 'ir.actions.act_window',
            'context': {'default_client_id': self.id}
        }
    
    def action_view_software(self):
        self.ensure_one()
        return {
            'name': _('Logiciels'),
            'view_mode': 'list,form',
            'res_model': 'it.software',
            'domain': [('client_id', '=', self.id)],
            'type': 'ir.actions.act_window',
            'context': {'default_client_id': self.id}
        }
    
    def action_view_contracts(self):
        self.ensure_one()
        return {
            'name': _('Contrats'),
            'view_mode': 'list,form',
            'res_model': 'it.contract',
            'domain': [('client_id', '=', self.id)],
            'type': 'ir.actions.act_window',
            'context': {'default_client_id': self.id}
        }
    
    def action_view_interventions(self):
        self.ensure_one()
        return {
            'name': _('Interventions'),
            'view_mode': 'list,form',
            'res_model': 'it.intervention',
            'domain': [('client_id', '=', self.id)],
            'type': 'ir.actions.act_window',
            'context': {'default_client_id': self.id}
        }


class ITClientContact(models.Model):
    _name = 'it.client.contact'
    _description = 'Contact client IT'
    _rec_name = 'partner_id'
    
    client_id = fields.Many2one('it.client', string='Client', required=True, ondelete='cascade')
    partner_id = fields.Many2one('res.partner', string='Contact', required=True, 
                                domain=[('is_company', '=', False)])
    function = fields.Char(string='Fonction')
    is_primary = fields.Boolean(string='Contact principal')
    is_technical = fields.Boolean(string='Contact technique')
    is_billing = fields.Boolean(string='Contact facturation')
    
    # Informations de contact
    email = fields.Char(related='partner_id.email', string='Email', readonly=False)
    phone = fields.Char(related='partner_id.phone', string='Téléphone', readonly=False)
    mobile = fields.Char(related='partner_id.mobile', string='Mobile', readonly=False)
    
    @api.onchange('is_primary')
    def _onchange_is_primary(self):
        if self.is_primary:
            # Si ce contact devient primaire, désactiver le statut primaire pour les autres contacts
            for contact in self.client_id.contact_ids.filtered(lambda c: c.id != self._origin.id):
                contact.is_primary = False


class ITClientSite(models.Model):
    _name = 'it.client.site'
    _description = 'Site du client IT'
    
    name = fields.Char(string='Nom du site', required=True)
    client_id = fields.Many2one('it.client', string='Client', required=True, ondelete='cascade')
    address = fields.Char(string='Adresse')
    zip = fields.Char(string='Code postal')
    city = fields.Char(string='Ville')
    state_id = fields.Many2one('res.country.state', string='État/Province')
    country_id = fields.Many2one('res.country', string='Pays')
    
    contact_id = fields.Many2one('it.client.contact', string='Contact principal',
                                domain="[('client_id', '=', client_id)]")
    
    equipment_ids = fields.One2many('it.equipment', 'site_id', string='Équipements sur ce site')
    equipment_count = fields.Integer(string='Nombre d\'équipements', compute='_compute_equipment_count')
    
    active = fields.Boolean(default=True)
    notes = fields.Text(string='Notes')
    
    def action_view_equipment(self):
        self.ensure_one()
        return {
            'name': _('Équipements'),
            'view_mode': 'list,form',
            'res_model': 'it.equipment',
            'domain': [('site_id', '=', self.id)],
            'type': 'ir.actions.act_window',
            'context': {'default_client_id': self.client_id.id, 'default_site_id': self.id}
        }

    @api.depends('equipment_ids')
    def _compute_equipment_count(self):
        for site in self:
            site.equipment_count = len(site.equipment_ids)