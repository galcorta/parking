# -*- coding: utf-8 -*-
from odoo import models, fields, api
from odoo.tools import DEFAULT_SERVER_DATE_FORMAT as DF
from datetime import date, datetime

import geojson

from odoo import api, fields
from odoo.addons.base_geoengine import geo_model
from odoo.addons.base_geoengine import fields as geo_fields


class TicketMachine(models.Model):
    _name = 'ticket.machine'

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
    _name = 'price.schedule'

    name = fields.Char('Name', required=True)
    description = fields.Char('Description')
    active = fields.Boolean('Active', required=True, default=True)
    available = fields.Boolean('Available', required=True, default=True)
    price_schedule_details = fields.One2many('price.schedule.detail', 'price_schedule')


class PriceScheduleDetail(models.Model):
    _name = 'price.schedule.detail'

    def _inverse_start(self):
        for rec in self:
            str_time = '{0:02.0f}:{1:02.0f}'.format(*divmod(rec.start_time_float * 60, 60))
            st_str = '2017-01-01 ' + str_time
            rec.env.cr.execute(
                "UPDATE price_schedule_detail SET start_time=%s, start_time_float=%s WHERE id=%s",
                (st_str, rec.start_time_float, rec.id))
            rec.invalidate_cache()

    def _inverse_end(self):
        for rec in self:
            str_time = '{0:02.0f}:{1:02.0f}'.format(*divmod(rec.end_time_float * 60, 60))
            st_str = '2017-01-01 ' + str_time
            rec.env.cr.execute(
                "UPDATE price_schedule_detail SET end_time=%s, end_time_float=%s WHERE id=%s",
                (st_str, rec.end_time_float, rec.id))
            rec.invalidate_cache()

    price_schedule = fields.Many2one('price.schedule', string="Price Schedule", ondelete='restrict')
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
    price_hour_ids = fields.One2many('price.hour', 'price_schedule_detail')


class PriceHour(models.Model):
    _name = 'price.hour'
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
    price_schedule_detail = fields.Many2one('price.schedule.detail',
                                            string="Price Schedule Detail", ondelete='restrict')
    minutes_convertion = fields.Char('Minutes convertion', compute='_compute_minutes', required=True, store=True)
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


class Country(models.Model):
    _name = 'country'

    name = fields.Char('Name', required=True)


class Department(models.Model):
    _name = 'department'

    name = fields.Char('Name', required=True)
    country = fields.Many2one('country', string="Country", ondelete='restrict', required=True)


class City(models.Model):
    _name = 'city'

    name = fields.Char('Name', required=True)
    department = fields.Many2one('department', string="Department", ondelete='restrict', required=True)


class District(models.Model):
    _name = 'district'

    name = fields.Char('Name', required=True)
    city = fields.Many2one('city', string="City", ondelete='restrict')


class Zone(models.Model):
    _name = 'zone'

    name = fields.Char('Name', required=True)
    district = fields.Many2one('district', string="District", ondelete='restrict', required=True)
    price_schedule = fields.Many2one('price.schedule', string="Price Schedule", ondelete='restrict')
    lot = fields.Char('Lot')
    floor_level = fields.Char('Floor level')
    reference = fields.Char('Reference')
    active = fields.Boolean('Active', required=True, default=True)


class Street(models.Model):
    _name = 'street'

    code = fields.Char('Code', unique=True, required=True)
    name = fields.Char('Name', required=True)
    start_numeration = fields.Char('Start numeration')
    end_numeration = fields.Char('End numeration')


class Parking(geo_model.GeoModel):
    _name = 'parking'

    @api.depends('street', 'parking_number')
    def _get_parking_name(self):
        self.parking_name = self.street.code + str(self.parking_number).zfill(3)

    parking_name = fields.Char('Parking name', store=True, compute='_get_parking_name')
    parking_number = fields.Integer('Parking number', unique=True, required=True)
    parking_type = fields.Selection([
        ('STANDARD', 'STANDARD'),
        ('PREFERENCE', 'PREFERENCE'),
        ('VIP', 'VIP'),
    ], 'Parking type', required=True, default='STANDARD')
    zone = fields.Many2one('zone', string="Zone", ondelete='restrict', required=True)
    street = fields.Many2one('street', string="Street", ondelete='restrict', required=True)
    next_street = fields.Many2one('street', string="Next street", ondelete='restrict', required=True)
    previous_street = fields.Many2one('street', string="Previous street", ondelete='restrict', required=True)
    latitude = fields.Float('Latitude', digits=(14, 11))
    longitude = fields.Float('Longitude', digits=(14, 11))
    free_at = fields.Datetime('Free at')
    description = fields.Char('Description')
    # available = fields.Boolean('Available', default=True, required=True)
    active = fields.Boolean('Active', required=True, default=True)
    name = fields.Char(string='Parking', related='parking_name')
    status = fields.Char('Status', compute='_get_status')
    last_ticket_start_time = fields.Char('Start time', compute='_get_last_ticket_start_time')
    last_ticket_end_time = fields.Char('End time', compute='_get_last_ticket_end_time')
    today_tickets_count = fields.Integer('Today tickets', compute='_get_today_tickets_count')
    last_ticket_amount = fields.Float('Price', digits=(8, 2), compute='_get_last_ticket_amount')
    today_tickets_amount = fields.Float('Price', digits=(8, 2), compute='_get_today_tickets_amount')

    coordinate = geo_fields.GeoPoint('Coordinate')

    @api.one
    def _get_status(self):
        dt_now = datetime.utcnow()
        #openerp.datetime.fields.now()
        if not self.free_at:
            self.status = 'Liberado'
        elif dt_now >= datetime.strptime(self.free_at, "%Y-%m-%d %H:%M:%S"):
            self.status = 'Liberado'
        else:
            self.status = 'Ocupado'

    @api.one
    def _get_last_ticket_start_time(self):
        if self.status == 'Ocupado':
            last_ticket = self.env['parking.ticket'].search([('parking', '=', self.id)], order="id desc", limit=1)
            if len(last_ticket) > 0:
                start_dt = datetime.strptime(last_ticket[0].start_time, "%Y-%m-%d %H:%M:%S")
                self.last_ticket_start_time = datetime.strftime(start_dt, "%H:%M")

    @api.one
    def _get_last_ticket_end_time(self):
        if self.status == 'Ocupado':
            last_ticket = self.env['parking.ticket'].search([('parking', '=', self.id)], order="id desc", limit=1)
            if len(last_ticket) > 0:
                end_dt = datetime.strptime(last_ticket[0].end_time, "%Y-%m-%d %H:%M:%S")
                self.last_ticket_end_time = datetime.strftime(end_dt, "%H:%M")

    @api.one
    def _get_today_tickets_count(self):
        today = date.today().strftime(DF)
        self.today_tickets_count = self.env['parking.ticket'] \
            .search_count([('parking', '=', self.id), ('create_date', '>=', today)])

    @api.one
    def _get_last_ticket_amount(self):
        last_ticket = self.env['parking.ticket'].search([('parking', '=', self.id)], order="id desc", limit=1)
        if len(last_ticket) > 0:
            self.last_ticket_amount = last_ticket[0].price_hour.price

    @api.one
    def _get_today_tickets_amount(self):
        today = date.today().strftime(DF)
        today_tickets = self.env['parking.ticket']\
            .search([('parking', '=', self.id), ('create_date', '>=', today)])
        for ticket in today_tickets:
            self.today_tickets_amount += ticket.price_hour.price

    _sql_constraints = [
        ('number_parking_uniq', 'unique(street, parking_number)', 'The number of the parking must be unique per street!'),
    ]


class Profile(models.Model):
    _name = 'profile'

    name = fields.Char('Name', unique=True, required=True)
    profile_alias = fields.Char('Alias', unique=True)
    description = fields.Char('Description')
    available = fields.Boolean('Available', default=True, required=True)
    active = fields.Boolean('Active', required=True, default=True)


class Person(models.Model):
    _name = "person"

    name = fields.Char('Name', required=True)
    last_name = fields.Char('Last name', required=True)
    date_birth = fields.Date('Date birth')
    document_number = fields.Char('Document number', required=True)
    document_type = fields.Char('Document type', required=True)
    address = fields.Char('Address')
    email_principal = fields.Char('Email principal')
    email_secondary = fields.Char('Email secondary')
    photo = fields.Char('Photo')
    active = fields.Boolean('Active', required=True, default=True)


class SysUser(models.Model):
    _name = 'sys.user'

    person = fields.Many2one('person', string="Person", ondelete='restrict')
    profile = fields.Many2one('profile', string="Profile", ondelete='restrict', required=True)
    username = fields.Char('User Name', unique=True, required=True)
    email = fields.Char('Email')
    msisdn = fields.Char('MSISDN', required=True)
    pin = fields.Char('PIN', required=True)
    password = fields.Char('Password', required=True)
    active = fields.Boolean('Active', required=True, default=True)


class PaymentMethod(models.Model):
    _name = 'payment.method'

    name = fields.Char('Name', unique=True, required=True)
    active = fields.Boolean('Active', required=True, default=True)


class Vehicle(models.Model):
    _name = 'vehicle'

    brand = fields.Char('Brand')
    model = fields.Char('Model')
    type = fields.Char('Type')
    plate = fields.Char('Plate')
    image_url = fields.Char('Image URL')
    description = fields.Char('Description')
    active = fields.Boolean('Active', required=True, default=True)


class VehicleCustomer(models.Model):
    _name = 'vehicle.customer'

    customer = fields.Many2one('sys.user', string="Customer", ondelete='restrict', required=True)
    vehicle = fields.Many2one('vehicle', string="Vehicle", ondelete='restrict', required=True)
    active = fields.Boolean('Active', required=True, default=True)

    _sql_constraints = [
        ('customer_vehicle_unique', 'UNIQUE (customer, vehicle)', 'Customer and vehicle must be unique!')
    ]


class ParkingTicket(models.Model):
    _name = 'parking.ticket'

    ticket_machine = fields.Many2one('ticket.machine', string="Ticket machine", ondelete='restrict', required=True)
    price_hour = fields.Many2one('price.hour', string="Price hour", ondelete='restrict', required=True)
    parking = fields.Many2one('parking', string="Parking", ondelete='restrict', required=True)
    parking_manager = fields.Many2one('sys.user', string="Customer", ondelete='restrict')
    payment_method = fields.Many2one('payment.method', string="Payment method", ondelete='restrict')
    vehicle_customer = fields.Many2one('vehicle.customer', string="Vehicle Customer", ondelete='restrict')
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


class ParkingTicketReleased(models.Model):
    _name = 'parking.ticket.released'

    parking_ticket = fields.Many2one('parking.ticket')
    sys_user = fields.Many2one('sys.user')


class SysSetting(models.Model):
    _name = 'sys.setting'

    sys_key = fields.Char('Sys key', required=True)
    sys_value = fields.Char('Sys value')
    description = fields.Char('Description')
    active = fields.Boolean('Active')
