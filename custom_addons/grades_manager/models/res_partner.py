from odoo import models, fields


class ResPartner(models.Model):
    # Se utiliza para extender, modificar o agregar funcionalidad del modelo estandar
    _inherit = 'res.partner'
    #_order = 'email' (Ordena por email)
    #_rec_name = '' (nombre para niveles de menú)

    is_teacher = fields.Boolean(string='Is Teacher')
    is_freelance = fields.Boolean(string='Is Freelance')
    is_student   = fields.Boolean(string='Is Student')