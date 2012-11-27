# -*- coding: utf-8 -*-
from __future__ import absolute_import
import unittest
import requests
from urlparse import urljoin
from pyspreedly.api import Client
from . site_conf import SPREEDLY_AUTH_TOKEN, SPREEDLY_SITE_NAME
from pprint import pprint

#TODO find a robust way of doing this without one person's tokens/names
# hard coded

# Create some plans in your test site

class  SpreedlyTests(unittest.TestCase):
    def setUp(self):
        self.sclient = Client(SPREEDLY_AUTH_TOKEN, SPREEDLY_SITE_NAME)

        # Remove all subscribers
        self.sclient.cleanup()

    def tearDown(self):
        # Remove all subscribers
        self.sclient.cleanup()

    def test_get_plans(self):
        #TODO add standard set of plans to ensure you get them all.
        keys = set([
            'charge_after_first_period',
            'needs_to_be_renewed',
            'feature_level',
            'updated_at',
            'id',
            'charge_later_duration_quantity',
            'setup_fee_amount',
            'duration_quantity',
            'version',
            'terms',
            'description',
            'setup_fee_description',
            'price',
            'plan_type',
            'charge_later_duration_units',
            'minimum_needed_for_charge',
            'setup_fee_currency_code',
            'name',
            'force_recurring',
            'versions',
            'amount',
            'created_at',
            'enabled',
            'duration_units',
            'currency_code',
            'return_url',
            ])
        plans = self.sclient.get_plans()
        print 'get_plans'
        pprint(plans)

        for plan in self.sclient.get_plans():
            plan = plan['subscription_plan']
            self.assertEquals(set(plan.keys()), keys)

    def test_create_subscriber(self):
        """You should be able to create a new subscriber"""
        keys = set([
            'subscription_plan_name',
            'eligible_for_free_trial',
            'updated_at',
            'on_gift',
            'ready_to_renew_since',
            'eligible_for_setup_fee',
            'billing_country',
            'billing_last_name',
            'on_metered',
            'billing_zip',
            'payment_account_on_file',
            'customer_id',
            'recurring',
            'pagination_id',
            'active_until',
            'store_credit_currency_code',
            'in_grace_period',
            'billing_address1',
            'billing_first_name',
            'ready_to_renew',
            'card_expires_before_next_auto_renew',
            'active',
            'billing_phone_number',
            'screen_name',
            'store_credit',
            'billing_city',
            'created_at',
            'feature_level',
            'grace_until',
            'email',
            'token',
            'billing_state',
            'on_trial',
            'lifetime_subscription',
            'payment_account_display',
            ])

        subscriber = self.sclient.create_subscriber(1, 'test')
        print 'create_subscriber'
        pprint(subscriber)
        self.assertEquals(set(subscriber.keys()), keys)
        self.assertEquals(subscriber['customer_id'], 1)

    def test_cleanup(self):
        """make sure that cleanup works, or all of this will be off"""
        subscriber = self.sclient.create_subscriber(1, 'test')
        subscriber2 = self.sclient.create_subscriber(2, 'test2')
        self.assertEquals(subscriber['customer_id'], 1)
        self.assertEquals(subscriber2['customer_id'], 2)
        self.sclient.cleanup()
        try:
            subscriber = self.sclient.get_info(1)
            raise AssertionError("Subscriber 1 should not exist")
        except requests.HTTPError as e:
            self.assertEquals(e.code, 404)
        try:
            subscriber2 = self.sclient.get_info(2)
            raise AssertionError("Subscriber 1 should not exist")
        except requests.HTTPError as e:
            self.assertEquals(e.code, 404)

    def test_subscribe(self):
        """Test you can create a trial subscription"""
        keys = set(['subscription_plan_name',
            'active',
            'created_at',
            'token',
            'active_until',
            'eligible_for_free_trial',
            'card_expires_before_next_auto_renew',
            'customer_id',
            'updated_at',
            'on_gift',
            'ready_to_renew_since',
            'eligible_for_setup_fee',
            'billing_country',
            'billing_last_name',
            'on_metered',
            'payment_account_on_file',
            'recurring',
            'pagination_id',
            'store_credit_currency_code',
            'in_grace_period',
            'billing_address1',
            'billing_first_name',
            'ready_to_renew',
            'billing_phone_number',
            'billing_city',
            'store_credit',
            'screen_name',
            'lifetime_subscription',
            'feature_level',
            'grace_until',
            'email',
            'billing_zip',
            'billing_state',
            'on_trial',
            'payment_account_display',
            ])

        # Create a subscriber first
        subscriber = self.sclient.create_subscriber(1, 'test')
        print 'subscribe'
        pprint(subscriber)

        # Subscribe to a free trial
        subscription = self.sclient.subscribe(1, 21431)
        self.assertEquals(set(subscriber.keys()), keys)
        self.assertTrue(subscription['on_trial'])

    def test_delete_subscriber(self):
        subscriber = self.sclient.create_subscriber(1, 'test')
        self.failUnlessEqual(self.sclient.delete_subscriber(1), 200)
        try:
            self.sclient.get_info(1)
            raise AssertionError("Subscriber should have been deleted")
        except requests.HTTPError as e:
            self.assertEquals(e.code, 404)

    def test_get_info(self):
        keys = set([
            'subscription_plan_name',
            'invoices',
            'eligible_for_free_trial',
            'updated_at',
            'on_gift',
            'ready_to_renew_since',
            'eligible_for_setup_fee',
            'billing_country',
            'billing_last_name',
            'on_metered',
            'billing_zip',
            'payment_account_on_file',
            'customer_id',
            'recurring',
            'pagination_id',
            'active_until',
            'store_credit_currency_code',
            'in_grace_period',
            'billing_address1',
            'billing_first_name',
            'ready_to_renew',
            'card_expires_before_next_auto_renew',
            'active',
            'billing_phone_number',
            'screen_name',
            'store_credit',
            'billing_city',
            'created_at',
            'feature_level',
            'grace_until',
            'email',
            'token',
            'billing_state',
            'on_trial',
            'lifetime_subscription',
            'payment_account_display',
            ])

        self.sclient.create_subscriber(1, 'test')
        subscriber = self.sclient.get_info(1)
        self.assertEquals(set(subscriber.keys()), keys)
        self.assertEquals(subscriber['email'], None)
        self.assertEquals(subscriber['screen_name'], 'test')


        self.sclient.set_info(1, email='jack@bauer.com', screen_name='jb')
        subscriber = self.sclient.get_info(1)
        self.assertEquals(subscriber['email'], 'jack@bauer.com')
        self.assertEquals(subscriber['screen_name'], 'jb')


    def test_get_signup_url(self):
        norm_url = urljoin(self.sclient.base_url,'subscribers/44763/subscribe/41/screen-name-for-44763')
        tokened_url = urljoin(self.sclient.base_url, 'subscribers/44763/d21de2b33ed811c1a040a507988241f550c45aee/subscribe/41')
        cust_id = 44763
        token = 'd21de2b33ed811c1a040a507988241f550c45aee'
        screen_name = 'screen-name-for-44763'
        plan_id = 41
        test_url = self.sclient.get_signup_url(cust_id, plan_id, screen_name)
        self.assertEquals(urljoin(self.sclient.base_url,test_url), norm_url)
        test_url = self.sclient.get_signup_url(cust_id, plan_id, screen_name,token)
        self.assertEquals(urljoin(self.sclient.base_url,test_url), tokened_url)


    def test_get_or_create(self):
        keys = set([
            'subscription_plan_name',
            'eligible_for_free_trial',
            'updated_at',
            'on_gift',
            'ready_to_renew_since',
            'eligible_for_setup_fee',
            'billing_country',
            'billing_last_name',
            'on_metered',
            'billing_zip',
            'payment_account_on_file',
            'customer_id',
            'recurring',
            'pagination_id',
            'active_until',
            'store_credit_currency_code',
            'in_grace_period',
            'billing_address1',
            'billing_first_name',
            'ready_to_renew',
            'card_expires_before_next_auto_renew',
            'active',
            'billing_phone_number',
            'screen_name',
            'store_credit',
            'billing_city',
            'created_at',
            'feature_level',
            'grace_until',
            'email',
            'token',
            'billing_state',
            'on_trial',
            'lifetime_subscription',
            'payment_account_display',
            ])
        #test non existent subscriber
        result = self.sclient.get_or_create_subscriber(123, 'tester')
        self.assertTrue(set(result.keys()) == keys)

        self.maxDiff =None
        #assure that we won't overwrite existing subscriber
        result2 = self.sclient.get_or_create_subscriber(123, 'tester2')
        diffset = [k for k in result if result2[k] != result[k]]
        self.assertFalse(diffset)


    def test_comp_subscription(self):
        result = self.sclient.get_or_create_subscriber(123, 'tester')

        self.sclient.create_complimentary_subscription(123, 2, 'months', 'Pro')
        # Probelm with asserting comp details here - the assigned time
        # seems kinda fuzzy

    def test_add_fee(self):
        # trial user cannot have fees.
        subscriber = self.sclient.get_or_create_subscriber(123, 'tester')
        result = self.sclient.add_fee(subscriber_id=123,name='Test Fee', description='A Test Levy',
                group='test fees', amount=24.0)
        self.assertEquals(result, 422)


if __name__ == '__main__':
    unittest.main()

