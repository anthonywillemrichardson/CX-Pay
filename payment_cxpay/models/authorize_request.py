# -*- coding: utf-8 -*-
import json
import logging
import requests

from uuid import uuid4

from odoo import _
from odoo.exceptions import UserError

from odoo.addons.payment.models.payment_acquirer import _partner_split_name

import pycurl
import urllib3 as urllib
import urllib.parse as urllib
import urllib.parse as urlparse
import io

_logger = logging.getLogger(__name__)


class CXPay():
    """Authorize.net Gateway API integration.

    This class allows contacting the Authorize.net API with simple operation
    requests. It implements a *very limited* subset of the complete API
    (http://developer.authorize.net/api/reference); namely:
        - Customer Profile/Payment Profile creation
        - Transaction authorization/capture/voiding
    """

    AUTH_ERROR_STATUS = 3

    def __init__(self, acquirer):
        """Initiate the environment with the acquirer data.

        :param record acquirer: payment.acquirer account that will be contacted
        """
        print("")
        if acquirer.state == 'test':
            self.url = 'https://apitest.authorize.net/xml/v1/request.api'
        else:
            self.url = 'https://api.authorize.net/xml/v1/request.api'
        self.state = acquirer.state
        self.name = acquirer.cxpay_login
        self.transaction_key = acquirer.cxpay_transaction_key
        self.login = dict()
        self.order = dict()
        self.billing = dict()
        self.shipping = dict()
        self.responses = dict()

    def setLogin(self, security_key):
        self.login['security_key'] = security_key

    def setOrder(self, orderid, orderdescription, tax, shipping, ponumber, ipadress):
        self.order['orderid'] = orderid
        self.order['orderdescription'] = orderdescription
        self.order['shipping'] = '{0:.2f}'.format(float(shipping))
        self.order['ipaddress'] = ipadress
        self.order['tax'] = '{0:.2f}'.format(float(tax))
        self.order['ponumber'] = ponumber

    def setBilling(self,
                   firstname,
                   lastname,
                   company,
                   address1,
                   address2,
                   city,
                   state,
                   zip,
                   country,
                   phone,
                   fax,
                   email,
                   website):
        self.billing['firstname'] = firstname
        self.billing['lastname'] = lastname
        self.billing['company'] = company
        self.billing['address1'] = address1
        self.billing['address2'] = address2
        self.billing['city'] = city
        self.billing['state'] = state
        self.billing['zip'] = zip
        self.billing['country'] = country
        self.billing['phone'] = phone
        self.billing['fax'] = fax
        self.billing['email'] = email
        self.billing['website'] = website

    def setShipping(self, firstname,
                    lastname,
                    company,
                    address1,
                    address2,
                    city,
                    state,
                    zipcode,
                    country,
                    email):
        self.shipping['firstname'] = firstname
        self.shipping['lastname'] = lastname
        self.shipping['company'] = company
        self.shipping['address1'] = address1
        self.shipping['address2'] = address2
        self.shipping['city'] = city
        self.shipping['state'] = state
        self.shipping['zip'] = zipcode
        self.shipping['country'] = country
        self.shipping['email'] = email

    def doSale(self, amount, ccnumber, ccexp, cvv=''):

        query = ""
        # Login Information

        query = query + "security_key=" + \
            urllib.quote(self.login['security_key']) + "&"
        # Sales Information
        query += "ccnumber=" + urllib.quote(ccnumber) + "&"
        query += "ccexp=" + urllib.quote(ccexp) + "&"
        query += "amount=" + \
            urllib.quote('{0:.2f}'.format(float(amount))) + "&"
        if (cvv != ''):
            query += "cvv=" + urllib.quote(cvv) + "&"
        # Order Information
        for key, value in self.order.items():
            query += key + "=" + urllib.quote(str(value)) + "&"

        # Billing Information
        for key, value in self.billing.items():
            query += key + "=" + urllib.quote(str(value)) + "&"

        # Shipping Information
        for key, value in self.shipping.items():
            query += key + "=" + urllib.quote(str(value)) + "&"

        query += "type=sale"
        return self.doPost(query)

    def doPost(self, query):
        responseIO = io.BytesIO()
        curlObj = pycurl.Curl()
        curlObj.setopt(pycurl.POST, 1)
        curlObj.setopt(pycurl.CONNECTTIMEOUT, 30)
        curlObj.setopt(pycurl.TIMEOUT, 30)
        curlObj.setopt(pycurl.HEADER, 0)
        curlObj.setopt(pycurl.SSL_VERIFYPEER, 0)
        curlObj.setopt(pycurl.WRITEFUNCTION, responseIO.write)

        curlObj.setopt(
            pycurl.URL, "https://cxpay.transactiongateway.com/api/transact.php")

        curlObj.setopt(pycurl.POSTFIELDS, query)

        curlObj.perform()

        data = responseIO.getvalue()
        temp = urlparse.parse_qs(data)
        for key, value in temp.items():
            self.responses[key.decode("utf-8")] = value[0]
        return self.responses


    # Transaction management
    def auth_and_capture(self, token, amount, reference, tx):
        """Authorize and capture a payment for the given amount.

        Authorize and immediately capture a payment for the given payment.token
        record for the specified amount with reference as communication.
        :param record token: the payment.token record that must be charged
        :param str amount: transaction amount (up to 15 digits with decimal point)
        :param str reference: used as "invoiceNumber" in the Authorize.net backend

        :return: a dict containing the response code, transaction id and transaction type
        :rtype: dict
        """
        # response = self._authorize_request(values)
        self.setLogin(token.acquirer_id.cxpay_client_key)
        response = self.doSale(str(amount), str(token.card_number), str(token.exp_date), str(token.cvv_no))
        _logger.info("_authorize_request: Received response:\n%s", response.get('response'))
        if response and response.get('response') and str(response.get('response').decode('ASCII') ) != '1':
            return {
                'x_response_code': response.get('response'),
                'x_response_reason_text': response.get('responsetext')
            }
        result = {
            'x_response_code': response.get('response'),
            'x_trans_id': response.get('transactionid'),
            'x_type': 'auth_capture'                
        }
        errors = response.get('transactionResponse', {}).get('errors')
        if errors:
            result['x_response_reason_text'] = '\n'.join(
                [e.get('errorText') for e in errors])
        return result

