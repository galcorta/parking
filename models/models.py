# -*- coding: utf-8 -*-

from odoo import models, fields, api


class TicketMachine(models.Model):
    _name = 'parking.ticket.machine'

    name = fields.Char('Name')
    code = fields.Char('Code', required=True)
    msisdn = fields.Char('MSISDN', required=True)
    status = fields.Selection([
        ('ACTIVE', 'ACTIVE'),
        ('INACTIVE', 'INACTIVE'),
    ], 'Status', required=True, default='ACTIVE')
    latitude = fields.Float('Latitude', digits=(14, 11))
    longitude = fields.Float('Longitude', digits=(14, 11))
    active = fields.Boolean('Active', required=True, default=True)


class PriceSchedule(models.Model):
    _name = 'parking.price.schedule'

    name = fields.Char('Name', required=True)
    description = fields.Char('Description')
    active = fields.Boolean('Active', required=True, default=True)
    price_schedule_detail_ids = fields.One2many('parking.price.schedule.detail', 'price_schedule_id')


class PriceScheduleDetail(models.Model):
    _name = 'parking.price.schedule.detail'

    def _inverse_start(self):
        for rec in self:
            str_time = '{0:02.0f}:{1:02.0f}'.format(*divmod(rec.start_time_float * 60, 60))
            st_str = '2017-01-01 ' + str_time
            rec.env.cr.execute(
                "UPDATE parking_price_schedule_detail SET start_time=%s, start_time_float=%s WHERE id=%s",
                (st_str, rec.start_time_float, rec.id))
            rec.invalidate_cache()

    def _inverse_end(self):
        for rec in self:
            str_time = '{0:02.0f}:{1:02.0f}'.format(*divmod(rec.end_time_float * 60, 60))
            st_str = '2017-01-01 ' + str_time
            rec.env.cr.execute(
                "UPDATE parking_price_schedule_detail SET end_time=%s, end_time_float=%s WHERE id=%s",
                (st_str, rec.end_time_float, rec.id))
            rec.invalidate_cache()

    price_schedule_id = fields.Many2one('parking.price.schedule', string="Price Schedule", ondelete='restrict')
    name = fields.Char('Name', required=True)
    start_time = fields.Datetime('Start time')
    start_time_float = fields.Float('Start time', inverse='_inverse_start', invisible=True, store=True, required=True)
    end_time = fields.Datetime('End time')
    end_time_float = fields.Float('End time', inverse='_inverse_end', invisible=True, store=True, required=True)
    day_of_the_week = fields.Selection([
        ('MONDAY', 'MONDAY'),
        ('TUESDAY', 'TUESDAY'),
        ('WEDNESDAY', 'WEDNESDAY'),
        ('THURSDAY', 'THURSDAY'),
        ('FRIDAY', 'FRIDAY'),
        ('SATURDAY', 'SATURDAY'),
        ('SUNDAY', 'SUNDAY'),
    ], 'Day of the week', required=True)
    status = fields.Selection([
        ('FEE', 'FEE'),
        ('FREE', 'FREE'),
    ], 'Status', required=True, default='FEE')
    description = fields.Char('Description')
    active = fields.Boolean('Active', required=True, default=True)
    price_hour_ids = fields.One2many('parking.price.hour', 'price_schedule_detail_id')


class PriceHour(models.Model):
    _name = 'parking.price.hour'
    _order = 'minutes'

    _dict_hour = {'30': 'Media',
                  '60': 'Una',
                  '90': 'Una y media',
                  '120': 'Dos',
                  '150': 'Dos y media',
                  '180': 'Tres',
                  '210': 'Tres y media',
                  '240': 'Cuatro',
                  '270': 'Cuatro y media',
                  '300': 'Cinco',
                  '330': 'Cinco y media',
                  '360': 'Seis',
                  }

    # @api.depends('minutes_convertion', 'label', 'price')
    # def _compute_name(self):
    #     for record in self:
    #         record.name = str(record.price) + ' ' + record.minutes_convertion + ' ' + record.label

    @api.depends('minutes')
    def _compute_minutes(self):
        for record in self:
            record.minutes_convertion = record._dict_hour[str(record.minutes)]

    #name = fields.Char(compute='_compute_name', string='Name')
    price_schedule_detail_id = fields.Many2one('parking.price.schedule.detail',
                                            string="Price Schedule Detail", ondelete='cascade')
    minutes_convertion = fields.Char('Minutes convertion', compute='_compute_minutes', store=True)
    label = fields.Char('Label', required=True, default='Hs')
    minutes = fields.Selection([
        (30, 'Media hora'),
        (60, 'Una hora'),
        (90, 'Una hora y media'),
        (120, 'Dos horas'),
        (150, 'Dos horas y media'),
        (180, 'Tres horas'),
        (210, 'Tres horas y media'),
        (240, 'Cuatro horas'),
        (270, 'Cuatro horas y media'),
        (300, 'Cinco horas'),
        (330, 'Cinco horas y media'),
        (360, 'Seis horas'),
    ], 'Minutes', required=True, default=30)
    price = fields.Float('Price', digits=(8, 2), required=True)
    active = fields.Boolean('Active', required=True, default=True)


class Zone(models.Model):
    _name = 'parking.zone'

    name = fields.Char('Name', required=True)
    city_id = fields.Many2one('res.country.state.city', string="City", ondelete='restrict', required=True)
    price_schedule_id = fields.Many2one('parking.price.schedule', string="Price Schedule", ondelete='restrict')
    lot = fields.Char('Lot')
    floor_level = fields.Char('Floor level')
    reference = fields.Char('Reference')
    active = fields.Boolean('Active', required=True, default=True)


class Street(models.Model):
    _name = 'parking.street'

    code = fields.Char('Code', unique=True, required=True)
    name = fields.Char('Name', required=True)
    start_numeration = fields.Char('Start numeration')
    end_numeration = fields.Char('End numeration')


class PaymentMethod(models.Model):
    _name = 'parking.payment.method'

    name = fields.Char('Name', unique=True, required=True)
    active = fields.Boolean('Active', required=True, default=True)


class Vehicle(models.Model):
    _name = 'parking.vehicle'

    brand = fields.Char('Brand')
    model = fields.Char('Model')
    vehicle_type = fields.Char('Type')
    plate = fields.Char('Plate')
    image_url = fields.Char('Image URL')
    description = fields.Char('Description')
    active = fields.Boolean('Active', required=True, default=True)


class VehicleCustomer(models.Model):
    _name = 'parking.vehicle.customer'

    partner_id = fields.Many2one('res.partner', string="Customer", ondelete='restrict', required=True)
    vehicle_id = fields.Many2one('parking.vehicle', string="Vehicle", ondelete='restrict', required=True)
    active = fields.Boolean('Active', required=True, default=True)

    _sql_constraints = [
        ('customer_vehicle_unique', 'UNIQUE (partner_id, vehicle_id)', 'Customer and vehicle must be unique!')
    ]


class ParkingTicket(models.Model):
    _name = 'parking.ticket'

    ticket_machine_id = fields.Many2one('parking.ticket.machine', string="Ticket machine", ondelete='restrict', required=True)
    price_hour_id = fields.Many2one('parking.price.hour', string="Price hour", ondelete='restrict', required=True)
    parking_id = fields.Many2one('parking.parking', string="Parking", ondelete='restrict', required=True)
    parking_manager_id = fields.Many2one('res.users', string="Parking manager", ondelete='restrict')
    payment_method_id = fields.Many2one('parking.payment.method', string="Payment method", ondelete='restrict')
    vehicle_customer_id = fields.Many2one('parking.vehicle.customer', string="Vehicle Customer", ondelete='restrict')
    ticket_type = fields.Char('Ticket type', required=True)
    start_time = fields.Datetime('Start time', required=True)
    end_time = fields.Datetime('End time', required=True)
    source = fields.Selection([
        ('SM', 'Auto-Gestionado'),
        ('PM', 'Gestionado por POS'),
    ], 'Source', required=True)
    status = fields.Selection([
        ('PENDING_PRINT', 'Pending print'),
        ('APPROVED', 'Aproved'),
        ('REJECTED', 'Rejected'),
    ], 'Status', required=True)
    description = fields.Char('Description')
    active = fields.Boolean('Active', required=True, default=True)
    start_time_string = fields.Char('Start time', compute='_get_start_time_string')
    end_time_string = fields.Char('End time', compute='_get_end_time_string')

    @api.one
    def _get_start_time_string(self):
        self.start_time_string = self.start_time[11:16]

    @api.one
    def _get_end_time_string(self):
        self.end_time_string = self.end_time[11:16]


class ParkingTicketReleased(models.Model):
    _name = 'parking.ticket.released'

    parking_ticket_id = fields.Many2one('parking.ticket')
    res_user_id = fields.Many2one('res.users')


class SysSetting(models.Model):
    _name = 'sys.setting'

    sys_key = fields.Char('Sys key', required=True)
    sys_value = fields.Char('Sys value')
    description = fields.Char('Description')
    active = fields.Boolean('Active')


class ParkingUserDevice(models.Model):
    _name = 'parking.user.device'

    msisdn = fields.Char('Mobile phone', unique=True)
    imei = fields.Char('IMEI')
    device_type = fields.Selection([
        ('POS_MACHINE', 'POS MACHINE'),
        ('MOBILE_PHONE', 'MOBILE PHONE'),
    ], 'Device type', default='POS_MACHINE')
    released = fields.Boolean('Released', default=True)
    active = fields.Boolean('Active', required=True, default=True)

    _sql_constraints = [
        ('msisdn_uniq', 'unique(msisdn)', 'The phone number must be unique per device!'),
    ]


class ParkingFine(models.Model):
    _name = 'parking.fine'

    res_user_id = fields.Many2one('res.users', string='Police')
    parking_id = fields.Many2one('parking.parking', string='Parking')
    ticket_machine_id = fields.Many2one('parking.ticket.machine', string='Ticket machine')
    status = fields.Selection([
        ('GENERATED', 'GENERATED'),
        ('PRINTED', 'PRINTED'),
    ], 'Status', required=True, default='GENERATED')
    plate = fields.Char('Plate')
    description = fields.Char('Description')
    active = fields.Boolean('Active', required=True, default=True)
