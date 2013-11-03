#!/usr/bin/env python
# -*- coding:utf-8 -*-

import re

from .validator import Validator

class EmailValidator(Validator):

    '''
    @var str the regular expression used to validate the attribute value.
    @see http://www.regular-expressions.info/email.html
    '''
    pattern = '^[a-zA-Z0-9!#$%&\'*+\\/=?^_`{|}~-]+(?:\.[a-zA-Z0-9!#$%&\'*+\\/=?^_`{|}~-]+)*@(?:[a-zA-Z0-9](?:[a-zA-Z0-9-]*[a-zA-Z0-9])?\.)+[a-zA-Z0-9](?:[a-zA-Z0-9-]*[a-zA-Z0-9])?$'

    '''
    @var bool whether the attribute value can be null or empty. Defaults to True,
         meaning that if the attribute is empty, it is considered valid.
    '''
    allow_empty = True

    def validate_attribute(self, form, attribute):
        '''
        Validates the attribute of the object.
        If there is any error, the error message is added to the object.
        @param tank.form.Form form the object being validated
        @param string attribute the attribute being validated
        '''

        _ = form.locale_translate
        value = getattr(form, attribute)

        if self.allow_empty and not value:
            return

        if not value or len(value) > 254 or not re.search(self.pattern, value):

            if self.message:
                message = _(self.message)
            else:
                message = _("{0} is not a valid email address.").format(_(form.get_attribute_label(attribute)))

            self.add_error(form, attribute, message)
