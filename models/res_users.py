# -*- coding: utf-8 -*-

from odoo import models, fields, api
from collections import defaultdict
import hashlib
from odoo.addons.base.res import res_users
res_users.USER_PRIVATE_FIELDS.append('pin_crypt')

def name_boolean_group(id):
    return 'in_group_' + str(id)


def name_selection_groups(ids):
    return 'sel_groups_' + '_'.join(map(str, ids))


class ResUsers(models.Model):
    _inherit = 'res.users'

    def custom_has_group(self, group_xml_id):
        self._cr.execute("""SELECT 1 FROM res_groups_users_rel WHERE uid=%s AND gid IN
                                            (SELECT res_id FROM ir_model_data WHERE module=%s AND name=%s)""",
                         (self.id, 'microcredit_portal', group_xml_id))

        return bool(self._cr.fetchone())

    def _compute_pin(self):
        self.env.cr.execute('SELECT id, pin FROM res_users WHERE id IN %s', [tuple(self.ids)])
        pin_dict = dict(self.env.cr.fetchall())
        for user in self:
            user.pin = pin_dict[user.id]

    def _inverse_pin(self):
        for user in self:
            user._set_pin(user.pin)
            self.invalidate_cache()

    def _set_pin(self, pin):
        self.ensure_one()
        """ Encrypts then stores the provided plaintext pin for the user
        ``self``
        """
        hash_object = hashlib.sha256(pin)
        encrypted = hash_object.hexdigest()
        self._set_encrypted_pin(encrypted)

    def _set_encrypted_pin(self, encrypted):
        """ Store the provided encrypted pin to the database, and clears
        any plaintext pin
        """
        self.env.cr.execute(
            "UPDATE res_users SET pin='', pin_crypt=%s WHERE id=%s",
            (encrypted, self.id))

    msisdn = fields.Char('Mobile phone')
    pin = fields.Char(compute='_compute_pin', inverse='_inverse_pin', invisible=True, store=True)
    pin_crypt = fields.Char(string='Encrypted PIN', invisible=True, copy=False)
    user_device_ids = fields.Many2many('parking.user.device')

    # @api.onchange('company_id')
    # def on_change_company_id(self):
    #     self.parent_id = self.company_id.partner_id
    #     if self.company_id not in self.company_ids:
    #         for c in self.company_ids:
    #             self.company_ids -= c
    #
    #         self.company_ids += self.company_id


class GroupsView(models.Model):
    _inherit = 'res.groups'

    @api.model
    def get_groups_by_application(self):
        """ Return all groups classified by application (module category), as a list::

                [(app, kind, groups), ...],

            where ``app`` and ``groups`` are recordsets, and ``kind`` is either
            ``'boolean'`` or ``'selection'``. Applications are given in sequence
            order.  If ``kind`` is ``'selection'``, ``groups`` are given in
            reverse implication order.
        """

        def linearize(app, gs):
            # determine sequence order: a group appears after its implied groups
            order = {g: len(g.trans_implied_ids & gs) for g in gs}
            # check whether order is total, i.e., sequence orders are distinct
            if len(set(order.itervalues())) == len(gs):
                return (app, 'selection', gs.sorted(key=order.get))
            else:
                return (app, 'boolean', gs)

        # classify all groups by application
        by_app, others = defaultdict(self.browse), self.browse()
        for g in self.get_application_groups([('hide_in_access_rights', '=', False)]):
            if g.category_id:
                by_app[g.category_id] += g
            else:
                others += g
        # build the result
        res = []
        for app, gs in sorted(by_app.iteritems(), key=lambda (a, _): a.sequence or 0):
            res.append(linearize(app, gs))
        if others:
            res.append((self.env['ir.module.category'], 'boolean', others))
        return res

    hide_in_access_rights = fields.Boolean('Hide in access rights', default=False)
    alias = fields.Char('Alias')


