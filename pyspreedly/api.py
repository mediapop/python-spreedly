import time, calendar
from urlparse import urljoin
import requests
from datetime import datetime
from xml.etree import ElementTree as ET
from objectify import objectify_spreedly

__all__ = [
        'API_VERSION', 'Client', ]

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
        return result

    ## Subscriber manipulation
    def create_subscriber(self, customer_id, screen_name):
        ''' .. py:method::create_subscriber(customer_id, screen_name)
        Creates a subscription
        :param customer_id: Customer ID
        :param screen_name: Customer's screen name
        :returns: Data for created customer
        :raises: HTTPError if response code isn't 201
        '''
        data = '''
        <subscriber>
            <customer-id>{id}</customer-id>
            <screen-name>{name}</screen-name>
        </subscriber>
        '''.format(id=customer_id, name=screen_name)

        response = self.query(url='subscribers.xml',data=data, action='post')

        # Parse
        if not response.status_code == 201:
            raise requests.HTTPError("status code: {0}, text: {1}".format(response.status_code, response.text))
        return objectify_spreedly(response.text)

    def get_signup_url(self, subscriber_id, plan_id, screen_name, token=None):
        ''' .. py:method:: get_signup_url(subscriber_id, plan_id, screen_name)
        Subscribe a user to the site plan on a free trial

        subscribe a user to a plan, either trial or not
        :param subscriber_id: ID of the subscriber
        :param plan_id: subscription plan ID
        :param screen_name: user screen name
        :param token: customer token or None - if passed use the token version
            of the url
        :returns: url for subscription
        '''
        subscriber_id = str(subscriber_id)
        plan_id = str(plan_id)
        if token:
            url = '/'.join(('subscribers',subscriber_id,token,
                'subscribe', plan_id))
        else:
            url = '/'.join(('subscribers',subscriber_id,'subscribe',
                plan_id,screen_name))
        url = urljoin(self.base_url, url)
        return url

    def subscribe(self, subscriber_id, plan_id=None):
        ''' .. py:method:: subscribe(subscriber_id, plan_id)
        Subscribe a user to the site plan on a free trial

        subscribe a user to a free trial plan.
        :param subscriber_id: ID of the subscriber
        :parma plan_id: subscription plan ID
        :returns: dictionary with xml data if all is good
        :raises: HTTPError if response status not 200
        '''
        #TODO - This lacks subscription for a site to a plan_id.
        data = '''
        <subscription_plan>
            <id>{plan_id}</id>
        </subscription_plan>'''.format(plan_id=plan_id)

        url = 'subscribers/{id}/subscribe_to_free_trial.xml'.format(id=subscriber_id)
        response = self.query(url, data, action='post')

        if response.status_code != 200:
            raise requests.HTTPError("status code: {0}, text: {1}".format(response.status_code, response.text))

        # Parse
        return objectify_spreedly(response.text)

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

    def allow_free_trial(self, subscriber_id):
        """ .. py:method:: allow_free_trial(subscriber_id)

        programatically allow for a new free trial
        :param subscriber_id: the id of the subscriber
        :returns: subscriber data as dictionary if all good,
        :raises: HTTPError if not so good (non-200)
        """
        url = 'subscribers/{id}/allow_free_trial.xml'.format(id=subscriber_id)
        response = self.query(url,'', action='post')
        if response.status_code is not 200:
            raise requests.HTTPError('status; {0}, text {1}'.format(
                response.status_code, response.text))
        else:
            return objectify_spreedly(response.text)


    def add_fee(self, subscriber_id, name, description, group, amount):
        """ .. py:method:: add_fee(subscriber_id, name, description, group, amount)
        Add a fee to a user with subscriber_id
        :param subscriber_id: the id of the subscriber
        :param name: the name of the fee (eg - Excess Bandwidth Charge)
        :param description: a description of the charge
        :param group: a group to add this charge too
        :param amount: the amount the charge is for
        :returns: the response object
        """
        data = """
        <fee>
          <name>{name}</name>
          <description>{description}</description>
          <group>{group}</group>
          <amount>{amount}</amount>
        </fee>
        """.format(name=name, description=description, group=group, amount=amount)
        url = 'subscribers/{id}/fees.xml'.format(id=subscriber_id)
        response = self.query(url,data, action='post')
        return response

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
            url = "subscribers/{id}.xml".format(id=id)
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

