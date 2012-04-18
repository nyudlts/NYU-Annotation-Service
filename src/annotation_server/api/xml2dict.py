import xml.etree.ElementTree as ET
import re

def _getValue(val):
    """
    If the value can be turned into an integer then do that
    else return it unchanged.
    """
    if re.match(r'^\d+$', val or ''):
        return int(val)
    else:
        return val

def _parseNode(node):
    """ Turn an XML node into a dictionary """
    the_dict = {}

    children = node.getchildren()
    if len(children) > 0:
        # look for what can be determined as a list of XML tags
        # if all tags at the same level are named the same then we
        # can turn those into a list, but not if there is only a single tag as 
        # this would obfuscate the tag name.
        tag_name_list = children[0].tag
        for child in children:
            if tag_name_list != child.tag:
                tag_name_list = False
                break

        if tag_name_list and len(children) > 1:
            # we found a list so place the values of each child into a list
            # against the current nodes tag name in the dictionary
            the_dict[node.tag] = [_parseNode(child)[child.tag] for child in children]
        else:
            # the child nodes were not a list so parse each of them as their own
            # dictionary against the current nodes tag name in the dictionary
            child_dic = {}
            for child in children:
                child_dic.update(_parseNode(child))

            the_dict[node.tag] = child_dic
    elif node.attrib.items():
        # the node has attributes so parse them as if they were child nodes by adding
        # them as their own dictionaries against the current nodes tag name in the dictionary
        attribs_dic = {}
        for k, v in node.attrib.items():
            attribs_dic[k] = _getValue(v)

        the_dict[node.tag] = attribs_dic
    else:
        # the node we are currently parsing has no child nodes so
        # add it's text as the value against the current node tag name in 
        # the dictionary
        the_dict[node.tag] = _getValue(node.text)

    return the_dict

def fromstring(s):
    """
    Given a string representation of some XML, return
    a python dictionary.
    """
    xml = ET.fromstring(s)
    return _parseNode(xml)
