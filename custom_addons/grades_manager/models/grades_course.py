from odoo import models, fields

class GradesCourse(models.Model):
    _name = 'grades.course'
    _description = 'Grades Course'
    _rec_name = 'nombre'

    def _default_teacher_id(self):
        teacher = self.env['res.partner'].search(
            [('is_teacher', '=', True), ('email', '=', 'mainteacher@gmail.com')], limit=1)
        return teacher.id

    nombre = fields.Char(string='Nombre', required=True)
    student_qty = fields.Integer(string='Student quantity')
    grades_averge = fields.Float(string='Grades averange')
    description = fields.Text(string='Description')
    is_active = fields.Boolean(string='Is active')
    course_start = fields.Date(string='Course Start', default=fields.Date.context_today)
    course_end = fields.Date(string='Course End')
    last_evaluation_date = fields.Datetime(string='Last evaluation date')
    course_image = fields.Binary(string='Course image')
    course_shift = fields.Selection([('day', 'Day'), ('night', 'Night')], string='Course shift')
    teacher_id = fields.Many2one('res.partner', string='Teacher', default=_default_teacher_id)
    evalaution_ids = fields.One2many('grades.evaluation', 'course_id', string='Evaluations')
    student_ids = fields.Many2many('res.partner', 'grades_course_students_rel', string="Student")
    state = fields.Selection([
        ('register', 'Register'),
        ('in_progress', 'In Progress'),
        ('finished', 'Finished')
    ], string='State', default='register')