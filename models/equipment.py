from odoo import models, fields, api, _
from datetime import datetime, timedelta


class ITEquipmentType(models.Model):
    _name = 'it.equipment.type'
    _description = 'Type d\'équipement'
    _order = 'name'
    
    name = fields.Char(string='Nom du type', required=True)
    code = fields.Char(string='Code')
    description = fields.Text(string='Description')
    
    equipment_ids = fields.One2many('it.equipment', 'type_id', string='Équipements')
    equipment_count = fields.Integer(compute='_compute_equipment_count', string='Nombre d\'équipements')
    
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
    
    @api.depends('equipment_ids')
    def _compute_equipment_count(self):
        for record in self:
            record.equipment_count = len(record.equipment_ids)


class ITEquipmentBrand(models.Model):
    _name = 'it.equipment.brand'
    _description = 'Marque d\'équipement'
    _order = 'name'
    
    name = fields.Char(string='Nom de la marque', required=True)
    logo = fields.Binary(string='Logo')
    website = fields.Char(string='Site web')
    
    equipment_ids = fields.One2many('it.equipment', 'brand_id', string='Équipements')
    equipment_count = fields.Integer(compute='_compute_equipment_count', string='Nombre d\'équipements')
    
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
    
    @api.depends('equipment_ids')
    def _compute_equipment_count(self):
        for record in self:
            record.equipment_count = len(record.equipment_ids)


class ITEquipment(models.Model):
    _name = 'it.equipment'
    _description = 'Équipement IT'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _order = 'name'
    
    name = fields.Char(string='Nom de l\'équipement', required=True, tracking=True)
    reference = fields.Char(string='Référence', readonly=True, copy=False, default=lambda self: _('Nouveau'))
    serial_number = fields.Char(string='Numéro de série', tracking=True)
    
    # Relations avec d'autres modèles
    client_id = fields.Many2one('it.client', string='Client', required=True, tracking=True)
    site_id = fields.Many2one('it.client.site', string='Site', domain="[('client_id', '=', client_id)]", tracking=True)
    user_id = fields.Many2one('res.partner', string='Utilisateur final', 
                             domain="[('parent_id', '=', client_id.partner_id.id)]", tracking=True,
                             help="Employé du client qui utilise cet équipement")
    
    # Caractéristiques
    type_id = fields.Many2one('it.equipment.type', string='Type d\'équipement', required=True)
    brand_id = fields.Many2one('it.equipment.brand', string='Marque', required=True)
    model = fields.Char(string='Modèle', tracking=True)
    product_id = fields.Many2one('product.product', string='Produit associé')
    
    # Cycle de vie
    purchase_date = fields.Date(string='Date d\'achat', tracking=True)
    installation_date = fields.Date(string='Date d\'installation', tracking=True)
    warranty_end = fields.Date(string='Fin de garantie', tracking=True)
    replacement_date = fields.Date(string='Date de remplacement prévue')
    end_of_life = fields.Date(string='Fin de vie')
    
    state = fields.Selection([
        ('draft', 'Brouillon'),
        ('in_stock', 'En stock'),
        ('in_use', 'En utilisation'),
        ('in_repair', 'En réparation'),
        ('end_of_life', 'Fin de vie'),
        ('decommissioned', 'Décommissionné'),
    ], string='État', default='draft', tracking=True)
    
    active = fields.Boolean(default=True, tracking=True)
    
    # Informations techniques
    technical_specs = fields.Text(string='Spécifications techniques')
    ip_address = fields.Char(string='Adresse IP')
    mac_address = fields.Char(string='Adresse MAC')
    
    # Relations
    intervention_ids = fields.One2many('it.intervention', 'equipment_id', string='Interventions')
    intervention_count = fields.Integer(compute='_compute_intervention_count', string='Nombre d\'interventions')
    
    software_ids = fields.Many2many('it.software', 'it_equipment_software_rel', 'equipment_id', 'software_id', 
                                  string='Logiciels installés')
    software_count = fields.Integer(compute='_compute_software_count', string='Nombre de logiciels')
    
    contract_ids = fields.Many2many('it.contract', 'it_equipment_contract_rel', 'equipment_id', 'contract_id',
                                  string='Contrats associés')
    contract_count = fields.Integer(compute='_compute_contract_count', string='Nombre de contrats')
    
    # Coûts
    purchase_cost = fields.Float(string='Coût d\'achat', tracking=True)
    monthly_cost = fields.Float(string='Coût mensuel', tracking=True)
    currency_id = fields.Many2one('res.currency', string='Devise', 
                                default=lambda self: self.env.company.currency_id.id)
    
    # Notes
    notes = fields.Text(string='Notes')
    
    # Alertes
    days_to_warranty_end = fields.Integer(compute='_compute_days_to_warranty_end', string='Jours avant fin de garantie')
    warranty_status = fields.Selection([
        ('valid', 'Valide'),
        ('expires_soon', 'Expire bientôt'),
        ('expired', 'Expirée'),
    ], compute='_compute_warranty_status', string='État de la garantie', store=True)
    
    # ajout
    company_id = fields.Many2one('res.company', string='Entreprise', default=lambda self: self.env.company)
    
    @api.model
    def create(self, vals):
        if vals.get('reference', _('Nouveau')) == _('Nouveau'):
            vals['reference'] = self.env['ir.sequence'].next_by_code('it.equipment') or _('Nouveau')
        return super(ITEquipment, self).create(vals)
    
    @api.depends('intervention_ids')
    def _compute_intervention_count(self):
        for record in self:
            record.intervention_count = len(record.intervention_ids)
    
    @api.depends('software_ids')
    def _compute_software_count(self):
        for record in self:
            record.software_count = len(record.software_ids)
    
    @api.depends('contract_ids')
    def _compute_contract_count(self):
        for record in self:
            record.contract_count = len(record.contract_ids)
    
    @api.depends('warranty_end')
    def _compute_days_to_warranty_end(self):
        today = fields.Date.today()
        for record in self:
            if record.warranty_end:
                delta = record.warranty_end - today
                record.days_to_warranty_end = delta.days
            else:
                record.days_to_warranty_end = 0
    
    @api.depends('warranty_end')
    def _compute_warranty_status(self):
        today = fields.Date.today()
        soon_limit = today + timedelta(days=30)  # 30 jours pour "expire bientôt"
        
        for record in self:
            if not record.warranty_end:
                record.warranty_status = 'expired'
            elif record.warranty_end < today:
                record.warranty_status = 'expired'
            elif record.warranty_end <= soon_limit:
                record.warranty_status = 'expires_soon'
            else:
                record.warranty_status = 'valid'
    
    def action_view_interventions(self):
        self.ensure_one()
        return {
            'name': _('Interventions'),
            'view_mode': 'list,form',
            'res_model': 'it.intervention',
            'domain': [('equipment_id', '=', self.id)],
            'type': 'ir.actions.act_window',
            'context': {'default_equipment_id': self.id, 'default_client_id': self.client_id.id}
        }
    
    def action_view_software(self):
        self.ensure_one()
        return {
            'name': _('Logiciels'),
            'view_mode': 'list,form',
            'res_model': 'it.software',
            'domain': [('id', 'in', self.software_ids.ids)],
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
    
    def action_set_in_use(self):
        self.write({'state': 'in_use'})
    
    def action_set_in_repair(self):
        self.write({'state': 'in_repair'})
    
    def action_set_end_of_life(self):
        self.write({'state': 'end_of_life'})