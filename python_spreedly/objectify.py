import xml.etree.ElementTree
from xml.etree import ElementTree as ET
from cStringIO import StringIO
from datetime import datetime
import re

_sub_dash = re.compile('-')


_types = {
    'string'   :  lambda x: x,
    'integer'  :  int,
    'datetime' :  lambda s: datetime.strptime(s, '%Y-%m-%dT%H:%M:%SZ') if s else None,
    'decimal'  :  float,
    'boolean'  :  lambda x: x == 'true',
    }



def parse_element(element):
    children = {}
    data_type = element.attrib.get('type','string')
    children = [] if data_type == 'array' else {}  # change how depth is handled
    name = _sub_dash.sub('_',element.tag)
    #  Depth First recursive population
    if len(element):
        for child in element:
            child_data = parse_element(child)
            if data_type == 'array':
                children.append(child_data)
            else:
                children.update(child_data)
        return { name : children}
    if _types['boolean'](element.attrib.get('nil',False)):
        return {name: None}
    return {name: _types[data_type](element.text)}


def objectify_spreedly(xml):
    if not hasattr(xml, 'read'):
        xml = StringIO(xml)
    tree = ET.parse(xml)
    data = parse_element(tree.getroot())
    return data



if __name__ == "__main__":
    from pprint import pprint
    xml = """<transaction>
    <amount type="decimal">24.0</amount>
    <created-at type="datetime">2009-09-26T03:06:30Z</created-at>
    <currency-code>USD</currency-code>
    <description>Subscription</description>
    <detail-type>Subscription</detail-type>
    <expires-at type="datetime">2009-12-26T04:06:30Z</expires-at>
    <id type="integer">20</id>
    <invoice-id type="integer">64</invoice-id>
    <start-time type="datetime">2009-09-26T03:06:30Z</start-time>
    <terms>3 months</terms>
    <updated-at type="datetime">2009-09-26T03:06:30Z</updated-at>
    <price>$24.00</price>
    <subscriber-customer-id>39053</subscriber-customer-id>
    <detail>
        <payment-method>visa</payment-method>
        <recurring type="boolean">false</recurring>
        <feature-level type="string">example</feature-level>
    </detail>
    </transaction>"""
    print " a test to show magic "
    print
    print xml
    print
    pprint(objectify_spreedly(StringIO(xml)))
