class SimpleForm:
    def __init__(self, data=None):
        self.data = data or {}
        self.errors = {}
    
    def validate_on_submit(self):
        return True

class RegisterForm(SimpleForm):
    @property
    def nickname(self):
        return type('obj', (object,), {'data': self.data.get('nickname', '')})
    
    @property 
    def password(self):
        return type('obj', (object,), {'data': self.data.get('password', '')})
    
    @property
    def confirm_password(self):
        return type('obj', (object,), {'data': self.data.get('confirm_password', '')})

class LoginForm(SimpleForm):
    @property
    def nickname(self):
        return type('obj', (object,), {'data': self.data.get('nickname', '')})
    
    @property
    def password(self):
        return type('obj', (object,), {'data': self.data.get('password', '')})