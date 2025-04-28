# -*- coding: utf-8 -*-

# from odoo import models, fields, api


# class it_park_management(models.Model):
#     _name = 'it_park_management.it_park_management'
#     _description = 'it_park_management.it_park_management'

#     name = fields.Char()
#     value = fields.Integer()
#     value2 = fields.Float(compute="_value_pc", store=True)
#     description = fields.Text()
#
#     @api.depends('value')
#     def _value_pc(self):
#         for record in self:
#             record.value2 = float(record.value) / 100

