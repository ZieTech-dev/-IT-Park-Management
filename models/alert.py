from odoo import models, fields, api, _
from datetime import datetime, timedelta


class ITAlertType(models.Model):
    _name = 'it.alert.type'
    _description = 'Type d\'alerte'
    _order = 'name'
    
    name = fields.Char(string='Nom du type', required=True)
    description = fields.Text(string='Description')
    color = fields.Char(string='Couleur')
    
    # Modèle concerné
    model = fields.Selection([
        ('it.equipment', 'Équipement'),
        ('it.software', 'Logiciel'),
        ('it.contract', 'Contrat'),
    ], string='Modèle concerné', required=True)
    
    # Configuration
    days_before = fields.Integer(string='Jours avant', default=30, 
                               help="Nombre de jours avant l'événement pour déclencher l'alerte")
    email_template_id = fields.Many2one('mail.template', string='Modèle d\'email',
                                      domain="[('model', '=', model)]")
    
    active = fields.Boolean(default=True)
    
    alert_ids = fields.One2many('it.alert', 'type_id', string='Alertes')
    alert_count = fields.Integer(compute='_compute_alert_count', string='Nombre d\'alertes')
    
    def action_view_alerts(self):
        self.ensure_one()
        action = self.env.ref('it_park_management.action_it_alert').read()[0]
        action['domain'] = [('type_id', '=', self.id)]
        action['context'] = {'default_type_id': self.id}
        return action
    
    @api.depends('alert_ids')
    def _compute_alert_count(self):
        for record in self:
            record.alert_count = len(record.alert_ids)


class ITAlert(models.Model):
    _name = 'it.alert'
    _description = 'Alerte IT'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _order = 'date desc, name'
    
    name = fields.Char(string='Titre', required=True, tracking=True)
    reference = fields.Char(string='Référence', readonly=True, copy=False, default=lambda self: _('Nouveau'))
    
    # Relations
    type_id = fields.Many2one('it.alert.type', string='Type d\'alerte', required=True)
    client_id = fields.Many2one('it.client', string='Client', tracking=True)
    
    # Références aux objets concernés
    res_model = fields.Char(string='Modèle')
    res_id = fields.Integer(string='ID')
    
    # Équipement/Logiciel/Contrat concerné (pour faciliter la recherche)
    equipment_id = fields.Many2one('it.equipment', string='Équipement')
    software_id = fields.Many2one('it.software', string='Logiciel')
    contract_id = fields.Many2one('it.contract', string='Contrat')
    
    # Dates
    date = fields.Date(string='Date de l\'événement', required=True, tracking=True)
    create_date = fields.Datetime(string='Date de création', readonly=True)
    
    # État
    state = fields.Selection([
        ('draft', 'À traiter'),
        ('in_progress', 'En cours'),
        ('done', 'Traité'),
        ('cancelled', 'Annulé'),
    ], string='État', default='draft', tracking=True)
    
    # Description
    description = fields.Text(string='Description')
    action_taken = fields.Text(string='Actions prises')
    
    # Assignation
    user_id = fields.Many2one('res.users', string='Assigné à', tracking=True)
    
    # ajout
    company_id = fields.Many2one('res.company', string='Entreprise', default=lambda self: self.env.company)
    
    @api.model
    def create(self, vals):
        if vals.get('reference', _('Nouveau')) == _('Nouveau'):
            vals['reference'] = self.env['ir.sequence'].next_by_code('it.alert') or _('Nouveau')
        return super(ITAlert, self).create(vals)
    
    def action_set_in_progress(self):
        self.write({'state': 'in_progress'})
    
    def action_set_done(self):
        self.write({'state': 'done'})
    
    def action_set_cancelled(self):
        self.write({'state': 'cancelled'})
    
    def action_view_related_record(self):
        """Voir l'enregistrement concerné par l'alerte"""
        self.ensure_one()
        
        if not self.res_model or not self.res_id:
            return
        
        return {
            'name': _('Élément concerné'),
            'view_mode': 'form',
            'res_model': self.res_model,
            'res_id': self.res_id,
            'type': 'ir.actions.act_window',
        }


class ITAlertGenerator(models.Model):
    _name = 'it.alert.generator'
    _description = 'Générateur d\'alertes'
    
    @api.model
    def _cron_generate_equipment_alerts(self):
        """Générer des alertes pour les équipements (garantie, fin de vie)"""
        alert_types = self.env['it.alert.type'].search([
            ('model', '=', 'it.equipment'),
            ('active', '=', True)
        ])
        
        for alert_type in alert_types:
            days_before = alert_type.days_before
            target_date = fields.Date.today() + timedelta(days=days_before)
            
            # Rechercher les équipements avec une garantie qui expire à la date cible
            equipments = self.env['it.equipment'].search([
                ('warranty_end', '=', target_date),
                ('state', 'in', ['in_stock', 'in_use', 'in_repair'])
            ])
            
            for equipment in equipments:
                # Vérifier si une alerte existe déjà
                existing_alert = self.env['it.alert'].search([
                    ('equipment_id', '=', equipment.id),
                    ('type_id', '=', alert_type.id),
                    ('date', '=', equipment.warranty_end),
                    ('state', 'in', ['draft', 'in_progress'])
                ])
                
                if not existing_alert:
                    # Créer une nouvelle alerte
                    alert_vals = {
                        'name': _('Fin de garantie - %s') % equipment.name,
                        'type_id': alert_type.id,
                        'client_id': equipment.client_id.id,
                        'res_model': 'it.equipment',
                        'res_id': equipment.id,
                        'equipment_id': equipment.id,
                        'date': equipment.warranty_end,
                        'description': _('La garantie de l\'équipement %s expire le %s.') % (
                            equipment.name, equipment.warranty_end)
                    }
                    self.env['it.alert'].create(alert_vals)
                    
                    # Envoyer un email si un modèle est configuré
                    if alert_type.email_template_id:
                        alert_type.email_template_id.send_mail(equipment.id)
    
    @api.model
    def _cron_generate_software_alerts(self):
        """Générer des alertes pour les logiciels (expiration de licence)"""
        alert_types = self.env['it.alert.type'].search([
            ('model', '=', 'it.software'),
            ('active', '=', True)
        ])
        
        for alert_type in alert_types:
            days_before = alert_type.days_before
            target_date = fields.Date.today() + timedelta(days=days_before)
            
            # Rechercher les logiciels avec une licence qui expire à la date cible
            softwares = self.env['it.software'].search([
                ('expiration_date', '=', target_date),
                ('state', 'in', ['active', 'to_renew'])
            ])
            
            for software in softwares:
                # Vérifier si une alerte existe déjà
                existing_alert = self.env['it.alert'].search([
                    ('software_id', '=', software.id),
                    ('type_id', '=', alert_type.id),
                    ('date', '=', software.expiration_date),
                    ('state', 'in', ['draft', 'in_progress'])
                ])
                
                if not existing_alert:
                    # Créer une nouvelle alerte
                    alert_vals = {
                        'name': _('Expiration de licence - %s') % software.name,
                        'type_id': alert_type.id,
                        'client_id': software.client_id.id,
                        'res_model': 'it.software',
                        'res_id': software.id,
                        'software_id': software.id,
                        'date': software.expiration_date,
                        'description': _('La licence du logiciel %s expire le %s.') % (
                            software.name, software.expiration_date)
                    }
                    self.env['it.alert'].create(alert_vals)
                    
                    # Envoyer un email si un modèle est configuré
                    if alert_type.email_template_id:
                        alert_type.email_template_id.send_mail(software.id)
    
    @api.model
    def _cron_generate_contract_alerts(self):
        """Générer des alertes pour les contrats (expiration, renouvellement)"""
        alert_types = self.env['it.alert.type'].search([
            ('model', '=', 'it.contract'),
            ('active', '=', True)
        ])
        
        for alert_type in alert_types:
            days_before = alert_type.days_before
            target_date = fields.Date.today() + timedelta(days=days_before)
            
            # Rechercher les contrats qui expirent à la date cible
            contracts = self.env['it.contract'].search([
                ('date_end', '=', target_date),
                ('state', 'in', ['active', 'to_renew'])
            ])
            
            for contract in contracts:
                # Vérifier si une alerte existe déjà
                existing_alert = self.env['it.alert'].search([
                    ('contract_id', '=', contract.id),
                    ('type_id', '=', alert_type.id),
                    ('date', '=', contract.date_end),
                    ('state', 'in', ['draft', 'in_progress'])
                ])
                
                if not existing_alert:
                    # Créer une nouvelle alerte
                    alert_vals = {
                        'name': _('Expiration de contrat - %s') % contract.name,
                        'type_id': alert_type.id,
                        'client_id': contract.client_id.id,
                        'res_model': 'it.contract',
                        'res_id': contract.id,
                        'contract_id': contract.id,
                        'date': contract.date_end,
                        'description': _('Le contrat %s expire le %s.') % (
                            contract.name, contract.date_end)
                    }
                    self.env['it.alert'].create(alert_vals)
                    
                    # Envoyer un email si un modèle est configuré
                    if alert_type.email_template_id:
                        alert_type.email_template_id.send_mail(contract.id)