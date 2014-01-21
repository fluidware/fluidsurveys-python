# -*- coding: utf-8 -*-
import datetime
import os
import sys
import time
import unittest

from mock import patch

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))
import fluid

from fluidsurveys.test.helper import (
    FluidTestCase,
    NOW, DUMMY_CARD, DUMMY_CHARGE, DUMMY_PLAN, DUMMY_COUPON,
    DUMMY_RECIPIENT, DUMMY_TRANSFER, DUMMY_INVOICE_ITEM)


class FunctionalTests(FluidTestCase):
    request_client = fluidsurveys.http_client.Urllib2Client

    def setUp(self):
        super(FunctionalTests, self).setUp()

        def get_http_client(*args, **kwargs):
            return self.request_client(*args, **kwargs)

        self.client_patcher = patch(
            'fluidsurveys.http_client.new_default_http_client')

        client_mock = self.client_patcher.start()
        client_mock.side_effect = get_http_client

    def tearDown(self):
        super(FunctionalTests, self).tearDown()

        self.client_patcher.stop()

    def test_dns_failure(self):
        api_base = fluidsurveys.api_base
        try:
            fluidsurveys.api_base = 'https://my-invalid-domain.ireallywontresolve/v1'
            self.assertRaises(fluidsurveys.error.APIConnectionError,
                              fluidsurveys.Customer.create)
        finally:
            fluidsurveys.api_base = api_base

    def test_run(self):
        charge = fluidsurveys.Charge.create(**DUMMY_CHARGE)
        self.assertFalse(charge.refunded)
        charge.refund()
        self.assertTrue(charge.refunded)

    def test_refresh(self):
        charge = fluidsurveys.Charge.create(**DUMMY_CHARGE)
        charge2 = fluidsurveys.Charge.retrieve(charge.id)
        self.assertEqual(charge2.created, charge.created)

        charge2.junk = 'junk'
        charge2.refresh()
        self.assertRaises(AttributeError, lambda: charge2.junk)

    def test_list_accessors(self):
        customer = fluidsurveys.Customer.create(card=DUMMY_CARD)
        self.assertEqual(customer['created'], customer.created)
        customer['foo'] = 'bar'
        self.assertEqual(customer.foo, 'bar')

    def test_raise(self):
        EXPIRED_CARD = DUMMY_CARD.copy()
        EXPIRED_CARD['exp_month'] = NOW.month - 2
        EXPIRED_CARD['exp_year'] = NOW.year - 2
        self.assertRaises(fluidsurveys.error.CardError, fluidsurveys.Charge.create,
                          amount=100, currency='usd', card=EXPIRED_CARD)

    def test_unicode(self):
        # Make sure unicode requests can be sent
        self.assertRaises(fluidsurveys.error.InvalidRequestError,
                          fluidsurveys.Charge.retrieve,
                          id=u'☃')

    def test_none_values(self):
        customer = fluidsurveys.Customer.create(plan=None)
        self.assertTrue(customer.id)

    def test_missing_id(self):
        customer = fluidsurveys.Customer()
        self.assertRaises(fluidsurveys.error.InvalidRequestError, customer.refresh)


class RequestsFunctionalTests(FunctionalTests):
    request_client = fluidsurveys.http_client.RequestsClient

# Avoid skipTest errors in < 2.7
if sys.version_info >= (2, 7):
    class UrlfetchFunctionalTests(FunctionalTests):
        request_client = 'urlfetch'

        def setUp(self):
            if fluidsurveys.http_client.urlfetch is None:
                self.skipTest(
                    '`urlfetch` from Google App Engine is unavailable.')
            else:
                super(UrlfetchFunctionalTests, self).setUp()


class PycurlFunctionalTests(FunctionalTests):
    def setUp(self):
        if sys.version_info >= (3, 0):
            self.skipTest('Pycurl is not supported in Python 3')
        else:
            super(PycurlFunctionalTests, self).setUp()

    request_client = fluidsurveys.http_client.PycurlClient


class AuthenticationErrorTest(FluidTestCase):

    def test_invalid_credentials(self):
        key = fluidsurveys.api_key
        try:
            fluidsurveys.api_key = 'invalid'
            fluidsurveys.Customer.create()
        except fluidsurveys.error.AuthenticationError, e:
            self.assertEqual(401, e.http_status)
            self.assertTrue(isinstance(e.http_body, basestring))
            self.assertTrue(isinstance(e.json_body, dict))
        finally:
            fluidsurveys.api_key = key


class CardErrorTest(FluidTestCase):

    def test_declined_card_props(self):
        EXPIRED_CARD = DUMMY_CARD.copy()
        EXPIRED_CARD['exp_month'] = NOW.month - 2
        EXPIRED_CARD['exp_year'] = NOW.year - 2
        try:
            fluidsurveys.Charge.create(amount=100, currency='usd', card=EXPIRED_CARD)
        except fluidsurveys.error.CardError, e:
            self.assertEqual(402, e.http_status)
            self.assertTrue(isinstance(e.http_body, basestring))
            self.assertTrue(isinstance(e.json_body, dict))

# Note that these are in addition to the core functional charge tests


class ChargeTest(FluidTestCase):

    def setUp(self):
        super(ChargeTest, self).setUp()

    def test_charge_list_all(self):
        charge_list = fluidsurveys.Charge.all(created={'lt': NOW})
        list_result = charge_list.all(created={'lt': NOW})

        self.assertEqual(len(charge_list.data),
                         len(list_result.data))

        for expected, actual in zip(charge_list.data,
                                    list_result.data):
            self.assertEqual(expected.id, actual.id)

    def test_charge_list_create(self):
        charge_list = fluidsurveys.Charge.all()

        charge = charge_list.create(**DUMMY_CHARGE)

        self.assertTrue(isinstance(charge, fluidsurveys.Charge))
        self.assertEqual(DUMMY_CHARGE['amount'], charge.amount)

    def test_charge_list_retrieve(self):
        charge_list = fluidsurveys.Charge.all()

        charge = charge_list.retrieve(charge_list.data[0].id)

        self.assertTrue(isinstance(charge, fluidsurveys.Charge))

    def test_charge_capture(self):
        params = DUMMY_CHARGE.copy()
        params['capture'] = False

        charge = fluidsurveys.Charge.create(**params)

        self.assertFalse(charge.captured)

        self.assertTrue(charge is charge.capture())
        self.assertTrue(fluidsurveys.Charge.retrieve(charge.id).captured)

    def test_charge_dispute(self):
        # We don't have a good way of simulating disputes
        # This is a pretty lame test but it at least checks that the
        # dispute code fails in the way we predict, not from e.g.
        # a syntax error

        charge = fluidsurveys.Charge.create(**DUMMY_CHARGE)

        self.assertRaisesRegexp(fluidsurveys.error.InvalidRequestError,
                                'No dispute for charge',
                                charge.update_dispute)

        self.assertRaisesRegexp(fluidsurveys.error.InvalidRequestError,
                                'No dispute for charge',
                                charge.close_dispute)


class AccountTest(FluidTestCase):

    def test_retrieve_account(self):
        account = fluidsurveys.Account.retrieve()
        self.assertEqual('test+bindings@fluidsurveys.com', account.email)
        self.assertFalse(account.charge_enabled)
        self.assertFalse(account.details_submitted)


class BalanceTest(FluidTestCase):

    def test_retrieve_balance(self):
        balance = fluidsurveys.Balance.retrieve()
        self.assertTrue(hasattr(balance, 'available'))
        self.assertTrue(isinstance(balance['available'], list))
        if len(balance['available']):
            self.assertTrue(hasattr(balance['available'][0], 'amount'))
            self.assertTrue(hasattr(balance['available'][0], 'currency'))

        self.assertTrue(hasattr(balance, 'pending'))
        self.assertTrue(isinstance(balance['pending'], list))
        if len(balance['pending']):
            self.assertTrue(hasattr(balance['pending'][0], 'amount'))
            self.assertTrue(hasattr(balance['pending'][0], 'currency'))

        self.assertEqual(False, balance['livemode'])
        self.assertEqual('balance', balance['object'])


class BalanceTransactionTest(FluidTestCase):

    def test_list_balance_transactions(self):
        balance_transactions = fluidsurveys.BalanceTransaction.all()
        self.assertTrue(hasattr(balance_transactions, 'count'))
        self.assertTrue(isinstance(balance_transactions.data, list))


class ApplicationFeeTest(FluidTestCase):
    def test_list_application_fees(self):
        application_fees = fluidsurveys.ApplicationFee.all()
        self.assertTrue(hasattr(application_fees, 'count'))
        self.assertTrue(isinstance(application_fees.data, list))


class CustomerTest(FluidTestCase):

    def test_list_customers(self):
        customers = fluidsurveys.Customer.all()
        self.assertTrue(isinstance(customers.data, list))

    def test_list_charges(self):
        customer = fluidsurveys.Customer.create(description="foo bar",
                                          card=DUMMY_CARD)

        fluidsurveys.Charge.create(customer=customer.id, amount=100, currency='usd')

        self.assertEqual(1,
                         len(customer.charges().data))

    def test_unset_description(self):
        customer = fluidsurveys.Customer.create(description="foo bar")

        customer.description = None
        customer.save()

        self.assertEqual(None, customer.retrieve(customer.id).description)

    def test_cannot_set_empty_string(self):
        customer = fluidsurveys.Customer()
        self.assertRaises(ValueError, setattr, customer, "description", "")

    def test_update_customer_card(self):
        customer = fluidsurveys.Customer.all(count=1).data[0]
        card = customer.cards.create(card=DUMMY_CARD)

        card.name = 'Python bindings test'
        card.save()

        self.assertEqual('Python bindings test',
                         customer.cards.retrieve(card.id).name)


class TransferTest(FluidTestCase):

    def test_list_transfers(self):
        transfers = fluidsurveys.Transfer.all()
        self.assertTrue(isinstance(transfers.data, list))
        self.assertTrue(isinstance(transfers.data[0], fluidsurveys.Transfer))


class RecipientTest(FluidTestCase):

    def test_list_recipients(self):
        recipients = fluidsurveys.Recipient.all()
        self.assertTrue(isinstance(recipients.data, list))
        self.assertTrue(isinstance(recipients.data[0], fluidsurveys.Recipient))

    def test_recipient_transfers(self):
        recipient = fluidsurveys.Recipient.all(count=1).data[0]

        # Weak assertion since the list could be empty
        for transfer in recipient.transfers().data:
            self.assertTrue(isinstance(transfer, fluidsurveys.Transfer))


class CustomerPlanTest(FluidTestCase):

    def setUp(self):
        super(CustomerPlanTest, self).setUp()
        try:
            self.plan_obj = fluidsurveys.Plan.create(**DUMMY_PLAN)
        except fluidsurveys.error.InvalidRequestError:
            self.plan_obj = None

    def tearDown(self):
        if self.plan_obj:
            try:
                self.plan_obj.delete()
            except fluidsurveys.error.InvalidRequestError:
                pass
        super(CustomerPlanTest, self).tearDown()

    def test_create_customer(self):
        self.assertRaises(fluidsurveys.error.InvalidRequestError,
                          fluidsurveys.Customer.create,
                          plan=DUMMY_PLAN['id'])
        customer = fluidsurveys.Customer.create(
            plan=DUMMY_PLAN['id'], card=DUMMY_CARD)
        self.assertTrue(hasattr(customer, 'subscription'))
        self.assertFalse(hasattr(customer, 'plan'))
        customer.delete()
        self.assertFalse(hasattr(customer, 'subscription'))
        self.assertFalse(hasattr(customer, 'plan'))
        self.assertTrue(customer.deleted)

    def test_update_and_cancel_subscription(self):
        customer = fluidsurveys.Customer.create(card=DUMMY_CARD)

        sub = customer.update_subscription(plan=DUMMY_PLAN['id'])
        self.assertEqual(customer.subscription.id, sub.id)
        self.assertEqual(DUMMY_PLAN['id'], sub.plan.id)

        customer.cancel_subscription(at_period_end=True)
        self.assertEqual(customer.subscription.status, 'active')
        self.assertTrue(customer.subscription.cancel_at_period_end)
        customer.cancel_subscription()
        self.assertEqual(customer.subscription.status, 'canceled')

    def test_datetime_trial_end(self):
        customer = fluidsurveys.Customer.create(
            plan=DUMMY_PLAN['id'], card=DUMMY_CARD,
            trial_end=datetime.datetime.now() + datetime.timedelta(days=15))
        self.assertTrue(customer.id)

    def test_integer_trial_end(self):
        trial_end_dttm = datetime.datetime.now() + datetime.timedelta(days=15)
        trial_end_int = int(time.mktime(trial_end_dttm.timetuple()))
        customer = fluidsurveys.Customer.create(plan=DUMMY_PLAN['id'],
                                          card=DUMMY_CARD,
                                          trial_end=trial_end_int)
        self.assertTrue(customer.id)


class InvoiceTest(FluidTestCase):

    def test_invoice(self):
        customer = fluidsurveys.Customer.create(card=DUMMY_CARD)

        customer.add_invoice_item(**DUMMY_INVOICE_ITEM)

        items = customer.invoice_items()
        self.assertEqual(1, len(items.data))

        invoice = fluidsurveys.Invoice.create(customer=customer)

        invoices = customer.invoices()
        self.assertEqual(1, len(invoices.data))
        self.assertEqual(1, len(invoices.data[0].lines.data))
        self.assertEqual(invoice.id, invoices.data[0].id)

        self.assertTrue(invoice.pay().paid)

        # It would be better to test for an actually existing
        # upcoming invoice but that isn't working so we'll just
        # check that the appropriate error comes back for now
        self.assertRaisesRegexp(
            fluidsurveys.error.InvalidRequestError,
            'No upcoming invoices',
            fluidsurveys.Invoice.upcoming,
            customer=customer)


class CouponTest(FluidTestCase):

    def test_create_coupon(self):
        self.assertRaises(fluidsurveys.error.InvalidRequestError,
                          fluidsurveys.Coupon.create, percent_off=25)
        c = fluidsurveys.Coupon.create(**DUMMY_COUPON)
        self.assertTrue(isinstance(c, fluidsurveys.Coupon))
        self.assertTrue(hasattr(c, 'percent_off'))
        self.assertTrue(hasattr(c, 'id'))

    def test_delete_coupon(self):
        c = fluidsurveys.Coupon.create(**DUMMY_COUPON)
        self.assertFalse(hasattr(c, 'deleted'))
        c.delete()
        self.assertFalse(hasattr(c, 'percent_off'))
        self.assertTrue(hasattr(c, 'id'))
        self.assertTrue(c.deleted)


class CustomerCouponTest(FluidTestCase):

    def setUp(self):
        super(CustomerCouponTest, self).setUp()
        self.coupon_obj = fluidsurveys.Coupon.create(**DUMMY_COUPON)

    def tearDown(self):
        self.coupon_obj.delete()

    def test_attach_coupon(self):
        customer = fluidsurveys.Customer.create(coupon=self.coupon_obj.id)
        self.assertTrue(hasattr(customer, 'discount'))
        self.assertNotEqual(None, customer.discount)

        customer.delete_discount()
        self.assertEqual(None, customer.discount)


class InvalidRequestErrorTest(FluidTestCase):

    def test_nonexistent_object(self):
        try:
            fluidsurveys.Charge.retrieve('invalid')
        except fluidsurveys.error.InvalidRequestError, e:
            self.assertEqual(404, e.http_status)
            self.assertTrue(isinstance(e.http_body, basestring))
            self.assertTrue(isinstance(e.json_body, dict))

    def test_invalid_data(self):
        try:
            fluidsurveys.Charge.create()
        except fluidsurveys.error.InvalidRequestError, e:
            self.assertEqual(400, e.http_status)
            self.assertTrue(isinstance(e.http_body, basestring))
            self.assertTrue(isinstance(e.json_body, dict))


class PlanTest(FluidTestCase):

    def setUp(self):
        super(PlanTest, self).setUp()
        try:
            fluidsurveys.Plan(DUMMY_PLAN['id']).delete()
        except fluidsurveys.error.InvalidRequestError:
            pass

    def test_create_plan(self):
        self.assertRaises(fluidsurveys.error.InvalidRequestError,
                          fluidsurveys.Plan.create, amount=2500)
        p = fluidsurveys.Plan.create(**DUMMY_PLAN)
        self.assertTrue(hasattr(p, 'amount'))
        self.assertTrue(hasattr(p, 'id'))
        self.assertEqual(DUMMY_PLAN['amount'], p.amount)
        p.delete()
        self.assertTrue(hasattr(p, 'deleted'))
        self.assertTrue(p.deleted)

    def test_update_plan(self):
        p = fluidsurveys.Plan.create(**DUMMY_PLAN)
        name = "New plan name"
        p.name = name
        p.save()
        self.assertEqual(name, p.name)
        p.delete()

    def test_update_plan_without_retrieving(self):
        p = fluidsurveys.Plan.create(**DUMMY_PLAN)

        name = 'updated plan name!'
        plan = fluidsurveys.Plan(p.id)
        plan.name = name

        # should only have name and id
        self.assertEqual(sorted(['id', 'name']), sorted(plan.keys()))
        plan.save()

        self.assertEqual(name, plan.name)
        # should load all the properties
        self.assertEqual(p.amount, plan.amount)
        p.delete()


class MetadataTest(FluidTestCase):

    def setUp(self):
        super(MetadataTest, self).setUp()
        self.initial_metadata = {
            'address': '77 Massachusetts Ave, Cambridge',
            'uuid': 'id'
        }

        charge = fluidsurveys.Charge.create(
            metadata=self.initial_metadata, **DUMMY_CHARGE)
        customer = fluidsurveys.Customer.create(
            metadata=self.initial_metadata, card=DUMMY_CARD)
        recipient = fluidsurveys.Recipient.create(
            metadata=self.initial_metadata, **DUMMY_RECIPIENT)
        transfer = fluidsurveys.Transfer.create(
            metadata=self.initial_metadata, **DUMMY_TRANSFER)

        self.support_metadata = [charge, customer, recipient, transfer]

    def test_noop_metadata(self):
        for obj in self.support_metadata:
            obj.description = 'test'
            obj.save()
            metadata = obj.retrieve(obj.id).metadata
            self.assertEqual(self.initial_metadata, metadata)

    def test_unset_metadata(self):
        for obj in self.support_metadata:
            obj.metadata = None
            expected_metadata = {}
            obj.save()
            metadata = obj.retrieve(obj.id).metadata
            self.assertEqual(expected_metadata, metadata)

    def test_whole_update(self):
        for obj in self.support_metadata:
            expected_metadata = {'txn_id': '3287423s34'}
            obj.metadata = expected_metadata.copy()
            obj.save()
            metadata = obj.retrieve(obj.id).metadata
            self.assertEqual(expected_metadata, metadata)

    def test_individual_delete(self):
        for obj in self.support_metadata:
            obj.metadata['uuid'] = None
            expected_metadata = {'address': self.initial_metadata['address']}
            obj.save()
            metadata = obj.retrieve(obj.id).metadata
            self.assertEqual(expected_metadata, metadata)

    def test_individual_update(self):
        for obj in self.support_metadata:
            obj.metadata['txn_id'] = 'abc'
            expected_metadata = {'txn_id': 'abc'}
            expected_metadata.update(self.initial_metadata)
            obj.save()
            metadata = obj.retrieve(obj.id).metadata
            self.assertEqual(expected_metadata, metadata)

    def test_combo_update(self):
        for obj in self.support_metadata:
            obj.metadata['txn_id'] = 'bar'
            obj.metadata = {'uid': '6735'}
            obj.save()
            metadata = obj.retrieve(obj.id).metadata
            self.assertEqual({'uid': '6735'}, metadata)

        for obj in self.support_metadata:
            obj.metadata = {'uid': '6735'}
            obj.metadata['foo'] = 'bar'
            obj.save()
            metadata = obj.retrieve(obj.id).metadata
            self.assertEqual({'uid': '6735', 'foo': 'bar'}, metadata)


if __name__ == '__main__':
    unittest.main()
