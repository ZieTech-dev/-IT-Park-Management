from odoo import http, _
from odoo.http import request
from odoo.addons.portal.controllers.portal import CustomerPortal, pager as portal_pager
from odoo.osv.expression import OR
from odoo.exceptions import AccessError

class ITPortal(CustomerPortal):

    def _prepare_home_portal_values(self, counters):
        """Ajoute les compteurs pour les contrats IT au tableau de bord du portail"""
        values = super()._prepare_home_portal_values(counters)
        
        if 'contract_count' in counters:
            partner = request.env.user.partner_id
            
            # Rechercher par partenaire commercial (pour inclure les contacts liés)
            partners = partner.commercial_partner_id | partner.commercial_partner_id.child_ids
            
            # Compter les contrats où le client est lié au partenaire
            contract_count = request.env['it.contract'].search_count([
                ('client_id.partner_id', 'in', partners.ids)
            ])
            
            values['contract_count'] = contract_count
            
        return values
    
    # Liste des contrats
    @http.route(['/my/it/contracts', '/my/it/contracts/page/<int:page>'], type='http', auth="user", website=True)
    def portal_my_contracts(self, page=1, date_begin=None, date_end=None, sortby=None, filterby=None, search=None, search_in='name', **kw):
        """Liste des contrats IT du client"""
        values = self._prepare_portal_layout_values()
        partner = request.env.user.partner_id
        ITContract = request.env['it.contract']
        
        # Domaine de recherche: contrats liés au partenaire commercial ou à ses contacts
        partners = partner.commercial_partner_id | partner.commercial_partner_id.child_ids
        domain = [('client_id.partner_id', 'in', partners.ids)]
            
        # Filtres et recherche
        searchbar_sortings = {
            'date_start': {'label': _('Date de début'), 'order': 'date_start desc'},
            'name': {'label': _('Nom'), 'order': 'name'},
            'state': {'label': _('État'), 'order': 'state'},
        }
        
        searchbar_filters = {
            'all': {'label': _('Tous'), 'domain': []},
            'active': {'label': _('Actifs'), 'domain': [('state', '=', 'active')]},
            'to_renew': {'label': _('À renouveler'), 'domain': [('state', '=', 'to_renew')]},
            'waiting': {'label': _('En attente'), 'domain': [('state', '=', 'waiting_approval')]},
        }
        
        searchbar_inputs = {
            'name': {'input': 'name', 'label': _('Nom')},
            'reference': {'input': 'reference', 'label': _('Référence')},
            'all': {'input': 'all', 'label': _('Tous')},
        }
        
        # Valeurs par défaut
        if not sortby:
            sortby = 'date_start'
        order = searchbar_sortings[sortby]['order']
        
        if not filterby:
            filterby = 'all'
        domain += searchbar_filters[filterby]['domain']
        
        # Recherche textuelle
        if search and search_in:
            search_domain = []
            if search_in in ('name', 'all'):
                search_domain = OR([search_domain, [('name', 'ilike', search)]])
            if search_in in ('reference', 'all'):
                search_domain = OR([search_domain, [('reference', 'ilike', search)]])
            domain += search_domain
        
        # Compteur et pagination
        contract_count = ITContract.search_count(domain)
        pager = portal_pager(
            url="/my/it/contracts",
            url_args={'date_begin': date_begin, 'date_end': date_end, 'sortby': sortby, 'filterby': filterby, 'search_in': search_in, 'search': search},
            total=contract_count,
            page=page,
            step=self._items_per_page
        )
        
        # Récupération des contrats
        contracts = ITContract.search(domain, order=order, limit=self._items_per_page, offset=pager['offset'])
        
        # Assignation des valeurs pour le template
        values.update({
            'contracts': contracts,
            'page_name': 'contract',
            'pager': pager,
            'default_url': '/my/it/contracts',
            'searchbar_sortings': searchbar_sortings,
            'searchbar_filters': searchbar_filters,
            'searchbar_inputs': searchbar_inputs,
            'sortby': sortby,
            'filterby': filterby,
            'search_in': search_in,
            'search': search,
        })
        
        return request.render("it_park_management.portal_my_contracts", values)
    
    # Détail d'un contrat
    @http.route(['/my/it/contract/<int:contract_id>'], type='http', auth="user", website=True)
    def portal_my_contract_detail(self, contract_id, **kw):
        """Détails d'un contrat IT"""
        try:
            contract_sudo = self._document_check_access('it.contract', contract_id)
        except AccessError:
            return request.redirect('/my')
        
        values = {
            'contract': contract_sudo,
            'page_name': 'contract_detail',
        }
        
        return request.render("it_park_management.portal_contract_detail", values)
    
    # Approbation d'un contrat
    @http.route(['/my/it/contract/approve/<int:contract_id>'], type='http', auth="user", website=True)
    def portal_approve_contract(self, contract_id, **kw):
        """Approuver un contrat via le portail"""
        try:
            contract_sudo = self._document_check_access('it.contract', contract_id)
        except AccessError:
            return request.redirect('/my')
        
        if contract_sudo.state != 'waiting_approval':
            return request.redirect('/my/it/contract/%s' % contract_id)
        
        contract_sudo.action_approve_via_portal()
        
        return request.redirect('/my/it/contract/%s?approved=1' % contract_id)