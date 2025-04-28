from odoo import models, fields, api, _
from datetime import datetime, timedelta


class ITSoftwareCategory(models.Model):
    _name = 'it.software.category'
    _description = 'Catégorie de logiciel'
    _order = 'name'
    
    name = fields.Char(string='Nom de la catégorie', required=True)
    description = fields.Text(string='Description')
    parent_id = fields.Many2one('it.software.category', string='Catégorie parente')
    child_ids = fields.One2many('it.software.category', 'parent_id', string='Sous-catégories')
    
    software_ids = fields.One2many('it.software', 'category_id', string='Logiciels')
    software_count = fields.Integer(compute='_compute_software_count', string='Nombre de logiciels')
    
    def action_view_equipment(self):
        self.ensure_one()
        return {
            'name': _('Équipements'),
            'view_mode': 'list,form',
            'res_model': 'it.equipment',
            'domain': [('type_id', '=', self.id)],
            'type': 'ir.actions.act_window',
            'context': {'default_type_id': self.id}
        }
        
    def action_view_software(self):
        self.ensure_one()
        return {
            'name': _('Logiciels'),
            'type': 'ir.actions.act_window',
            'view_mode': 'list,form',
            'res_model': 'it.software',
            'domain': [('category_id', '=', self.id)],
            'context': {'default_category_id': self.id},
        }

    
    @api.depends('software_ids')
    def _compute_software_count(self):
        for record in self:
            record.software_count = len(record.software_ids)


class ITSoftwareEditor(models.Model):
    _name = 'it.software.editor'
    _description = 'Éditeur de logiciel'
    _order = 'name'
    
    name = fields.Char(string='Nom de l\'éditeur', required=True)
    logo = fields.Binary(string='Logo')
    website = fields.Char(string='Site web')
    
    software_ids = fields.One2many('it.software', 'editor_id', string='Logiciels')
    software_count = fields.Integer(compute='_compute_software_count', string='Nombre de logiciels')
    
    def action_view_equipment(self):
        self.ensure_one()
        return {
            'name': _('Équipements'),
            'view_mode': 'list,form',
            'res_model': 'it.equipment',
            'domain': [('type_id', '=', self.id)],
            'type': 'ir.actions.act_window',
            'context': {'default_type_id': self.id}
        }
        
    def action_view_software(self):
        self.ensure_one()
        return {
            'name': _('Logiciels'),
            'type': 'ir.actions.act_window',
            'view_mode': 'list,form',
            'res_model': 'it.software',
            'domain': [('category_id', '=', self.id)],
            'context': {'default_category_id': self.id},
        }
    
    @api.depends('software_ids')
    def _compute_software_count(self):
        for record in self:
            record.software_count = len(record.software_ids)


class ITSoftware(models.Model):
    _name = 'it.software'
    _description = 'Logiciel IT'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _order = 'name'
    
    name = fields.Char(string='Nom du logiciel', required=True, tracking=True)
    reference = fields.Char(string='Référence', readonly=True, copy=False, default=lambda self: _('Nouveau'))
    
    # Relations
    client_id = fields.Many2one('it.client', string='Client', required=True, tracking=True)
    category_id = fields.Many2one('it.software.category', string='Catégorie')
    editor_id = fields.Many2one('it.software.editor', string='Éditeur')
    
    # Caractéristiques
    version = fields.Char(string='Version', tracking=True)
    is_license = fields.Boolean(string='Est une licence', default=True)
    license_key = fields.Char(string='Clé de licence')
    license_type = fields.Selection([
        ('perpetual', 'Perpétuelle'),
        ('subscription', 'Abonnement'),
        ('open_source', 'Open Source'),
        ('freeware', 'Freeware'),
        ('trial', 'Version d\'essai'),
    ], string='Type de licence', default='perpetual', tracking=True)
    
    # Cycle de vie
    purchase_date = fields.Date(string='Date d\'achat', tracking=True)
    installation_date = fields.Date(string='Date d\'installation', tracking=True)
    expiration_date = fields.Date(string='Date d\'expiration', tracking=True)
    renewal_date = fields.Date(string='Date de renouvellement', tracking=True)
    
    # Coûts
    purchase_cost = fields.Float(string='Coût d\'achat', tracking=True)
    renewal_cost = fields.Float(string='Coût de renouvellement', tracking=True)
    currency_id = fields.Many2one('res.currency', string='Devise', 
                                default=lambda self: self.env.company.currency_id.id)
    
    # État
    state = fields.Selection([
        ('draft', 'Brouillon'),
        ('active', 'Active'),
        ('expired', 'Expirée'),
        ('to_renew', 'À renouveler'),
        ('renewed', 'Renouvelée'),
        ('cancelled', 'Annulée'),
    ], string='État', default='draft', tracking=True)
    
    active = fields.Boolean(default=True, tracking=True)
    
    # Relations
    equipment_ids = fields.Many2many('it.equipment', 'it_equipment_software_rel', 'software_id', 'equipment_id',
                                   string='Installé sur')
    equipment_count = fields.Integer(compute='_compute_equipment_count', string='Nombre d\'équipements')
    
    contract_ids = fields.Many2many('it.contract', 'it_software_contract_rel', 'software_id', 'contract_id',
                                  string='Contrats associés')
    contract_count = fields.Integer(compute='_compute_contract_count', string='Nombre de contrats')
    
    intervention_ids = fields.One2many('it.intervention', 'software_id', string='Interventions')
    intervention_count = fields.Integer(compute='_compute_intervention_count', string='Nombre d\'interventions')
    
    # Notes
    notes = fields.Text(string='Notes')
    
    # Alertes
    days_to_expiration = fields.Integer(compute='_compute_days_to_expiration', string='Jours avant expiration')
    license_status = fields.Selection([
        ('valid', 'Valide'),
        ('expires_soon', 'Expire bientôt'),
        ('expired', 'Expirée'),
    ], compute='_compute_license_status', string='État de la licence', store=True)
    
    # ajout
    company_id = fields.Many2one('res.company', string='Entreprise', default=lambda self: self.env.company)
    
    @api.model
    def create(self, vals):
        if vals.get('reference', _('Nouveau')) == _('Nouveau'):
            vals['reference'] = self.env['ir.sequence'].next_by_code('it.software') or _('Nouveau')
        return super(ITSoftware, self).create(vals)
    
    @api.depends('equipment_ids')
    def _compute_equipment_count(self):
        for record in self:
            record.equipment_count = len(record.equipment_ids)
    
    @api.depends('contract_ids')
    def _compute_contract_count(self):
        for record in self:
            record.contract_count = len(record.contract_ids)
    
    @api.depends('intervention_ids')
    def _compute_intervention_count(self):
        for record in self:
            record.intervention_count = len(record.intervention_ids)
    
    @api.depends('expiration_date')
    def _compute_days_to_expiration(self):
        today = fields.Date.today()
        for record in self:
            if record.expiration_date:
                delta = record.expiration_date - today
                record.days_to_expiration = delta.days
            else:
                record.days_to_expiration = 0
    
    @api.depends('expiration_date')
    def _compute_license_status(self):
        today = fields.Date.today()
        soon_limit = today + timedelta(days=30)  # 30 jours pour "expire bientôt"
        
        for record in self:
            if not record.expiration_date:
                record.license_status = 'valid'  # Si pas de date d'expiration, considérer comme valide (perpétuelle)
            elif record.expiration_date < today:
                record.license_status = 'expired'
            elif record.expiration_date <= soon_limit:
                record.license_status = 'expires_soon'
            else:
                record.license_status = 'valid'
    
    def action_set_active(self):
        self.write({'state': 'active'})
    
    def action_set_to_renew(self):
        self.write({'state': 'to_renew'})
    
    def action_set_renewed(self):
        self.write({'state': 'renewed'})
    
    def action_set_cancelled(self):
        self.write({'state': 'cancelled'})
    
    def action_view_equipment(self):
        self.ensure_one()
        return {
            'name': _('Équipements'),
            'view_mode': 'list,form',
            'res_model': 'it.equipment',
            'domain': [('id', 'in', self.equipment_ids.ids)],
            'type': 'ir.actions.act_window',
        }
    
    def action_view_contracts(self):
        self.ensure_one()
        return {
            'name': _('Contrats'),
            'view_mode': 'list,form',
            'res_model': 'it.contract',
            'domain': [('id', 'in', self.contract_ids.ids)],
            'type': 'ir.actions.act_window',
        }
    
    def action_view_interventions(self):
        self.ensure_one()
        return {
            'name': _('Interventions'),
            'view_mode': 'list,form',
            'res_model': 'it.intervention',
            'domain': [('software_id', '=', self.id)],
            'type': 'ir.actions.act_window',
            'context': {'default_software_id': self.id, 'default_client_id': self.client_id.id}
        }