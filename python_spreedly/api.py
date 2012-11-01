import time, calendar
from urlparse import urljoin
import requests
from datetime import datetime
from decimal import Decimal
from xml.etree.ElementTree import fromstring
from xml.etree import ElementTree as ET
from objectify import objectify_spreedly

API_VERSION = 'v4'


def utc_to_local(dt):
    ''' Converts utc datetime to local'''
    secs = calendar.timegm(dt.timetuple())
    return datetime(*time.localtime(secs)[:6])


def str_to_datetime(s):
    ''' Converts ISO 8601 string (2009-11-10T21:11Z) to LOCAL datetime,
    or returns None if None is passed'''
    if not s:  #TODO am I on crack?
        return None
    return utc_to_local(datetime.strptime(s, '%Y-%m-%dT%H:%M:%SZ'))

#TODO - more coherent mapping to parse the XML in different methods

class Client(object):
    """
    .. py:class:: Client(token, site_name)
    Create an object to manage queries for a Client on a given site.

    :param token: API access token for authorization.
    :param site_name: the site_name registered with spreedly.
    """

    def __init__(self, token, site_name):
        self.auth = token
        self.base_host = 'https://spreedly.com'
        self.base_path = '/api/{api_version}/{site_name}/'.format(
                api_version=API_VERSION, site_name=site_name)
        self.base_url = urljoin(self.base_host,self.base_path)
        self.url = None

    def _ft(self, tree):
        def ft(x):
            try:
                return tree.findtext(x)
            except:
                None
        return ft

    def _get_parsed_subscriber(self, tree):
        """
        returns a dictionary containing a parsed subscriber tree. lazily.
        The following when called, will genarate a dictionary that will
        lazily parse the the given tree tags for their values
        yeah - This kind of just happened this way
        usage:
        data = self._get_parsed_subscriber(subscriber_tree)
        """
#TODO - when I sort out the keys - make most of this annoying stuff go away
        ft = self._ft(tree)
        truth = lambda x: x == 'true'
        return {
            'customer_id': int(ft('customer-id')),
            'first_name': ft('billing-first-name'),
            'last_name': ft('billing-first-name'),
            'active': truth(ft('active')),
            'active': truth(ft('on-trial')),
            'trial_elegible': truth(ft('eligible-for-free-trial')),
            'lifetime': truth(ft('lifetime-subscription')),
            'recurring': truth(ft('recurring')),
            'card_expires_before_next_auto_renew': truth(ft('card-expires-before-next-auto-renew')),
            'token': ft('token'),
            'name': ft('subscription-plan-name'),
            'feature_level': ft('feature-level'),
            'created_at': str_to_datetime(ft('created-at')),
            'date_changed': str_to_datetime(ft('updated-at')),
            'active_until': str_to_datetime(ft('active_until')),
            'email': ft('email'),
            'screen_name': ft('screen-name'),
        }


    def query(self, url, data=None, action='get'):
        """ .. py:method:: query(url[, data=None, put='get'])

        which has the problem that it doesn't check if there is data for
        PUT, and is hard to read.

        status_codes are not checked here, and should be handled by the
        caller.

        Delete is only supported on test users

        :param url: the api url you wish to reach (not incuding site/version)
        :param data: the data to send in the request. Default to `None`
        :type data: UTF-8 encoded XML or None
        :param action: one of 'get', 'post', 'put' and 'delete'.  Case insensitive, Default 'get'
        :return: response object
        :rtype: :py:mod:`requests` response object
        """
        action = action.lower()
        if action not in ('get', 'put', 'post','delete'):
            raise NotImplementedError()
        url = urljoin(self.base_url, url)
        headers = {
                'User-Agent': 'python-spreedly 1.1',
                }
        if action in ('put','post'):
            headers['Content-Type'] = 'application/xml'
        auth = (self.auth,'X')
        response = getattr(requests, action)(url, auth=auth, headers=headers,
                                             data=data)
        return response


    def get_plans(self):
        """ .. py:method::get_plans()
        get subscription plans for the configured site
        :returns: data as dict
        :raises: :py:exc:`HTTPError` if response is not 200
        """
        response = self.query('subscription_plans.xml', action='get')

        if response.status_code != 200:
            e = requests.HTTPError()
            e.code = response.status_code
            raise e

        # Parse
        result = objectify_spreedly(response.text)
## Left in for reference as I haven't read this closesly
#        result = []
#        tree = fromstring(response.text)
#        for plan in tree.getiterator('subscription-plan'):
#            data = {
#                'name': plan.findtext('name'),
#                'description': plan.findtext('description'),
#                'terms': plan.findtext('terms'),
#                'plan_type': plan.findtext('plan-type'),
#                'price': Decimal(plan.findtext('price')),
#                'enabled': True if plan.findtext('enabled') == 'true' else False,
#                'force_recurring': \
#                    True if plan.findtext('force-recurring') == 'true' else False,
#                'force_renew': \
#                    True if plan.findtext('needs-to-be-renewed') == 'true' else False,
#                'duration': int(plan.findtext('duration-quantity')),
#                'duration_units': plan.findtext('duration-units'),
#                'feature_level': plan.findtext('feature-level'),
#                'return_url': plan.findtext('return-url'),
#                'version': int(plan.findtext('version')) \
#                    if plan.findtext('version') else 0,
#                'speedly_id': int(plan.findtext('id')),
#                'speedly_site_id': int(plan.findtext('site-id')) \
#                    if plan.findtext('site-id') else 0,
#                'created_at': str_to_datetime(plan.findtext('created-at')),
#                'date_changed': str_to_datetime(plan.findtext('updated-at')),
#            }
#            result.append(data)
        return result

    ## Subscriber manipulation
    def create_subscriber(self, customer_id, screen_name):
        ''' .. py:method::create_subscriber(customer_id, screen_name)
        Creates a subscription
        :param customer_id: Customer ID
        :param screen_name: Customer's screen name
        :returns: Data for created customer
        '''
        data = '''
        <subscriber>
            <customer-id>{id}</customer-id>
            <screen-name>{name}</screen-name>
        </subscriber>
        '''.format(id=customer_id, name=screen_name)

        response = self.query(url='subscribers.xml',data=data, action='post')

        # Parse
        data = objectify_spreedly(response.text)
        data['customer_id'] = int(data['customer_id'])
        return data

    def get_signup_url(self, subscriber_id, plan_id, screen_name):
        ''' .. py:method:: get_signup_url(subscriber_id, plan_id, screen_name)
        Subscribe a user to the site plan on a free trial

        subscribe a user to a plan, either trial or not
        :param subscriber_id: ID of the subscriber
        :param plan_id: subscription plan ID
        :param screen_name: user screen name
        :returns: url for subscription
        '''
        return 'subscribers/{id}/subscribe/{plan_id}/{screen_name}'.format(
                id=subscriber_id, plan_id=plan_id,
                screen_name=screen_name)

    def subscribe(self, subscriber_id, plan_id=None):
        ''' .. py:method:: subscribe(subscriber_id, plan_id)
        Subscribe a user to the site plan on a free trial

        subscribe a user to a plan, either trial or not
        :param subscriber_id: ID of the subscriber
        :parma plan_id: subscription plan ID
        '''
        #TODO - This lacks subscription for a site to a plan_id.
        data = '''
        <subscription_plan>
            <id>{plan_id}</id>
        </subscription_plan>'''.format(plan_id=plan_id)

        url = 'subscribers/{id}/subscribe_to_free_trial.xml'.format(id=subscriber_id)
        response = self.query(url, data, action='post')

        # Parse
        data = objectify_spreedly(response.text)
        data['customer_id'] = int(data['customer_id'])
        return data

    def get_info(self, subscriber_id):
        """ .. py:method:: get_info(subscriber_id)

        :param subscriber_id: Id of subscriber to fetch
        :returns: Data as dictionary
        :raises: HTTPError if not 200
        """
        url = 'subscribers/{id}.xml'.format(id=subscriber_id)
        response = self.query(url, action='get')
        if response.status_code != 200:
            e = requests.HTTPError()
            e.code = response.status_code
            raise e

        # Parse
        return objectify_spreedly(response.text)

    def set_info(self, subscriber_id, **kw):
        """ .. py:method: set_info(subscriber_id[, **kw])
        this corrisponds to the update-subscriber action. passed kw args are
        placed into the xml data (not sure how the -/_ are dealt with though)

        There is a design flaw atm where sclient.set_info(sclient.get_info(123))
        will not work at all as the keys are all different
        """
        root = ET.Element('subscriber')

        for key, value in kw.items():
            e = ET.SubElement(root, key)
            e.text = value

        url = 'subscribers/{id}.xml'.format(id=subscriber_id)
        self.query(url, data=ET.tostring(root), action='put')

    def create_complimentary_subscription(self, subscriber_id,
            duration, duration_units, feature_level,
            start_time=None, amount=None):
        """ .. py:method:: create_complimentary_subscription(subscriber_id, duration, duration_units, feature_level[, start_time=None, amount=None])

        corrisponds to adding corrisponding subscription to a subscriber
        :param subscriber_id: Subscriber ID
        :param duration: Duration (unitless)
        :param duration_units: Unit for above (days, weeks, months i think)
        :param feature_level string: what feature level this is at
        :param start_time: If assgining a value for pro-rating purpose, you need this start datetime
        :type start_time: datetime.datetime or None
        :param amount: How much this comp is worth
        :type amount: float or None
        """
        if start_time and amount:
            comp_value = """<start-time>{start_time}</start_time>
            <amount>{amount}</amount>""".format(
                    start_time=start_time.strftime('%Y-%m-%dT%H:%M:%SZ'),
                    amount=amount)
        else:
            comp_value = ''
        data = """<complimentary_subscription>
            <duration_quantity>{duration}</duration_quantity>
            <duration_units>{duration_units}</duration_units>
            <feature_level>{level}</feature_level>
            {comp_value}
            </complimentary_subscription>""".format(
                    duration=duration, duration_units=duration_units, 
                    level=feature_level,comp_value=comp_value)

        url = 'subscribers/{subscriber_id}/complimentary_subscriptions.xml'.format(subscriber_id=subscriber_id)
        self.query(url, data, action='post')

    def complimentary_time_extensions(self, subscriber_id, duration, duration_units):
        """ .. py:method:: complimentary_time_extension(subscriber_id, duration, duration_units)

        corrisponds to adding complimentary time extension to a subscriber
        """
        data = """<complimentary_time_extension>
            <duration_quantity>{duration}</duration_quantity>
            <duration_units>{duration_units}</duration_units>
            </complimentary_time_extension>""".format(
                    duration=duration, duration_units=duration_units)

        url ='subscribers/{id}/complimentary_time_extensions.xml'.format(
                id=subscriber_id)
        self.query(url, data, action='post')

    def get_or_create_subscriber(self, subscriber_id, screen_name):
        """ .. py:method:: get_or_create_subscriber(subscriber_id, screen_name)
        Tries to get info for a subscriber, else creates a new subscriber
        """
        try:
            return self.get_info(subscriber_id)
        except requests.HTTPError, e:
            if e.code == 404:
                return self.create_subscriber(subscriber_id, screen_name)

    ## Payment Gateway Configuration
    #TODO

    ## Invoicing
    #TODO

    ## Payments
    #TODO

    ## Reporting
    #TODO

    ## Emails
    #TODO

    ## Testing
    def delete_subscriber(self, id):
        """ .. py:method:: delete_subscriber(id)
        delete a test subscriber
        :param id: user id
        :returns: status code
        """
        if 'test' in self.base_path:
            url = "{id}.xml".format(id=id)
            response = self.query(url,action='delete')
            return response.status_code
        return

    def cleanup(self):
        """ .. py:method:: cleanup()
        Removes ALL subscribers. NEVER USE IN PRODUCTION! (should only Remove
        test users...)
        :returns: status code
        """
        if 'test' in self.base_path:
            response = self.query('subscribers.xml', action='delete')
            return response.status_code
        return

