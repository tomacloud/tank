#!/usr/bin/env python
# -*- coding:utf-8 -*-

import re

def get_validator_cls(name):
    from .required import RequiredValidator

    cls_map = dict(
        required = RequiredValidator
    )

    if cls_map.has_key(name):
        return cls_map[name]
    else:
        return None


class Validator:

    attributes    = []
    message       = ""
    on            = None
    excepts       = None
    skip_on_error = False

    @classmethod
    def create_validator(cls, name, form, attributes, params):
        """
        Create a validator object.

        @param string name the name or class of the validator
        @param tank.form.Form
        @param string|list attributes list of arrtibutes to be validated.
               this can be either an list of the attribute names or a
               a string of comma-separated attribute names
        @param list params initial values to be applied to the validator
               properties
        @return tank.validator.Validator the validator
        """

        if isinstance(attributes, (str, unicode)):
            attributes = re.split('\s*,\s*', attributes)

        if params.has_key('on'):
            if isinstance(params['on'], list):
                on = params['on']
            else:
                on = re.split('\s*,\s*', params['on'])
        else:
            on = []

        if params.has_key('excepts'):
            if isinstance(params['excepts'], list):
                excepts = params['excepts']
            else:
                excepts = re.split('\s*,\s*', params['excepts'])
        else:
            excepts = []
            

        if hasattr(form, name): # inline validate
            pass
        else:
            params['attributes'] = attributes

            cls = get_validator_cls(name)

            if not cls:
                raise ValueError('%s validate not exists' % name)

            validator = cls()
            for k, v in params.iteritems():
                setattr(validator, k, v)

        validator.on = on
        validator.excepts = excepts

        return validator


    def validate(self, form, attributes=None):
        """
        Validates the specified object.

        @param tank.form.Form form the data object being validated
        @param attributes the list of attributes to be validated. Defaults to None
               meaning every attribute listed in attributes will be validated.
        """

        if isinstance(attributes, list):
            for attr in self.attributes:
                if attr not in attributes:
                    attributes.append(attr)

        else:
            attributes = self.attributes

        for attr in attributes:
            if not self.skip_on_error or not form.has_errors(attr):
                self.validate_attribute(form, attr)

    def validate_attribute(self, form, attribute):
        """
        Validates a single attribute.
        This method should be overridden by child classes.
        @param tank.form.Form form the data object being validated
        @param str attribute the name of the attribute to be validated.
        """
        pass

        
    def add_error(self, form, attribute, message):
        """
        Adds an error about the specified attribute to the active record.
        This is a helper method that performs message selection and internationalization.
        @param tank.form.Form form the data object being validated
        @param string attribute the attribute being validated
        @param string message the error message
        """
        form.add_error(attribute, message)

    def apply_to(self, scenario):
        """
	Returns a value indicating whether the validator applies to the specified scenario.
	A validator applies to a scenario as long as any of the following conditions is met:
	
        1) the validator's "on" property is empty
        2) <li>the validator's "on" property contains the specified scenario
        @param string scenario scenario name
        @return boolean whether the validator applies to the specified scenario.
        """
        if scenario in self.excepts:
            return False

        return not self.on or scenario in self.on


    def is_emtpy(self, value, trim=False):
        return not value or trim and not value.strip()
