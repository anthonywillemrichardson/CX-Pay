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
        print("??????????????????????????????????????????000000000000000000000000000")
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
            print("??????????????????????????", value)
            query += key + "=" + urllib.quote(str(value)) + "&"

        query += "type=sale"
        print("?////////??????///", query)
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

    def _authorize_request(self, data):
        # print("?????????????????????datDadata??????????????????????????????????", data)
        # print("?????????????????????datDadata??????????????????????????????????", data.get('createCustomerProfileRequest').get('profile'))
        # print("?????????????????????datDadata??????????????????????????????????", data['profile'])
        # print("?????????????????????datDadata??????????????????????????????????", data.get('createCustomerProfileRequest').get('profile'))?
        print("?????????????????????datDadata??????????????????????????????????", )
        print("?????????????????????datDadata??????????????????????????????????", )
        # 5/0
        _logger.info(
            '_authorize_request: Sending values to URL %s, values:\n%s', self.url, data)
        self.setLogin("bu8y7R6bucE72Y2UGDM7C2454BVvq48h")
        # self.setBilling("John", "Smith", "Acme, Inc.", "123 Main St", "Suite 200", "Beverly Hills",
        #                 "CA", "90210", "US", "555-555-5555", "555-555-5556", "support@example.com",
        #                 "www.example.com")
        # self.setShipping("Mary", "Smith", "na", "124 Shipping Main St", "Suite Ship", "Beverly Hills",
        #                  "CA", "90210", "US", "support@example.com")
        # self.setOrder("1234", "Big Order", 1, 2, "PO1234", "65.192.14.10")
        resp = self.doSale("5.00", "4111111111111111", "1212", '999')
        print("???????????????????????????????//", resp)
        # 5/0
        # resp = requests.post(self.url, json.dumps(data))
        # resp.raise_for_status()
        # resp = json.loads(resp.content)
        _logger.info("_authorize_request: Received response:\n%s", resp)
        # messages = resp.get('messages')
        # if messages and messages.get('resultCode') == 'Error':
        #     return {
        #         'err_code': messages.get('message')[0].get('code'),
        #         'err_msg': messages.get('message')[0].get('text')
        #     }

        return resp

    # Customer profiles
    def create_customer_profile(self, partner, opaqueData):
        """Create a payment and customer profile in the Authorize.net backend.

        Creates a customer profile for the partner/credit card combination and links
        a corresponding payment profile to it. Note that a single partner in the Odoo
        database can have multiple customer profiles in Authorize.net (i.e. a customer
        profile is created for every res.partner/payment.token couple).

        :param record partner: the res.partner record of the customer
        :param str cardnumber: cardnumber in string format (numbers only, no separator)
        :param str expiration_date: expiration date in 'YYYY-MM' string format
        :param str card_code: three- or four-digit verification number

        :return: a dict containing the profile_id and payment_profile_id of the
                 newly created customer profile and payment profile
        :rtype: dict
    create_customer_profile    """
        values = {
            'createCustomerProfileRequest': {
                'merchantAuthentication': {
                    'name': self.name,
                    'transactionKey': self.transaction_key
                },
                'profile': {
                    'description': ('ODOO-%s-%s' % (partner.id, uuid4().hex[:8]))[:20],
                    'email': partner.email or '',
                    'paymentProfiles': {
                        'customerType': 'business' if partner.is_company else 'individual',
                        'billTo': {
                            'firstName': '' if partner.is_company else _partner_split_name(partner.name)[0],
                            'lastName':  _partner_split_name(partner.name)[1],
                            'address': (partner.street or '' + (partner.street2 if partner.street2 else '')) or None,
                            'city': partner.city,
                            'state': partner.state_id.name or None,
                            'zip': partner.zip or '',
                            'country': partner.country_id.name or None,
                            'phoneNumber': partner.phone or '',
                        },
                        'payment': {
                            'opaqueData': {
                                'dataDescriptor': opaqueData.get('dataDescriptor'),
                                'dataValue': opaqueData.get('dataValue')
                            }
                        }
                    }
                },
                'validationMode': 'liveMode' if self.state == 'enabled' else 'testMode'
            }
        }

        response = self._authorize_request(values)
        print("??responseresponseresponse????????????", response)
        if response and response.get('err_code'):
            raise UserError(_(
                "Authorize.net Error:\nCode: %s\nMessage: %s"
                % (response.get('err_code'), response.get('err_msg'))
            ))

        return {
            'profile_id': response.get('transactionid'),
            'payment_profile_id': response.get('transactionid')
        }

    def create_customer_profile_from_tx(self, partner, transaction_id):
        """Create an Auth.net payment/customer profile from an existing transaction.

        Creates a customer profile for the partner/credit card combination and links
        a corresponding payment profile to it. Note that a single partner in the Odoo
        database can have multiple customer profiles in Authorize.net (i.e. a customer
        profile is created for every res.partner/payment.token couple).

        Note that this function makes 2 calls to the authorize api, since we need to
        obtain a partial cardnumber to generate a meaningful payment.token name.

        :param record partner: the res.partner record of the customer
        :param str transaction_id: id of the authorized transaction in the
                                   Authorize.net backend

        :return: a dict containing the profile_id and payment_profile_id of the
                 newly created customer profile and payment profile as well as the
                 last digits of the card number
        :rtype: dict
        """
        values = {
            'createCustomerProfileFromTransactionRequest': {
                "merchantAuthentication": {
                    "name": self.name,
                    "transactionKey": self.transaction_key
                },
                'transId': transaction_id,
                'customer': {
                    'merchantCustomerId': ('ODOO-%s-%s' % (partner.id, uuid4().hex[:8]))[:20],
                    'email': partner.email or ''
                }
            }
        }

        response = self._authorize_request(values)
        print("Sssssssssssssssssss")
        if not response.get('customerProfileId'):
            _logger.warning(
                'Unable to create customer payment profile, data missing from transaction. Transaction_id: %s - Partner_id: %s'
                % (transaction_id, partner)
            )
            return False

        res = {
            'profile_id': response.get('customerProfileId'),
            'payment_profile_id': response.get('customerPaymentProfileIdList')[0]
        }

        values = {
            'getCustomerPaymentProfileRequest': {
                "merchantAuthentication": {
                    "name": self.name,
                    "transactionKey": self.transaction_key
                },
                'customerProfileId': res['profile_id'],
                'customerPaymentProfileId': res['payment_profile_id'],
            }
        }

        response = self._authorize_request(values)
        print("??????????????????????????????????????????????????")
        res['name'] = response.get('paymentProfile', {}).get(
            'payment', {}).get('creditCard', {}).get('cardNumber')
        return res

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
        print("?????????????????????///....................self.nameself.name", self)
        print("?????????????????????///....................self.nameself.name", self.transaction_key)
        print("?????????????????????///....................self.nameself.name", token.acquirer_id.cxpay_client_key)
        print("?????????????????????///....................self.nameself.name", amount)
        print("?????????????????????///....................self.nameself.name", token.authorize_profile)
        print("?????????????????????///....................self.nameself.name", token.acquirer_ref)
        print("?????????????????????///....................self.nameself.name", reference)
        print("?????????????????????///....................self.nameself.name", reference[:-2])
        print("?????????????????????///....................self.nameself.name", token.card_number, token.exp_date, token.cvv_no)
        # values = {
        #     'createTransactionRequest': {
        #         "merchantAuthentication": {
        #             "name": self.name,
        #             "transactionKey": self.transaction_key
        #         },
        #         'transactionRequest': {
        #             'transactionType': 'authCaptureTransaction',
        #             'amount': str(amount),
        #             'profile': {
        #                 'customerProfileId': token.authorize_profile,
        #                 'paymentProfile': {
        #                     'paymentProfileId': token.acquirer_ref,
        #                 }
        #             },
        #             'order': {
        #                 'invoiceNumber': reference[:20]
        #             }
        #         }

        #     }
        # }
        # response = self._authorize_request(values)
        self.setLogin(token.acquirer_id.cxpay_client_key)
        response = self.doSale(str(amount), str(token.card_number), str(token.exp_date), str(token.cvv_no))
        _logger.info("_authorize_request: Received response:\n%s", response.get('response'))
        print("Ssssssssssssssssssssssssssssssssssssssssssssssssssssssss", str(response.get('response')), str(response.get('response')) != '1')
        if response and response.get('response') and str(response.get('response').decode('ASCII') ) != '1':
            return {
                'x_response_code': response.get('response'),
                'x_response_reason_text': response.get('responsetext')
            }
        print("???????response????????????????////", )
        print("???????response????????????????////", )
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

    def authorize(self, token, amount, reference):
        """Authorize a payment for the given amount.

        Authorize (without capture) a payment for the given payment.token
        record for the specified amount with reference as communication.

        :param record token: the payment.token record that must be charged
        :param str amount: transaction amount (up to 15 digits with decimal point)
        :param str reference: used as "invoiceNumber" in the Authorize.net backend

        :return: a dict containing the response code, transaction id and transaction type
        :rtype: dict
        """
        values = {
            'createTransactionRequest': {
                "merchantAuthentication": {
                    "name": self.name,
                    "transactionKey": self.transaction_key
                },
                'transactionRequest': {
                    'transactionType': 'authOnlyTransaction',
                    'amount': str(amount),
                    'profile': {
                        'customerProfileId': token.authorize_profile,
                        'paymentProfile': {
                            'paymentProfileId': token.acquirer_ref,
                        }
                    },
                    'order': {
                        'invoiceNumber': reference[:20]
                    }
                }

            }
        }
        response = self._authorize_request(values)
        print("????????????????????1111111111111111111111   ???????")

        if response and response.get('response') and response.get('response') != 1:
            return {
                'x_response_code': response.get('response'),
                'x_response_reason_text': response.get('responsetext')
            }

        return {
            'x_response_code': response.get('transactionResponse', {}).get('responseCode'),
            'x_trans_id': response.get('transactionResponse', {}).get('transId'),
            'x_type': 'auth_only'
        }

    def capture(self, transaction_id, amount):
        """Capture a previously authorized payment for the given amount.

        Capture a previsouly authorized payment. Note that the amount is required
        even though we do not support partial capture.

        :param str transaction_id: id of the authorized transaction in the
                                   Authorize.net backend
        :param str amount: transaction amount (up to 15 digits with decimal point)

        :return: a dict containing the response code, transaction id and transaction type
        :rtype: dict
        """
        values = {
            'createTransactionRequest': {
                "merchantAuthentication": {
                    "name": self.name,
                    "transactionKey": self.transaction_key
                },
                'transactionRequest': {
                    'transactionType': 'priorAuthCaptureTransaction',
                    'amount': str(amount),
                    'refTransId': transaction_id,
                }
            }
        }

        response = self._authorize_request(values)

        print("???????????????????????????????????????????Dddddddddddddddddddddddddddddddddddd")
        if response and response.get('response') and response.get('response') != 1:
            return {
                'x_response_code': response.get('response'),
                'x_response_reason_text': response.get('responsetext')
            }
        return {
            'x_response_code': response.get('transactionResponse', {}).get('responseCode'),
            'x_trans_id': response.get('transactionResponse', {}).get('transId'),
            'x_type': 'prior_auth_capture'
        }

    def void(self, transaction_id):
        """Void a previously authorized payment.

        :param str transaction_id: the id of the authorized transaction in the
                                   Authorize.net backend

        :return: a dict containing the response code, transaction id and transaction type
        :rtype: dict
        """
        values = {
            'createTransactionRequest': {
                "merchantAuthentication": {
                    "name": self.name,
                    "transactionKey": self.transaction_key
                },
                'transactionRequest': {
                    'transactionType': 'voidTransaction',
                    'refTransId': transaction_id
                }
            }
        }

        response = self._authorize_request(values)

        print("???????????????????????????Ssssssssssssssssssssssssssss11111111")
        if response and response.get('response') and response.get('response') != 1:
            return {
                'x_response_code': response.get('response'),
                'x_response_reason_text': response.get('responsetext')
            }
        return {
            'x_response_code': response.get('transactionResponse', {}).get('responseCode'),
            'x_trans_id': response.get('transactionResponse', {}).get('transId'),
            'x_type': 'void'
        }

    # Test
    def test_authenticate(self):
        """Test Authorize.net communication with a simple credentials check.

        :return: True if authentication was successful, else False (or throws an error)
        :rtype: bool
        """
        values = {
            'authenticateTestRequest': {
                "merchantAuthentication": {
                    "name": self.name,
                    "transactionKey": self.transaction_key
                },
            }
        }

        response = self._authorize_request(values)
        print("Ssssssssssssssssssssssssss")
        if response and response.get('err_code'):
            return False
        return True

    # Client Key
    def get_client_secret(self):
        """ Create a client secret that will be needed for the AcceptJS integration. """
        values = {
            "getMerchantDetailsRequest": {
                "merchantAuthentication": {
                    "name": self.name,
                    "transactionKey": self.transaction_key,
                }
            }
        }
        response = self._authorize_request(values)
        print("sssssssssssssssssssssssssssssssssssssssss")
        client_secret = response.get('publicClientKey')
        return client_secret
