from datetime import datetime
import http.client
import json
import ssl


def date_api_to_odoo(date):
    if date == None or date == False:
        return False
    else:
        return datetime.strptime(date, '%Y-%m-%d').date()


def many2one_to_json(fields):


    #List of ids
    if type(fields) == tuple:
        return {'id': fields[0], 'display_name': fields[1]}

    if type(fields) != dict:
        return fields

    for field in fields:
        #Check if field is tuple
        if type(fields[field]) == tuple:
            if fields[field][0]:
                fields[field] = {'id': fields[field][0], 'display_name': fields[field][1]}
            else:
                fields[field] = False
        
        if type(fields[field]) == list:
            new_list = []

            for item in fields[field]:
                new_item = many2one_to_json(item)
                new_list.append(new_item)
            
            fields[field] = new_list

    return fields


def fields_to_lower_case(fields):

    new_fields = {}

    if type(fields) != dict:

        return fields

    for field in fields:

        if type(fields[field]) == list:

            new_list = []

            for item in fields[field]:

                new_list_item = fields_to_lower_case(item)
                new_list.append(new_list_item)

            new_fields[field.lower()] = new_list
        
        else:

            new_fields[field.lower()] = fields[field]
    
    return new_fields


class api_client():

    def __init__(self, host, database, user, password, ssh=True):

        self.host = host
        self.database = database
        self.user = user
        self.password = password
        self.ssh = ssh
        self.cookie = False
        self.user_data = False


    def _get_connection(self):
        
        if self.ssh:
            connection = http.client.HTTPSConnection(self.host, context=ssl._create_unverified_context())
        else:
            connection = http.client.HTTPConnection(self.host)
        
        return connection

    def get_attributes(self):

        return {
            'host': self.host,
            'database' : self.database,
            'user' : self.user,
            'password': self.password,
            'user_data' : str(self.user_data or ''),
            'cookie': self.cookie or '',
        }


    def __str__(self) -> str:
        
        return str(self.get_attributes())


    def get_headers(self, add_cookie=True):
        

        headers = {
	        'Content-Type' : 'application/json', 
	        'Accept' : '*/*'}

        if add_cookie:
            headers['cookie'] = self.cookie

        return headers

    def authenticate(self):

        connection = self._get_connection()

        uri = '/web/session/authenticate'

        body = {
            "jsonrpc": "2.0", 
            "params": {
                "db": self.database, 
                "login": self.user, 
                "password": self.password
            }}

        connection.request("POST", uri, json.dumps(body), self.get_headers(False))
        
        response = connection.getresponse()

        if response.status == 200:
            user_data_str = response.read()
            user_data_dict = json.loads(user_data_str)

            if 'error' in user_data_dict:
                self.user_data = False
                self.cookie = False
                raise  Exception(user_data_dict['error']['data']['message'])
            else:
                self.user_data = user_data_dict
                self.cookie = response.headers['set-cookie']
        
        else:
            self.user_data = False
            self.cookie = False
            raise Exception('Server %s returned HTTP error %d' % (self.host, response.status))

        connection.close()


    def logout(self):

        connection = self._get_connection()

        uri = '/web/session/logout'

        connection.request("GET", uri, '', self.get_headers())

        response = connection.getresponse()

        if response.status in [200, 303]:
           self.cookie = False
           self.user_data = False
        else:
            raise Exception('Server %s returned HTTP error %d' % (self.host, response.status))
    
        connection.close()


    def call(self, command, uri, params=False):

        connection = self._get_connection()

        if params:
            body = {"jsonrpc": "2.0", "params": params }
        else:
            body = {"jsonrpc": "2.0"}

        connection.request(command, uri, json.dumps(body), self.get_headers())
        
        response = connection.getresponse()

        if response.status == 200:

            response_body = response.read()

            response_dict = json.loads(response_body)

            connection.close()

            if 'error' in response_dict:
                raise  Exception(response_dict['error']['data']['message'])
            else:
                return response_dict['result']
    
        
        else:

            connection.close()

            raise Exception('Server %s returned HTTP error %d' % (self.host, response.status))


    def check_connection(self):

        if not self.cookie:
            return

        uri = '/web/session/check'
        
        try: 
            self.call("POST", uri)
        except:
           self.cookie = False
           self.user_data = False            



    def connected(self):

        return self.cookie != False


class aspide_client(api_client):

    def get_entity(self, cnpj):

        uri = '/grifo_external_source/entity/'

        cnpj_fmt = ('%014d' % int(cnpj))

        params = {"cnpj": cnpj_fmt}

        company_data = self.call("POST", uri, params)

        return company_data['object']


def run_test():
    client = api_client('aspide.tec.br', 'backbone', 'admin', 'backbone')

    client.authenticate()

    print(client)

    client.check_connection()

    client.logout()

    client.check_connection()

    print(client)

if __name__ == '__main__':
    run_test()


