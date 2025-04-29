from odoo import http, _
from odoo.http import request
from addons.portal.controllers.portal import CustomerPortal, pager as portal_pager
from odoo.exceptions import AccessError, MissingError
from collections import OrderedDict


class ITPortal(CustomerPortal):

    def _prepare_home_portal_values(self, counters):
        values = super()._prepare_home_portal_values(counters)
        partner = request.env.user.partner_id

        ITContract = request.env['it.contract']
        ITEquipment = request.env['it.equipment']
        
        if 'contract_count' in counters:
            contract_count = ITContract.search_count([
                ('client_id.partner_id', '=', partner.id),
                ('state', 'in', ['draft', 'waiting_approval', 'active', 'to_renew'])
            ])
            values['contract_count'] = contract_count
            
        if 'equipment_count' in counters:
            equipment_count = ITEquipment.search_count([
                ('client_id.partner_id', '=', partner.id)
            ])
            values['equipment_count'] = equipment_count
            
        return values

    # Page d'accueil du portail client IT
    @http.route(['/my/it'], type='http', auth="user", website=True)
    def portal_my_it_home(self, **kw):
        values = self._prepare_portal_layout_values()
        return request.render("it_park_management.portal_my_it_home", values)
    
    # Liste des contrats
    @http.route(['/my/it/contracts', '/my/it/contracts/page/<int:page>'], type='http', auth="user", website=True)
    def portal_my_contracts(self, page=1, date_begin=None, date_end=None, sortby=None, **kw):
        values = self._prepare_portal_layout_values()
        partner = request.env.user.partner_id
        ITContract = request.env['it.contract']
        
        domain = [
            ('client_id.partner_id', '=', partner.id)
        ]
        
        # Pagination
        contract_count = ITContract.search_count(domain)
        pager = portal_pager(
            url="/my/it/contracts",
            url_args={'date_begin': date_begin, 'date_end': date_end, 'sortby': sortby},
            total=contract_count,
            page=page,
            step=self._items_per_page
        )
        
        # Recherche des contrats avec limite de pagination
        contracts = ITContract.search(domain, limit=self._items_per_page, offset=pager['offset'])
        
        values.update({
            'contracts': contracts,
            'page_name': 'contract',
            'pager': pager,
            'default_url': '/my/it/contracts',
        })
        
        return request.render("it_park_management.portal_my_contracts", values)
    
    # Détail d'un contrat
    @http.route(['/my/it/contract/<int:contract_id>'], type='http', auth="user", website=True)
    def portal_my_contract_detail(self, contract_id, **kw):
        try:
            contract_sudo = self._document_check_access('it.contract', contract_id)
        except (AccessError, MissingError):
            return request.redirect('/my')
            
        values = self._prepare_portal_layout_values()
        values.update({
            'contract': contract_sudo,
            'page_name': 'contract',
        })
        
        return request.render("it_park_management.portal_my_contract_detail", values)
    
    # Action d'acceptation du contrat
    @http.route(['/my/it/contract/<int:contract_id>/accept'], type='http', auth="user", website=True)
    def portal_contract_accept(self, contract_id, **kw):
        contract = request.env['it.contract'].browse(contract_id)
        if contract.state == 'waiting_approval':
            contract.sudo().write({'state': 'active'})
            # Envoyer un email de confirmation
            template = request.env.ref('it_park_management.email_template_contract_accepted')
            template.sudo().send_mail(contract.id, force_send=True)
        
        return request.redirect('/my/it/contract/%s' % contract_id)