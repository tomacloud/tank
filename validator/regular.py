#!/usr/bin/env python
# -*- coding:utf-8 -*-

import re
from .validator import Validator

class RegularValidator(Validator):

    '''
    @var str the regular expression to be matched with
    '''
    pattern = None

    '''
    @var bool whether the attribute value can be null or empty. Defaults to
         True, meaning that if the attribute is empty, it is considered valid.
    '''
    allow_empty = True;

    '''
    @var bool whether to invert the validation logic. Defaults to false. If set to true,
    the regular expression defined via `pattern` should NOT match the attribute value.
    '''
    invert = False


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

        if not self.pattern:
            raise ValueError('pattern cannot be null')

        elif not self.invert and not re.search(self.pattern, value) or\
             self.invert and re.search(self.pattern, value):
            if self.message:
                message = _(self.message)
            else:
                message = _("{0} is invalid.").format(_(form.get_attribute_label(attribute)))

            self.add_error(form, attribute, message)
            
    
