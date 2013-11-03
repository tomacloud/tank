#!/usr/bin/env python
# -*- coding:utf-8 -*-

import re
from .validator import Validator

class StringValidator(Validator):

    '''
    @var int maximum length. Defaults to None, meaning no maximum limit.
    '''
    string_max = None
    
    '''
    @var int minimum length. Defaults to None, meaning no minimum limit.
    '''
    string_min = None
    
    '''
    @var int exact length. Defaults to null, meaning no exact length limit.
    '''
    string_is = None;
    
    '''
    @var str user-defined error message used when the value is too short.
    '''
    too_short = None
    '''
    @var string user-defined error message used when the value is too long.
    '''
    too_long = None
    '''
    @var boolean whether the attribute value can be null or empty. Defaults to true,
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

        if self.allow_empty and self.is_empty(value):
            return

        length = len(value)

        if self.string_min and length < self.string_min:
            if self.too_short:
                message = self.too_short
            else:
                message = _("{0} is too short (minimum is {1} characters).").format(form.get_attribute_label(attribute), self.string_min)

            self.add_error(form, attribute, message)

        elif self.string_max and length > self.string_max:
            if self.too_long:
                message = self.too_long
            else:
                message = _("{0} is too long (maximum is {1} characters).").format(form.get_attribute_label(attribute), self.string_max)

            self.add_error(form, attribute, message)

        elif self.string_is and length != self.string_is:
            if self.message:
                message = self.message
            else:
                message = _("{0} is of the wrong length (should be {1} characters).").format(form.get_attribute_label(attribute), self.string_is)

            self.add_error(form, attribute, message)
