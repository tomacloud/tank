#!/usr/bin/env python
# -*- coding:utf-8 -*-

from .validator import Validator

class InlineValidator(Validator):

    '''
    @var string the name of the validation method defined in the active record class
    '''
    method = None

    '''
    @var dict additional parameters that are passed to the validation method
    '''
    params = None;

    def validate_attribute(self, form, attribute):
        '''
        Validates the attribute of the object.
        If there is any error, the error message is added to the object.
        @param tank.form.Form form the object being validated
        @param string attribute the attribute being validated
        '''
        getattr(form, self.method)(attribute, **self.params)
    
