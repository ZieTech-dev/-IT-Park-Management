from odoo import models, fields, api, _
from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta
from odoo.exceptions import UserError
from odoo.exceptions import ValidationError

import logging
_logger = logging.getLogger(__name__)



class ITContractType(models.Model):
    _name = 'it.contract.type'
    _description = 'Type de contrat'
    _order = 'name'
    
    name = fields.Char(string='Nom du type', required=True)
    description = fields.Text(string='Description')
    
    contract_ids = fields.One2many('it.contract', 'type_id', string='Contrats')
    contract_count = fields.Integer(compute='_compute_contract_count', string='Nombre de contrats')
    
    def action_view_contracts(self):
        # Ajoute ici la logique qui sera exécutée lorsque le bouton sera cliqué
        return {
            'type': 'ir.actions.act_window',
            'name': 'Contrats',
            'res_model': 'it.contract',  # Le modèle à afficher
            'view_mode': 'tree,form',
            'domain': [('type_id', '=', self.id)],  # Ajoute la logique de filtrage
        }
    
    @api.depends('contract_ids')
    def _compute_contract_count(self):
        for record in self:
            record.contract_count = len(record.contract_ids)


class ITContract(models.Model):
    _name = 'it.contract'
    _description = 'Contrat de service IT'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _order = 'date_start desc, name'
    
    name = fields.Char(string='Nom du contrat', required=True, tracking=True)
    reference = fields.Char(string='Référence', readonly=True, copy=False, default=lambda self: _('Nouveau'))
    
    # Relations
    client_id = fields.Many2one('it.client', string='Client', required=True, tracking=True, ondelete='restrict')
    type_id = fields.Many2one('it.contract.type', string='Type de contrat', required=True)
    subscription_id = fields.Many2one('sale.order', string='Abonnement Odoo')
    
    # Dates
    date_start = fields.Date(string='Date de début', required=True, tracking=True)
    date_end = fields.Date(string='Date de fin', tracking=True)
    
    # Facturation
    invoicing_frequency = fields.Selection([
        ('monthly', 'Mensuelle'),
        ('quarterly', 'Trimestrielle'),
        ('semi_annual', 'Semestrielle'),
        ('annual', 'Annuelle'),
        ('one_time', 'Unique'),
    ], string='Fréquence de facturation', default='monthly', required=True, tracking=True)
    
    next_invoice_date = fields.Date(string='Prochaine facturation', compute='_compute_next_invoice_date', store=True)
    
    price = fields.Float(string='Montant du contrat', tracking=True)
    recurring_amount = fields.Float(string='Montant récurrent', tracking=True)
    currency_id = fields.Many2one('res.currency', string='Devise', 
                                default=lambda self: self.env.company.currency_id.id)
    
    # État
    state = fields.Selection([
        ('draft', 'Brouillon'),
        ('waiting_approval', 'En attente d\'acceptation'),
        ('active', 'Actif'),
        ('to_renew', 'À renouveler'),
        ('expired', 'Expiré'),
        ('cancelled', 'Annulé'),
    ], string='État', default='draft', tracking=True, compute='_compute_state', store=True)
    
    active = fields.Boolean(default=True, tracking=True)
    
    # Relations
    equipment_ids = fields.Many2many('it.equipment', 'it_equipment_contract_rel', 'contract_id', 'equipment_id',
                                   string='Équipements couverts')
    equipment_count = fields.Integer(compute='_compute_equipment_count', string='Nombre d\'équipements')
    
    software_ids = fields.Many2many('it.software', 'it_software_contract_rel', 'contract_id', 'software_id',
                                  string='Logiciels couverts')
    software_count = fields.Integer(compute='_compute_software_count', string='Nombre de logiciels')
    
    invoice_ids = fields.One2many('account.move', 'contract_id', string='Factures')
    invoice_count = fields.Integer(compute='_compute_invoice_count', string='Nombre de factures')
    
    # Termes du contrat
    description = fields.Text(string='Description du contrat')
    terms = fields.Html(string='Termes et conditions')
    
    # SLA (Service Level Agreement)
    sla_response_time = fields.Selection([
        ('0', 'Immédiat'),
        ('1', '1 heure'),
        ('2', '2 heures'),
        ('4', '4 heures'),
        ('8', '8 heures'),
        ('24', '24 heures'),
        ('48', '48 heures'),
    ], string='Temps de réponse SLA', default='4')
    
    sla_resolution_time = fields.Selection([
        ('4', '4 heures'),
        ('8', '8 heures'),
        ('24', '24 heures'),
        ('48', '48 heures'),
        ('72', '72 heures'),
    ], string='Temps de résolution SLA', default='24')
    
    # Notes
    notes = fields.Text(string='Notes')
    
    # Alertes
    days_to_expiration = fields.Integer(compute='_compute_days_to_expiration', string='Jours avant expiration', store=True)
    
    #ajout
    company_id = fields.Many2one('res.company', string='Entreprise', default=lambda self: self.env.company)
    
    @api.model
    def create(self, vals):
        if vals.get('reference', _('Nouveau')) == _('Nouveau'):
            vals['reference'] = self.env['ir.sequence'].next_by_code('it.contract') or _('Nouveau')
        return super(ITContract, self).create(vals)
    
    @api.depends('equipment_ids')
    def _compute_equipment_count(self):
        for record in self:
            record.equipment_count = len(record.equipment_ids)
    
    @api.depends('software_ids')
    def _compute_software_count(self):
        for record in self:
            record.software_count = len(record.software_ids)
    
    @api.depends('invoice_ids')
    def _compute_invoice_count(self):
        for record in self:
            record.invoice_count = len(record.invoice_ids)
    
    @api.depends('date_start', 'date_end')
    def _compute_days_to_expiration(self):
        today = fields.Date.today()
        for record in self:
            try:
                if record.date_end:
                    delta = record.date_end - today
                    record.days_to_expiration = delta.days
                else:
                    record.days_to_expiration = 0
            except Exception as e:
                _logger.error(f"Erreur lors du calcul des jours avant expiration: {e}")
                record.days_to_expiration = 0
    
    @api.depends('date_start', 'date_end')
    def _compute_state(self):
        today = fields.Date.today()
        soon_limit = today + timedelta(days=30)  # 30 jours pour "à renouveler"
        
        for record in self:
            try:
                if record.state == 'cancelled':
                    continue  # Garder l'état "annulé" s'il a été défini manuellement
                    
                if not record.date_end:
                    record.state = 'active'  # Si pas de date de fin, considérer comme actif
                elif record.date_end < today:
                    record.state = 'expired'
                elif record.date_end <= soon_limit:
                    record.state = 'to_renew'
                else:
                    record.state = 'active'
            except Exception as e:
                _logger.error(f"Erreur lors du calcul de l'état du contrat {record.id}: {e}")
                record.state = 'draft'  # État par défaut en cas d'erreur
    
    @api.depends('date_start', 'invoicing_frequency')
    def _compute_next_invoice_date(self):
        today = fields.Date.today()
        
        for record in self:
            if record.state != 'active' or not record.date_start:
                record.next_invoice_date = False
                continue
                
            # Protection contre les boucles infinies
            max_iterations = 1000  # Une limite raisonnable
            
            # Calculer la prochaine date basée sur la fréquence
            if record.invoicing_frequency == 'monthly':
                increment = relativedelta(months=1)
            elif record.invoicing_frequency == 'quarterly':
                increment = relativedelta(months=3)
            elif record.invoicing_frequency == 'semi_annual':
                increment = relativedelta(months=6)
            elif record.invoicing_frequency == 'annual':
                increment = relativedelta(years=1)
            else:  # one_time
                record.next_invoice_date = False
                continue
            
            # Trouver la prochaine date à partir de la date de début
            next_date = record.date_start
            count = 0
            
            while next_date <= today and count < max_iterations:
                next_date += increment
                count += 1
                
            if count >= max_iterations:
                # Gérer le cas où la boucle a atteint sa limite
                _logger.warning("Boucle infinie potentielle détectée pour le contrat %s", record.name)
                record.next_invoice_date = today + increment
            else:
                record.next_invoice_date = next_date
    
    
    # @api.depends('date_start', 'invoicing_frequency')
    # def _compute_next_invoice_date(self):
    #     today = fields.Date.today()
        
    #     for record in self:
    #         if record.state != 'active' or not record.date_start:
    #             record.next_invoice_date = False
    #             continue
            
    #         # Approche simplifiée pour éviter les boucles infinies
    #         # On ajoute directement la période à la date du jour
    #         if record.invoicing_frequency == 'monthly':
    #             record.next_invoice_date = today + relativedelta(months=1)
    #         elif record.invoicing_frequency == 'quarterly':
    #             record.next_invoice_date = today + relativedelta(months=3)
    #         elif record.invoicing_frequency == 'semi_annual':
    #             record.next_invoice_date = today + relativedelta(months=6)
    #         elif record.invoicing_frequency == 'annual':
    #             record.next_invoice_date = today + relativedelta(years=1)
    #         else:  # one_time
    #             record.next_invoice_date = False
    
    
    # @api.depends('date_start', 'invoicing_frequency')
    # def _compute_next_invoice_date(self):
    #     today = fields.Date.today()
        
    #     for record in self:
    #         if record.state != 'active' or not record.date_start:
    #             record.next_invoice_date = False
    #             continue
            
    #         # Approche simplifiée pour éviter les boucles infinies
    #         if record.invoicing_frequency == 'monthly':
    #             record.next_invoice_date = today + relativedelta(months=1)
    #         elif record.invoicing_frequency == 'quarterly':
    #             record.next_invoice_date = today + relativedelta(months=3)
    #         elif record.invoicing_frequency == 'semi_annual':
    #             record.next_invoice_date = today + relativedelta(months=6)
    #         elif record.invoicing_frequency == 'annual':
    #             record.next_invoice_date = today + relativedelta(years=1)
    #         else:  # one_time
    #             record.next_invoice_date = False
    
    
    
    
    # @api.depends('date_start', 'invoicing_frequency')
    # def _compute_next_invoice_date(self):
    #     today = fields.Date.today()
        
    #     for record in self:
    #         try:
    #             if record.state != 'active' or not record.date_start:
    #                 record.next_invoice_date = False
    #                 continue
                
    #             # Vérifier si client_id est valide
    #             if record.client_id and not self.env['it.client'].browse(record.client_id.id).exists():
    #                 record.next_invoice_date = False
    #                 continue
                
    #             # Approche simplifiée pour éviter les boucles infinies
    #             if record.invoicing_frequency == 'monthly':
    #                 record.next_invoice_date = today + relativedelta(months=1)
    #             elif record.invoicing_frequency == 'quarterly':
    #                 record.next_invoice_date = today + relativedelta(months=3)
    #             elif record.invoicing_frequency == 'semi_annual':
    #                 record.next_invoice_date = today + relativedelta(months=6)
    #             elif record.invoicing_frequency == 'annual':
    #                 record.next_invoice_date = today + relativedelta(years=1)
    #             else:  # one_time
    #                 record.next_invoice_date = False
    #         except Exception as e:
    #             _logger.error(f"Erreur lors du calcul de la prochaine date de facturation pour le contrat {record.id}: {e}")
    #             record.next_invoice_date = False
                
    
    def action_submit_for_approval(self):
        self.write({'state': 'waiting_approval'})
        
        template = self.env.ref('it_park_management.email_template_contract_approval')
        
        try:
            # Méthode pour Odoo 18 - utiliser render et send
            email_values = {
                'subject': template._render_field('subject', [self.id])[self.id],
                'body_html': template._render_field('body_html', [self.id])[self.id],
                'email_to': template._render_field('email_to', [self.id])[self.id],
                'email_from': template._render_field('email_from', [self.id])[self.id],
            }
            
            # Vérifier que le rendu s'est bien passé
            if '${object' in email_values.get('body_html', ''):
                _logger.error("Le rendu du template a échoué, des variables sont restées non évaluées")
                
                # Alternative: créer un email avec des valeurs fixes
                email_values = {
                    'subject': f'Contrat {self.name} - Demande d\'approbation',
                    'body_html': f'''
                        <div style="margin: 0px; padding: 0px;">
                            <p style="margin: 0px; padding: 0px; font-size: 13px;">
                                Bonjour {self.client_id.name or "Client"},
                                <br/><br/>
                                Un nouveau contrat de service informatique a été créé pour vous et est en attente de votre approbation.
                                <br/><br/>
                                <strong>Référence:</strong> {self.reference or "N/A"}<br/>
                                <strong>Nom:</strong> {self.name or "N/A"}<br/>
                                <strong>Date de début:</strong> {self.date_start or "N/A"}<br/>
                                <strong>Date de fin:</strong> {self.date_end or "N/A"}<br/>
                                <strong>Montant:</strong> {self.price or 0.0} {self.currency_id.name or "EUR"}<br/>
                                <br/>
                                Pour consulter les détails et approuver ce contrat, veuillez cliquer sur le lien suivant:
                                <br/><br/>
                                <a href="/my/it/contract/{self.id}" style="background-color: #875A7B; padding: 8px 16px 8px 16px; text-decoration: none; color: #fff; border-radius: 5px; font-size:13px;">
                                    Voir le contrat
                                </a>
                                <br/><br/>
                                Cordialement,<br/>
                                L'équipe {self.company_id.name or ""}
                            </p>
                        </div>
                    ''',
                    'email_to': self.client_id.partner_id.email if self.client_id and self.client_id.partner_id else "",
                    'email_from': self.company_id.email or self.env.user.email_formatted,
                }
            
            # Créer et envoyer l'email
            mail = self.env['mail.mail'].sudo().create(email_values)
            mail_sent = mail.send(raise_exception=False)
            
            # Journaliser le résultat
            if mail_sent:
                _logger.info(f"Email envoyé avec succès pour le contrat {self.name} (ID: {self.id})")
                self.message_post(body="Email de demande d'approbation envoyé avec succès")
            else:
                _logger.error(f"Échec d'envoi d'email pour le contrat {self.name} (ID: {self.id})")
                self.message_post(body="Échec d'envoi de l'email de demande d'approbation")
        
        except Exception as e:
            _logger.error(f"Erreur lors de l'envoi de l'email: {e}")
            # Approche de dernier recours - utiliser l'API message_post
            partner_ids = []
            if self.client_id and self.client_id.partner_id:
                partner_ids.append(self.client_id.partner_id.id)
            
            self.message_post(
                body=f'''
                    <div style="margin: 0px; padding: 0px;">
                        <p style="margin: 0px; padding: 0px; font-size: 13px;">
                            Bonjour {self.client_id.name or "Client"},
                            <br/><br/>
                            Un nouveau contrat de service informatique a été créé pour vous et est en attente de votre approbation.
                            <br/><br/>
                            <strong>Référence:</strong> {self.reference or "N/A"}<br/>
                            <strong>Nom:</strong> {self.name or "N/A"}<br/>
                            <strong>Date de début:</strong> {self.date_start or "N/A"}<br/>
                            <strong>Date de fin:</strong> {self.date_end or "N/A"}<br/>
                            <strong>Montant:</strong> {self.price or 0.0} {self.currency_id.name or "EUR"}<br/>
                        </p>
                    </div>
                ''',
                subject=f'Contrat {self.name} - Demande d\'approbation',
                partner_ids=partner_ids,
                email_layout_xmlid='mail.mail_notification_light',
            )
            
            # Notification dans l'interface Odoo
            return {
                'type': 'ir.actions.client',
                'tag': 'display_notification',
                'params': {
                    'title': _('Erreur d\'envoi d\'email'),
                    'message': _('Une erreur s\'est produite lors de l\'envoi de l\'email. Voir les logs pour plus de détails.'),
                    'sticky': True,
                    'type': 'danger',
                }
            }
        
        return True
        
        

    def read(self, fields=None, load='_classic_read'):
        contracts_data = []
        
        # Traiter chaque enregistrement individuellement 
        for record in self:
            record_data = {'id': record.id}
            
            if fields:
                for field in fields:
                    try:
                        if field == 'client_id':
                            if record.client_id and self.env['it.client'].browse(record.client_id.id).exists():
                                record_data[field] = (record.client_id.id, record.client_id.display_name or f"Client #{record.client_id.id}")
                            else:
                                record_data[field] = False
                        elif field == 'type_id':
                            if record.type_id and self.env['it.contract.type'].browse(record.type_id.id).exists():
                                record_data[field] = (record.type_id.id, record.type_id.display_name or f"Type #{record.type_id.id}")
                            else:
                                record_data[field] = False
                        elif field == 'state':
                            # État est un champ calculé, donc on retourne sa valeur directement
                            record_data[field] = record.state
                        elif hasattr(record, field):
                            record_data[field] = getattr(record, field)
                        else:
                            record_data[field] = False
                    except Exception as e:
                        _logger.error(f"Erreur lors de la lecture du champ {field} pour le contrat {record.id}: {e}")
                        record_data[field] = False
            
            contracts_data.append(record_data)
        
        return contracts_data
        
    
    @api.constrains('client_id', 'type_id')
    def _check_required_valid_references(self):
        for record in self:
            if record.client_id and not self.env['it.client'].browse(record.client_id.id).exists():
                raise ValidationError(_('Le client sélectionné n\'existe pas.'))
            if record.type_id and not self.env['it.contract.type'].browse(record.type_id.id).exists():
                raise ValidationError(_('Le type de contrat sélectionné n\'existe pas.'))
    
    
    def name_get(self):
        try:
            return super(ITContract, self).name_get()
        except Exception as e:
            _logger.error(f"Erreur lors de name_get: {e}")
            result = []
            for record in self:
                try:
                    name = record.name or f"Contrat #{record.id}"
                    result.append((record.id, name))
                except:
                    result.append((record.id, f"Contrat #{record.id}"))
            return result
    
    
    def web_read(self, specification=None):
        """
        Override complet de web_read pour contourner les erreurs de KeyError avec les relations many2one
        """
        try:
            return super(ITContract, self).web_read(specification)
        except Exception as e:
            _logger.error(f"Erreur lors de web_read: {e}")
            
            # S'assurer que l'on retourne toujours une liste, même pour un seul enregistrement
            result = []
            for record in self:
                try:
                    # Créer un résultat minimal mais suffisant pour chaque enregistrement
                    record_data = {
                        'id': record.id,
                        'display_name': record.name or f"Contrat #{record.id}"
                    }
                    
                    # Ajouter les champs demandés avec gestion d'erreur
                    if specification:
                        for field_name in specification:
                            try:
                                # Obtenir les informations sur le champ
                                field_info = self._fields.get(field_name)
                                
                                if field_name == 'client_id':
                                    if record.client_id and self.env['it.client'].browse(record.client_id.id).exists():
                                        record_data[field_name] = {
                                            'id': record.client_id.id,
                                            'display_name': record.client_id.display_name or f"Client #{record.client_id.id}"
                                        }
                                    else:
                                        record_data[field_name] = False
                                elif field_name == 'type_id':
                                    if record.type_id and self.env['it.contract.type'].browse(record.type_id.id).exists():
                                        record_data[field_name] = {
                                            'id': record.type_id.id,
                                            'display_name': record.type_id.display_name or f"Type #{record.type_id.id}"
                                        }
                                    else:
                                        record_data[field_name] = False
                                elif field_info and field_info.type == 'many2one':
                                    # Gérer d'autres champs many2one
                                    value = getattr(record, field_name, False)
                                    if value:
                                        record_data[field_name] = {
                                            'id': value.id,
                                            'display_name': value.display_name or f"{field_name.capitalize()} #{value.id}"
                                        }
                                    else:
                                        record_data[field_name] = False
                                elif field_info and field_info.type in ['one2many', 'many2many']:
                                    # Gérer les champs o2m et m2m
                                    values = getattr(record, field_name, False)
                                    if values:
                                        record_data[field_name] = [{'id': v.id, 'display_name': v.display_name or f"Record #{v.id}"} for v in values]
                                    else:
                                        record_data[field_name] = []
                                else:
                                    # Champs simples
                                    record_data[field_name] = getattr(record, field_name, False)
                            except Exception as err:
                                _logger.error(f"Erreur lors de la récupération du champ {field_name}: {err}")
                                # Pour les champs o2m et m2m, on renvoie une liste vide
                                if field_name in ['equipment_ids', 'software_ids', 'invoice_ids']:
                                    record_data[field_name] = []
                                else:
                                    record_data[field_name] = False
                    
                    result.append(record_data)
                except Exception as record_err:
                    _logger.error(f"Erreur complète lors du traitement de l'enregistrement {record.id}: {record_err}")
                    # Ajouter un enregistrement minimal en cas d'erreur
                    result.append({'id': record.id, 'display_name': f"Contrat #{record.id}"})
                    
            return result
        
    
    @api.model
    def _init_column(self, column_name):
        # Méthode appelée lors de l'initialisation des colonnes
        res = super(ITContract, self)._init_column(column_name)
        
        # Si la colonne initialisée est client_id ou type_id, vérifier son intégrité
        if column_name in ['client_id', 'type_id']:
            self._check_relational_integrity()
        
        return res

    @api.model
    def _check_relational_integrity(self):
        # Vérifier que toutes les références sont valides
        contracts = self.search([])
        for contract in contracts:
            try:
                # Vérifier client_id
                if contract.client_id and not self.env['it.client'].browse(contract.client_id.id).exists():
                    contract.write({'client_id': False})
                    
                # Vérifier type_id
                if contract.type_id and not self.env['it.contract.type'].browse(contract.type_id.id).exists():
                    contract.write({'type_id': False})
            except:
                pass
    
    
    @api.model
    def repair_broken_references(self):
        # Rechercher tous les contrats
        contracts = self.search([])
        fixed_count = 0
        
        for contract in contracts:
            try:
                # Vérifier les références client
                if contract.client_id and not self.env['it.client'].browse(contract.client_id.id).exists():
                    _logger.warning(f"Réparation du contrat {contract.id}: suppression de la référence client invalide {contract.client_id}")
                    contract.write({'client_id': False})
                    fixed_count += 1
                    
                # Vérifier les références type
                if contract.type_id and not self.env['it.contract.type'].browse(contract.type_id.id).exists():
                    _logger.warning(f"Réparation du contrat {contract.id}: suppression de la référence type invalide {contract.type_id}")
                    contract.write({'type_id': False})
                    fixed_count += 1
                    
                # Vérifier les autres références importantes
                if contract.subscription_id and not self.env['sale.subscription'].browse(contract.subscription_id.id).exists():
                    contract.write({'subscription_id': False})
                    fixed_count += 1
                    
            except Exception as e:
                _logger.error(f"Erreur lors de la vérification du contrat {contract.id}: {e}")
        
        return {
            'type': 'ir.actions.client',
            'tag': 'display_notification',
            'params': {
                'title': 'Réparation des contrats',
                'message': f'{fixed_count} contrats ont été réparés',
                'type': 'success',
            }
        }
        
    
    def action_set_active(self):
        self.write({'state': 'active'})
    
    def action_set_to_renew(self):
        self.write({'state': 'to_renew'})
    
    def action_set_cancelled(self):
        self.write({'state': 'cancelled'})
    
    def action_view_equipment(self):
        self.ensure_one()
        return {
            'name': _('Équipements'),
            'view_mode': 'tree,form',
            'res_model': 'it.equipment',
            'domain': [('id', 'in', self.equipment_ids.ids)],
            'type': 'ir.actions.act_window',
        }
    
    def action_view_software(self):
        self.ensure_one()
        return {
            'name': _('Logiciels'),
            'view_mode': 'tree,form',
            'res_model': 'it.software',
            'domain': [('id', 'in', self.software_ids.ids)],
            'type': 'ir.actions.act_window',
        }
    
    def action_view_invoices(self):
        self.ensure_one()
        return {
            'name': _('Factures'),
            'view_mode': 'tree,form',
            'res_model': 'account.move',
            'domain': [('id', 'in', self.invoice_ids.ids)],
            'type': 'ir.actions.act_window',
        }
    
    
    def create_subscription(self):
        """Créer un abonnement Odoo pour la facturation récurrente"""
        self.ensure_one()
        
        # Vérifier si le module est installé
        if not self.env['ir.module.module'].search([('name', '=', 'sale_subscription'), ('state', '=', 'installed')]):
            raise UserError(_("Le module Enterprise 'Abonnements' n'est pas installé."))
        
        if self.subscription_id:
            raise UserError(_('Un abonnement existe déjà pour ce contrat'))
        
        # Vérifier si le client a un partenaire associé
        if not (self.client_id and self.client_id.partner_id):
            raise UserError(_('Le client doit avoir un partenaire associé pour créer un abonnement'))
        
        # Créer un devis d'abonnement
        order_vals = {
            'partner_id': self.client_id.partner_id.id,
            'date_order': fields.Datetime.now(),
            'is_subscription': True,
            'subscription_state': '1_draft',  # Brouillon d'abonnement
            'origin': self.reference or self.name,
            'start_date': self.date_start,
            'end_date': self.date_end,
        }
        
        # Chercher un plan d'abonnement
        plan = self.env['sale.subscription.plan'].search([], limit=1)
        if not plan:
            raise UserError(_("Aucun plan d'abonnement n'a été trouvé. Veuillez en créer un d'abord."))
        
        order_vals['plan_id'] = plan.id
        
        # Créer la commande
        order = self.env['sale.order'].create(order_vals)
        
        # Créer une ligne pour le service récurrent
        product = self._get_subscription_product()
        line_vals = {
            'order_id': order.id,
            'product_id': product.id,
            'name': self.name,
            'product_uom_qty': 1.0,
            'price_unit': self.recurring_amount,
        }
        
        # Vérifier si le champ recurring_invoice existe sur sale.order.line
        order_line_fields = self.env['sale.order.line']._fields
        if 'recurring_invoice' in order_line_fields:
            line_vals['recurring_invoice'] = True
        
        self.env['sale.order.line'].create(line_vals)
        
        # Lier l'abonnement au contrat
        self.write({'subscription_id': order.id})
        
        return {
            'name': _('Abonnement'),
            'view_mode': 'form',
            'res_model': 'sale.order',
            'res_id': order.id,
            'type': 'ir.actions.act_window',
        }


    def _get_subscription_product(self):
        """Obtenir ou créer un produit pour l'abonnement"""
        product = self.env['product.product'].search([
            ('name', '=', 'Service d\'abonnement IT'),
            ('type', '=', 'service'),
            ('recurring_invoice', '=', True)
        ], limit=1)
        
        if not product:
            # Vérifier si le champ recurring_invoice existe sur product.template
            product_fields = self.env['product.template']._fields
            recurring_invoice_exists = 'recurring_invoice' in product_fields
            
            vals = {
                'name': 'Service d\'abonnement IT',
                'type': 'service',
                'invoice_policy': 'order',
                'uom_id': self.env.ref('uom.product_uom_unit').id,
            }
            
            # Ajouter le champ recurring_invoice seulement s'il existe
            if recurring_invoice_exists:
                vals['recurring_invoice'] = True
                
            product = self.env['product.product'].create(vals)
        
        return product


class AccountMove(models.Model):
    _inherit = 'account.move'
    
    contract_id = fields.Many2one('it.contract', string='Contrat IT associé')