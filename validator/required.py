#!/usr/bin/env python
# -*- coding:utf-8 -*-

from .validator import Validator

class RequiredValidator(Validator):

    '''
    @var mixed the desired value that the attribute must have.
    If this is null, the validator will validate that the specified attribute
    does not have null or empty value.
    If this is set as a value that is not null, the validator will validate
    that the attribute has a value that is the same as this property value.
    Defaults to None.
    '''
    required_value = None

    '''
    @var boolean whether the value should be trimmed with python str.strip() method when comparing strings.
    When set to False, the attribute value is not considered empty when it contains spaces.
    Defaults to True, meaning the value will be trimmed.
    '''
    trim = True

    def validate_attribute(self, form, attribute):
        _ = form.locale_translate

        value = getattr(form, attribute)

        if self.required_value:
            if value != self.required_value:
                if self.message:
                    message = self.message
                else:
                    message = _("{0} must be {1}.").format(_(attribute), self.required_value)

                self.add_error(form, attribute, message)
        elif self.is_emtpy(value, self.trim):
            if self.message:
                message = self.message
            else:
                message = _("{0} cannot be blank.").format(_(attribute))

            self.add_error(form, attribute, message)
