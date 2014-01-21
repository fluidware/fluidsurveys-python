import datetime
import os
import random
import re
import string
import sys
import unittest

from mock import patch, Mock

import fluid

NOW = datetime.datetime.now()

DUMMY_CARD = {
    'number': '4242424242424242',
    'exp_month': NOW.month,
    'exp_year': NOW.year + 4
}
DUMMY_CHARGE = {
    'amount': 100,
    'currency': 'usd',
    'card': DUMMY_CARD
}

DUMMY_PLAN = {
    'amount': 2000,
    'interval': 'month',
    'name': 'Amazing Gold Plan',
    'currency': 'usd',
    'id': ('fluid-test-gold-' +
           ''.join(random.choice(string.ascii_lowercase) for x in range(10)))
}

DUMMY_COUPON = {
    'percent_off': 25,
    'duration': 'repeating',
    'duration_in_months': 5
}

DUMMY_RECIPIENT = {
    'name': 'John Doe',
    'type': 'individual'
}

DUMMY_TRANSFER = {
    'amount': 400,
    'currency': 'usd',
    'recipient': 'self'
}

DUMMY_INVOICE_ITEM = {
    'amount': 456,
    'currency': 'usd',
}

SAMPLE_INVOICE = fluidsurveys.util.json.loads("""
{
  "amount_due": 1305,
  "attempt_count": 0,
  "attempted": true,
  "charge": "ch_wajkQ5aDTzFs5v",
  "closed": true,
  "customer": "cus_osllUe2f1BzrRT",
  "date": 1338238728,
  "discount": null,
  "ending_balance": 0,
  "id": "in_t9mHb2hpK7mml1",
  "livemode": false,
  "next_payment_attempt": null,
  "object": "invoice",
  "paid": true,
  "period_end": 1338238728,
  "period_start": 1338238716,
  "starting_balance": -8695,
  "subtotal": 10000,
  "total": 10000,
  "lines": {
    "invoiceitems": [],
    "prorations": [],
    "subscriptions": [
      {
        "plan": {
          "interval": "month",
          "object": "plan",
          "identifier": "expensive",
          "currency": "usd",
          "livemode": false,
          "amount": 10000,
          "name": "Expensive Plan",
          "trial_period_days": null,
          "id": "expensive"
        },
        "period": {
          "end": 1340917128,
          "start": 1338238728
        },
        "amount": 10000
      }
    ]
  }
}
""")


class FluidTestCase(unittest.TestCase):
    RESTORE_ATTRIBUTES = ('api_version', 'api_key')

    def setUp(self):
        super(FluidTestCase, self).setUp()

        self._fluid_original_attributes = {}

        for attr in self.RESTORE_ATTRIBUTES:
            self._fluid_original_attributes[attr] = getattr(fluid, attr)

        api_base = os.environ.get('STRIPE_API_BASE')
        if api_base:
            fluidsurveys.api_base = api_base
        fluidsurveys.api_key = os.environ.get(
            'STRIPE_API_KEY', 'tGN0bIwXnHdwOa85VABjPdSn8nWY7G7I')

    def tearDown(self):
        super(FluidTestCase, self).tearDown()

        for attr in self.RESTORE_ATTRIBUTES:
            setattr(fluid, attr, self._fluid_original_attributes[attr])

    # Python < 2.7 compatibility
    def assertRaisesRegexp(self, exception, regexp, callable, *args, **kwargs):
        try:
            callable(*args, **kwargs)
        except exception, err:
            if regexp is None:
                return True

            if isinstance(regexp, basestring):
                regexp = re.compile(regexp)
            if not regexp.search(str(err)):
                raise self.failureException('"%s" does not match "%s"' %
                                            (regexp.pattern, str(err)))
        else:
            raise self.failureException(
                '%s was not raised' % (exception.__name__,))


class FluidUnitTestCase(FluidTestCase):
    REQUEST_LIBRARIES = ['urlfetch', 'requests', 'pycurl']

    if sys.version_info >= (3, 0):
        REQUEST_LIBRARIES.append('urllib.request')
    else:
        REQUEST_LIBRARIES.append('urllib2')

    def setUp(self):
        super(FluidUnitTestCase, self).setUp()

        self.request_patchers = {}
        self.request_mocks = {}
        for lib in self.REQUEST_LIBRARIES:
            patcher = patch("fluidsurveys.http_client.%s" % (lib,))

            self.request_mocks[lib] = patcher.start()
            self.request_patchers[lib] = patcher

    def tearDown(self):
        super(FluidUnitTestCase, self).tearDown()

        for patcher in self.request_patchers.itervalues():
            patcher.stop()


class FluidApiTestCase(FluidTestCase):

    def setUp(self):
        super(FluidApiTestCase, self).setUp()

        self.requestor_patcher = patch('fluidsurveys.api_requestor.APIRequestor')
        requestor_class_mock = self.requestor_patcher.start()
        self.requestor_mock = requestor_class_mock.return_value

    def tearDown(self):
        super(FluidApiTestCase, self).tearDown()

        self.requestor_patcher.stop()

    def mock_response(self, res):
        self.requestor_mock.request = Mock(return_value=(res, 'reskey'))


class MyResource(fluidsurveys.resource.APIResource):
    pass


class MySingleton(fluidsurveys.resource.SingletonAPIResource):
    pass


class MyListable(fluidsurveys.resource.ListableAPIResource):
    pass


class MyCreatable(fluidsurveys.resource.CreateableAPIResource):
    pass


class MyUpdateable(fluidsurveys.resource.UpdateableAPIResource):
    pass


class MyDeletable(fluidsurveys.resource.DeletableAPIResource):
    pass


class MyComposite(fluidsurveys.resource.ListableAPIResource,
                  fluidsurveys.resource.CreateableAPIResource,
                  fluidsurveys.resource.UpdateableAPIResource,
                  fluidsurveys.resource.DeletableAPIResource):
    pass
