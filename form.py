#!/usr/bin/env python
# -*- coding:utf-8 -*-

from tank.validator.validator import Validator 

class Form:

    __attrs__ = {}
    __rules = []
        
    def __init__(self, **kvargs):
        self.locale_translate = None
        self.scenario = None
        self._errors = {}

        for k, v in self.__attrs__.iteritems():

            if kvargs and kvargs.has_key(k):
                value = kvargs[k]

            elif isinstance(v, tuple) and len(v) >= 2:
                value = v[1]

            else:
                value = ''

            setattr(self, k, value)

    @classmethod
    def init_with_handler(cls, handler):
        obj = cls()
        obj.web_handler = handler

        locale = handler.get_user_locale()
        if locale:
            obj.locale_translate = locale.translate

        for k, v in obj.__attrs__.iteritems():
            value = handler.get_argument(k, '')
            setattr(obj, k, value)

        return obj

    def get_attribute_label(self, attribute):
        value = self.__attrs__.get(attribute)

        if isinstance(value, tuple):
            return value[0]

        elif isinstance(value, (str, unicode)):
            return value

        else:
            return attribute

    def create_validators(self):
        if not hasattr(self, '__rules__'): return

        validators = []

        for rule in self.__rules__:
            if rule[0] and rule[1]:

                if len(rule) >= 3:
                    params = rule[2]
                else:
                    params = {}

                validator = Validator.create_validator(rule[1], self, rule[0], params)
                validators.append(validator)

        return validators

    def get_validators(self, attribute = None):
        if not hasattr(self, '_validators') or not self._validators:
            self._validators = self.create_validators()

        validators = []
        scenario = self.scenario

        for validator in self._validators:
            if validator.apply_to(scenario):
                if not attribute or attribute in validator.atributes:
                    validators.append(validator)

        return validators

    def validate(self, attributes = None, clear_errors = True):
        if clear_errors:
            self.clear_errors()

        if self.before_validate():
            for validator in self.get_validators():
                validator.validate(self, attributes)

            self.after_validate()

            return not self.has_errors()

        else:
            return False

    def before_validate(self):
        return True

    def after_validate(self):
        pass

    def has_errors(self, attribute=None):
        if not attribute:
            return True if self._errors else False
        else:
            return self._errors.has_key(attribute) and self._errors[attribute]

    def get_errors(self, attribute=None):
        if not attribute:
            return self._errors
        else:
            return self._errors[attribute] if self._errors.has_key(attribute) else []

    def get_error(self, attribute):
        return self._errors[attribute] if self._errors.has_key(attribute) else None

    def add_error(self, attribute, error):
        if not self._errors.has_key(attribute) or not self._errors[attribute]:
            self._errors[attribute] = []

        self._errors[attribute].append(error)
            
    def add_errors(self, errors):
        for attribute, error in errors:
            if isinstance(error, list):
                for e in error:
                    self.add_error(attribute, e)
            else:
                self.add_error(attribute, error)

    def clear_errors(self, attribute=None):
        if not attribute:
            self._errors = {}
        else:
            if self._errors.has_key(attribute):
                del self._errors[attribute]


if __name__ == "__main__":

    from tornado import locale

    class LoginForm(Form):
        __attrs__ = dict(
            name = ("Name", ),
            email = None,
            passwd = None,
            confirm_passwd = None
        )

        __rules__ = [
            ('name, email, passwd', 'required'),
            ('name', 'string', dict( string_min = 6, string_max = 12 )),
            ('name', 'regular', dict( pattern = r"^[a-zA-Z][a-zA-Z0-9]+$", message = "Name has wrong format." )),
            ('email', 'email'),
            ('confirm_passwd', 'confirm_passwd_validate')
        ]

        def confirm_passwd_validate(self, attribute):
            _ = form.locale_translate

            if self.passwd != self.confirm_passwd:
                self.add_error(attribute, _("confirm passwd not correct."))

    form = LoginForm(
        name = "yinwmfjsdlkfjsdlajlkjsdlkfjdsklfkdjsjfldslkf",
        email = "lovekona@gmail.com",
        passwd = "123",
        confirm_passwd = "123"
    )

    form.locale_translate = locale.get('en_US').translate

    print form.validate()
    print form.get_errors()
    

