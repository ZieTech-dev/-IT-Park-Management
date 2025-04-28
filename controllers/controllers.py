# -*- coding: utf-8 -*-
# from odoo import http


# class ItParkManagement(http.Controller):
#     @http.route('/it_park_management/it_park_management', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/it_park_management/it_park_management/objects', auth='public')
#     def list(self, **kw):
#         return http.request.render('it_park_management.listing', {
#             'root': '/it_park_management/it_park_management',
#             'objects': http.request.env['it_park_management.it_park_management'].search([]),
#         })

#     @http.route('/it_park_management/it_park_management/objects/<model("it_park_management.it_park_management"):obj>', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('it_park_management.object', {
#             'object': obj
#         })

