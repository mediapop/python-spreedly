# -*- coding: utf-8 -*-
from __future__ import absolute_import
import unittest
import requests
from python_spreedly.api import Client

#TODO find a robust way of doing this without one person's tokens/names
# hard coded
SPREEDLY_AUTH_TOKEN = '59f064f450af88df24f54281f3d78ad8ee0eb8f0'
SPREEDLY_SITE_NAME = 'shelfworthytest'

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
            'date_changed', 'terms', 'name', 'force_recurring', 'feature_level',
            'price', 'enabled', 'plan_type', 'force_renew', 'duration_units',
            'version', 'speedly_site_id', 'duration', 'created_at',
            'speedly_id', 'return_url', 'description'
        ])

        for plan in self.sclient.get_plans():
            self.assertEquals(set(plan.keys()), keys)

    def test_create_subscriber(self):
        """You should be able to create a new subscriber"""
        keys = set([
            'token', 'active_until', 'trial_active', 'created_at',
            'active', 'lifetime', 'customer_id', 'date_changed',
            'trial_elegible', 'plan', 'card_expires_before_next_auto_renew'
        ])

        subscriber = self.sclient.create_subscriber(1, 'test')
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
        keys = set([
            'token', 'active_until', 'trial_active', 'created_at',
            'active', 'lifetime', 'customer_id', 'date_changed',
            'trial_elegible', 'plan', 'card_expires_before_next_auto_renew'
        ])

        # Create a subscriber first
        subscriber = self.sclient.create_subscriber(1, 'test')

        # Subscribe to a free trial
        subscription = self.sclient.subscribe(1, 1824, True)
        self.assertEquals(set(subscriber.keys()), keys)
        self.assertTrue(subscription['trial_active'])

    def test_delete_subscriber(self):
        self.sclient.create_subscriber(1, 'test')
        self.failUnlessEqual(self.sclient.delete_subscriber(1), 200)
        try:
            self.sclient.get_info(1)
            raise AssertionError("Subscriber should have been deleted")
        except requests.HTTPError as e:
            self.assertEquals(e.code, 404)

    def test_get_info(self):
        keys = set([
            'token', 'active_until', 'trial_active', 'created_at',
            'active', 'lifetime', 'customer_id', 'date_changed',
            'trial_elegible', 'plan', 'card_expires_before_next_auto_renew'
        ])

        self.sclient.create_subscriber(1, 'test')
        subscriber = self.sclient.get_info(1)
        self.assertEquals(set(subscriber.keys()), keys)
        self.assertEquals(subscriber['email'], '')
        self.assertEquals(subscriber['screen_name'], 'test')


        self.sclient.set_info(1, email='jack@bauer.com', screen_name='jb')
        subscriber = self.sclient.get_info(1)
        self.assertEquals(subscriber['email'], 'jack@bauer.com')
        self.assertEquals(subscriber['screen_name'], 'jb')


    def test_get_or_create(self):
        keys = set([
            'token', 'active_until', 'trial_active', 'created_at',
            'active', 'lifetime', 'customer_id', 'date_changed',
            'trial_elegible', 'plan', 'card_expires_before_next_auto_renew'
        ])
        #test non existent subscriber
        result = self.sclient.get_or_create_subscriber(123, 'tester')
        self.assertEquals(set(result.keys()), keys)

        #assure that we won't overwrite existing subscriber
        result2 = self.sclient.get_or_create_subscriber(123, 'tester2')
        self.assertEquals(result, result2)


    def test_comp_subscription(self):
        result = self.sclient.get_or_create_subscriber(123, 'tester')

        self.sclient.create_complimentary_subscription(123, 2, 'months', 'Pro')
        # Probelm with asserting comp details here - the assigned time
        # seems kinda fuzzy


if __name__ == '__main__':
    unittest.main()

