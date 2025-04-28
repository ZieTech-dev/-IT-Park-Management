from odoo import models, fields, api, _
from datetime import datetime, timedelta
from odoo.exceptions import UserError



class ITInterventionType(models.Model):
    _name = 'it.intervention.type'
    _description = 'Type d\'intervention'
    _order = 'name'
    
    name = fields.Char(string='Nom du type', required=True)
    description = fields.Text(string='Description')
    color = fields.Char(string='Couleur')
    
    intervention_ids = fields.One2many('it.intervention', 'type_id', string='Interventions')
    intervention_count = fields.Integer(compute='_compute_intervention_count', string='Nombre d\'interventions')
    
    def action_view_interventions(self):
        self.ensure_one()
        action = self.env.ref('it_park_management.action_it_intervention').read()[0]
        action['domain'] = [('type_id', '=', self.id)]
        action['context'] = {'default_type_id': self.id}
        return action
    
    @api.depends('intervention_ids')
    def _compute_intervention_count(self):
        for record in self:
            record.intervention_count = len(record.intervention_ids)


class ITInterventionPriority(models.Model):
    _name = 'it.intervention.priority'
    _description = 'Priorité d\'intervention'
    _order = 'sequence'
    
    name = fields.Char(string='Nom', required=True)
    sequence = fields.Integer(string='Séquence', default=10)
    color = fields.Char(string='Couleur')
    
    # SLA associé
    response_time_hours = fields.Float(string='Temps de réponse (heures)')
    resolution_time_hours = fields.Float(string='Temps de résolution (heures)')
    
    intervention_ids = fields.One2many('it.intervention', 'priority_id', string='Interventions')
    intervention_count = fields.Integer(compute='_compute_intervention_count', string='Nombre d\'interventions')
    
    def action_view_interventions(self):
        self.ensure_one()
        action = self.env.ref('it_park_management.action_it_intervention').read()[0]
        action['domain'] = [('priority_id', '=', self.id)]
        action['context'] = {'default_priority_id': self.id}
        return action
    
    @api.depends('intervention_ids')
    def _compute_intervention_count(self):
        for record in self:
            record.intervention_count = len(record.intervention_ids)


class ITIntervention(models.Model):
    _name = 'it.intervention'
    _description = 'Intervention IT'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _order = 'date_start desc, name'
    
    name = fields.Char(string='Titre', required=True, tracking=True)
    reference = fields.Char(string='Référence', readonly=True, copy=False, default=lambda self: _('Nouveau'))
    
    # Relations
    client_id = fields.Many2one('it.client', string='Client', required=True, tracking=True)
    equipment_id = fields.Many2one('it.equipment', string='Équipement concerné', 
                                 domain="[('client_id', '=', client_id)]", tracking=True)
    software_id = fields.Many2one('it.software', string='Logiciel concerné',
                                domain="[('client_id', '=', client_id)]", tracking=True)
    
    # Type et priorité
    type_id = fields.Many2one('it.intervention.type', string='Type d\'intervention', required=True)
    priority_id = fields.Many2one('it.intervention.priority', string='Priorité', required=True)
    
    # Assignation
    user_id = fields.Many2one('res.users', string='Assigné à', tracking=True)
    team_id = fields.Many2one('crm.team', string='Équipe')
    
    # Dates
    date_start = fields.Datetime(string='Date de début', default=fields.Datetime.now, tracking=True)
    date_end = fields.Datetime(string='Date de fin', tracking=True)
    planned_duration = fields.Float(string='Durée prévue (heures)', default=1.0)
    actual_duration = fields.Float(string='Durée réelle (heures)', compute='_compute_actual_duration', store=True)
    
    # État
    state = fields.Selection([
        ('draft', 'Brouillon'),
        ('assigned', 'Assigné'),
        ('in_progress', 'En cours'),
        ('resolved', 'Résolu'),
        ('closed', 'Clôturé'),
        ('cancelled', 'Annulé'),
    ], string='État', default='draft', tracking=True)
    
    # Lien avec le helpdesk
    helpdesk_ticket_id = fields.Many2one('helpdesk.ticket', string='Ticket Helpdesk')
    
    # Description et solution
    description = fields.Html(string='Description')
    cause = fields.Text(string='Cause')
    solution = fields.Html(string='Solution')
    
    # Suivi SLA
    sla_deadline = fields.Datetime(string='Échéance SLA', compute='_compute_sla_deadline', store=True)
    sla_status = fields.Selection([
        ('on_track', 'Dans les délais'),
        ('at_risk', 'En risque'),
        ('overdue', 'En retard'),
        ('completed', 'Complété'),
    ], string='Statut SLA', compute='_compute_sla_status', store=True)
    
    # Notes
    internal_notes = fields.Text(string='Notes internes')
    
    #ajout
    company_id = fields.Many2one('res.company', string='Entreprise', default=lambda self: self.env.company)
    
    @api.model
    def create(self, vals):
        if vals.get('reference', _('Nouveau')) == _('Nouveau'):
            vals['reference'] = self.env['ir.sequence'].next_by_code('it.intervention') or _('Nouveau')
        return super(ITIntervention, self).create(vals)
    
    @api.depends('date_start', 'date_end')
    def _compute_actual_duration(self):
        for record in self:
            if record.date_start and record.date_end:
                diff = record.date_end - record.date_start
                record.actual_duration = diff.total_seconds() / 3600.0
            else:
                record.actual_duration = 0.0
    
    @api.depends('date_start', 'priority_id')
    def _compute_sla_deadline(self):
        for record in self:
            if record.date_start and record.priority_id:
                hours = record.priority_id.resolution_time_hours
                record.sla_deadline = record.date_start + timedelta(hours=hours)
            else:
                record.sla_deadline = False
    
    @api.depends('sla_deadline', 'state')
    def _compute_sla_status(self):
        now = fields.Datetime.now()
        
        for record in self:
            if record.state in ['resolved', 'closed']:
                if record.date_end and record.sla_deadline and record.date_end <= record.sla_deadline:
                    record.sla_status = 'completed'
                else:
                    record.sla_status = 'overdue'
            elif not record.sla_deadline:
                record.sla_status = 'on_track'
            elif record.sla_deadline < now:
                record.sla_status = 'overdue'
            elif record.sla_deadline < now + timedelta(hours=2):
                record.sla_status = 'at_risk'
            else:
                record.sla_status = 'on_track'
    
    def action_set_assigned(self):
        self.write({'state': 'assigned'})
    
    def action_set_in_progress(self):
        self.write({'state': 'in_progress'})
    
    def action_set_resolved(self):
        self.write({'state': 'resolved', 'date_end': fields.Datetime.now()})
    
    def action_set_closed(self):
        self.write({'state': 'closed'})
    
    def action_set_cancelled(self):
        self.write({'state': 'cancelled'})
    
    def create_helpdesk_ticket(self):
        """Créer un ticket dans le module Helpdesk"""
        self.ensure_one()
        if self.helpdesk_ticket_id:
            raise UserError(_('Un ticket Helpdesk existe déjà pour cette intervention'))
        
        helpdesk_team = self.env['helpdesk.team'].search([], limit=1)
        
        ticket_vals = {
            'name': self.name,
            'description': self.description or '',
            'team_id': helpdesk_team.id if helpdesk_team else False,
            'partner_id': self.client_id.partner_id.id,
            'user_id': self.user_id.id,
            'priority': '2',  # Medium priority by default
        }
        
        ticket = self.env['helpdesk.ticket'].create(ticket_vals)
        self.write({'helpdesk_ticket_id': ticket.id})
        
        return {
            'name': _('Ticket Helpdesk'),
            'view_mode': 'form',
            'res_model': 'helpdesk.ticket',
            'res_id': ticket.id,
            'type': 'ir.actions.act_window',
        }