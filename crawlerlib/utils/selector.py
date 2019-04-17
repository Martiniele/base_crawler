import os
import sys
import json
import re
from lxml import etree
from urllib import urlopen
from datetime import datetime
import HTMLParser
import logging

reload(sys)
sys.setdefaultencoding('utf8')


def normalize(x):
    subx = []

    def f1(m):
        n = len(subx)
        g1 = m.group(1)
        subx.append(g1)
        ret = "[#%d]" % n
        return ret

    x = re.sub(r"[\['](\??\(.*?\))[\]']", f1, x)
    x = re.sub(r"'?(?<!@)\.'?|\['?", ";", x)
    x = re.sub(r";;;|;;", ";..;", x)
    x = re.sub(r";$|'?\]|'$", "", x)

    def f2(m):
        g1 = m.group(1)
        return subx[int(g1)]

    x = re.sub(r"#([0-9]+)", f2, x)
    return x


def jsonpath(obj, expr):
    def s(x, y):
        return str(x) + ';' + str(y)

    def isint(x):
        return x.isdigit()

    def trace(expr, obj, path):
        if expr:
            x = expr.split(';')
            loc = x[0]
            x = ';'.join(x[1:])
            if loc == "*":
                def f03(key, loc, expr, obj, path):
                    trace(s(key, expr), obj, path)

                walk(loc, x, obj, path, f03)
            elif loc == "..":
                trace(x, obj, path)

                def f04(key, loc, expr, obj, path):
                    if isinstance(obj, dict):
                        if key in obj:
                            trace(s('..', expr), obj[key], s(path, key))
                    else:
                        if key < len(obj):
                            trace(s('..', expr), obj[key], s(path, key))

                walk(loc, x, obj, path, f04)
            elif loc == "!":
                def f06(key, loc, expr, obj, path):
                    if isinstance(obj, dict):
                        trace(expr, key, path)

                walk(loc, x, obj, path, f06)
            elif isinstance(obj, dict) and loc in obj:
                trace(x, obj[loc], s(path, loc))
            elif isinstance(obj, list) and isint(loc):
                iloc = int(loc)
                if len(obj) > iloc:
                    trace(x, obj[iloc], s(path, loc))
            else:
                if loc.startswith("(") and loc.endswith(")"):
                    e = evalx(loc, obj)
                    trace(s(e, x), obj, path)
                    return
                if loc.startswith("?(") and loc.endswith(")"):
                    def f05(key, loc, expr, obj, path):
                        if isinstance(obj, dict):
                            eval_result = evalx(loc, obj[key])
                        else:
                            eval_result = evalx(loc, obj[int(key)])
                        if eval_result:
                            trace(s(key, expr), obj, path)

                    loc = loc[2:-1]
                    walk(loc, x, obj, path, f05)
                    return
                m = re.match(r'(-?[0-9]*):(-?[0-9]*):?(-?[0-9]*)$', loc)
                if m:
                    if isinstance(obj, (dict, list)):
                        def max(x, y):
                            if x > y:
                                return x
                            return y

                        def min(x, y):
                            if x < y:
                                return x
                            return y

                        objlen = len(obj)
                        s0 = m.group(1)
                        s1 = m.group(2)
                        s2 = m.group(3)
                        start = int(s0) if s0 else 0
                        end = int(s1) if s1 else objlen
                        step = int(s2) if s2 else 1
                        if start < 0:
                            start = max(0, start + objlen)
                        else:
                            start = min(objlen, start)
                        if end < 0:
                            end = max(0, end + objlen)
                        else:
                            end = min(objlen, end)
                        for i in range(start, end, step):
                            trace(s(i, x), obj, path)
                    return

                if loc.find(",") >= 0:
                    for piece in re.split(r"'?,'?", loc):
                        trace(s(piece, x), obj, path)
        else:
            result.append(obj)

    def walk(loc, expr, obj, path, funct):
        if isinstance(obj, list):
            for i in range(0, len(obj)):
                funct(i, loc, expr, obj, path)
        elif isinstance(obj, dict):
            for key in obj:
                funct(key, loc, expr, obj, path)

    def evalx(loc, obj):
        loc = loc.replace("@.length", "len(__obj)")
        loc = loc.replace("&&", " and ").replace("||", " or ")

        def notvar(m):
            return "'%s' not in __obj" % m.group(1)

        loc = re.sub("!@\.([a-zA-Z@_]+)", notvar, loc)

        def varmatch(m):
            def brackets(elts):
                ret = "__obj"
                for e in elts:
                    if isint(e):
                        ret += "[%s]" % e
                    else:
                        ret += "['%s']" % e
                return ret

            g1 = m.group(1)
            elts = g1.split('.')
            if elts[-1] == "length":
                return "len(%s)" % brackets(elts[1:-1])
            return brackets(elts[1:])

        loc = re.sub(r'(?<!\\)(@\.[a-zA-Z@_.]+)', varmatch, loc)

        loc = re.sub(r'(?<!\\)@', "__obj", loc).replace(r'\@', '@')
        try:
            v = eval(loc, caller_globals, {'__obj': obj})
        except Exception as e:
            return False
        return v

    caller_globals = sys._getframe(1).f_globals
    result = []
    if expr and obj:
        cleaned_expr = normalize(expr)
        if cleaned_expr.startswith("$;"):
            cleaned_expr = cleaned_expr[2:]
        trace(cleaned_expr, obj, '$')
        if len(result) > 0:
            return result
    return False


class RuleItem(object):
    def __init__(self, text, attr):
        self._text = text
        self._attr = attr

    def process(self, datas):
        raise NotImplementedError


class JpathRule(RuleItem):
    def process(self, jsontree, url):
        if self._text == "@raw_url":
            return [url]
        datas = jsonpath(jsontree, self._text)
        if datas:
            return datas
        else:
            return []


class XpathRule(RuleItem):
    def process(self, tree, url):
        if self._text == "@raw_url":
            return [url]
        datas = tree.xpath(self._text)
        if datas:
            return [data.strip() for data in datas if data]
        else:
            return []


class RegRule(RuleItem):
    def process(self, datas):
        connector = self._attr.get('connector', '')
        power = self._attr.get('power', None)
        none_marker = self._attr.get('none_marker', None)
        match = self._attr.get('match', 'match')
        pattern = re.compile(self._text, re.U | re.S)
        parsed_result = []
        for data in datas:
            if match == 'match':
                match_result = pattern.match(data)
                if match_result:
                    if power is None:
                        parsed_result.append(connector.join([group for group in match_result.groups() if group]))
                    else:
                        s = 0
                        for num in match_result.groups():
                            s *= int(power)
                            s += int(num)
                            parsed_result.append(str(s))
            elif match == 'findall':
                match_result = pattern.findall(data)
                if match_result:
                    parsed_result.append(connector.join([group for group in match_result if group]))
            elif match == 'search':
                match_result = pattern.search(data)
                if match_result:
                    parsed_result.append(connector.join([group for group in match_result.groups() if group]))
            else:
                # logging.warning("regex is not match, reg: %s, data: %s" % (self._text, data))
                continue
            if not match_result and none_marker:
                parsed_result.append(none_marker)
        return parsed_result


class PrefixRule(RuleItem):
    def process(self, datas):
        result = []
        dup_flag = self._attr.get('no_duplicate', None)
        for data in datas:
            result.append(data if (dup_flag and str(data).startswith(self._text)) or str(data).startswith('http')
                          else self._text + data)
        return result


class SuffixRule(RuleItem):
    def process(self, datas):
        result = []
        for data in datas:
            result.append(data + self._text)
        return result


class SplitRule(RuleItem):
    def process(self, datas):
        result = []
        index = int(self._attr.get('index', '-1'))
        skip_pattern = self._attr.get('not_start_with', None)
        for data in datas:
            slices = data.split(self._text)
            if skip_pattern:
                slices = [item for item in slices if not item.startswith(skip_pattern)]
            if len(slices) <= index:
                continue
            result.extend(slices if index is -1 else [slices[index]])
        return result


class ConnectRule(RuleItem):
    def process(self, datas):
        if not datas:
            return datas
        if len(datas) == 0:
            return []
        self._text = '' if self._text is None else self._text
        self._text = str(self._text)
        self._text = self._text.replace('\\n', '\n')
        return [self._text.join(datas)]


class ReplaceRule(RuleItem):
    def process(self, datas):
        if len(datas) == 0:
            return []
        pattern = self._attr.get('pattern', None)
        if not self._text:
            self._text = ""
        if not pattern:
            return datas
        return [data.replace(pattern, self._text) for data in datas if data]


class FormatRule(RuleItem):
    def process(self, datas):
        return [self._text % data for data in datas]


class DropEmptyRule(RuleItem):
    def process(self, datas):
        return [data for data in datas if data]


class DropRegRule(RuleItem):
    def process(self, datas):
        return [data for data in datas if not re.search(self._text, data)]


class UnescapeRule(RuleItem):
    def process(self, datas):
        parser = HTMLParser.HTMLParser()
        return [parser.unescape(data) for data in datas]


class StripRule(RuleItem):
    def process(self, datas):
        return [item.strip(self._text) for item in datas if item]


class LengthRule(RuleItem):
    def process(self, datas):
        return [str(len(datas))]


class MappingRule(RuleItem):
    def process(self, datas):
        srcValue = self._text
        pattern = self._attr.get('match', 'full')
        destValue = self._attr.get('map2', None)
        if destValue is None:
            raise Exception("mapping rule must has map2 attr.")
        for i, data in enumerate(datas):
            if pattern != 'full':
                if re.search(srcValue, data):
                    datas[i] = destValue
            else:
                if data == srcValue:
                    datas[i] = destValue
        return datas


rule_map = {'xpath': XpathRule,
            'jpath': JpathRule,
            'regex': RegRule,
            'prefix': PrefixRule,
            'suffix': SuffixRule,
            'split': SplitRule,
            'connect': ConnectRule,
            'format': FormatRule,
            'drop_empty': DropEmptyRule,
            'unescape': UnescapeRule,
            'strip': StripRule,
            'mapping': MappingRule,
            'replace': ReplaceRule,
            'drop_reg': DropRegRule,
            'length': LengthRule}


class NodeItem(object):
    def __init__(self, target, attr):
        self._target = target
        self._attr = attr

    def _load_from_elem(self, elem):
        pass

    def load_from_elem(self, elem):
        return self._load_from_elem(elem)

    def _conv_data(self, data, data_type, time_format):
        try:
            if data_type == 'str':
                return data.strip()
            elif data_type == 'int':
                return int(data)
            elif data_type == "float":
                return float(data)
            elif data_type == "object":
                return data
            elif data_type == "datetime":
                return datetime.strptime(
                    data.encode('utf8'), time_format.encode('utf8'))
        except:
            logging.exception('Error occurred when converting data.')
            return None

    def _conv_data_list(self, datas):
        data_type = self._attr.get('data_type', 'str')
        array_type = self._attr.get('array_type', 'array')
        time_format = self._attr.get('time_format', u'')
        if data_type == 'datetime' and time_format == '':
            logging.error('time_format can not be empty when data_type is time')
            return None

        result = []
        for data in datas:
            conv = self._conv_data(data, data_type, time_format)
            if conv is not None:
                result.append(conv)
        limit = int(self._attr.get('limit', '-1'))
        if limit != -1:
            result = result[:limit]
        index = int(self._attr.get('index', '-1'))
        if index != -1:
            result = [result[index]]
        if array_type == "elem" and result:
            result = result[0]
        return result


class MatchNode(NodeItem):
    def __init__(self, target, attr):
        NodeItem.__init__(self, target, attr)
        self._rules = []

    def _load_from_elem(self, elem):
        children = elem.getchildren()
        if not children:
            return False
        if children[0].tag != 'xpath' and children[0].tag != 'jpath':
            raise Exception('The fist rule must be xpath or jpath, now is %s' % children[0].tag)
        for child in children:
            if child.tag not in rule_map:
                raise Exception('unknown rule name: %s' % child.tag)
            self._rules.append(rule_map[child.tag](child.text, child.attrib))
        return True

    def process(self, tree, jsontree, url):
        data = []
        for rule in self._rules:
            if isinstance(rule, XpathRule):
                if tree is None:
                    continue
                data.extend(rule.process(tree, url))
            elif isinstance(rule, JpathRule):
                if jsontree is None:
                    continue
                data.extend(rule.process(jsontree, url))
            else:
                data = rule.process(data)
        data = self._conv_data_list(data)
        if not data:
            return None
        return {self._target: data}

    def show_info(self):
        logging.debug('match')
        for rule in self._rules:
            logging.debug(type(rule))


class StructNode(NodeItem):
    def __init__(self, target, attr):
        NodeItem.__init__(self, target, attr)
        self._xpath = []
        self._jpath = []
        self._subnodes = []

    def _load_from_elem(self, elem):
        children = elem.getchildren()
        if not children:
            return False
        while children[0].tag == 'xpath':
            self._xpath.append(children.pop(0).text)
        while children[0].tag == 'jpath':
            self._jpath.append(children.pop(0).text)
        for child in children:
            target = child.get('target', None)
            if not target:
                raise Exception('node must has target attribute')
            if child.tag == 'match':
                match = MatchNode(target, child.attrib)
                if not match.load_from_elem(child):
                    return False
                self._subnodes.append(match)
            elif child.tag == 'struct':
                struct = StructNode(target, child.attrib)
                if not struct.load_from_elem(child):
                    logging.error('struct call struct load_from_elem error')
                    return False
                self._subnodes.append(struct)
            else:
                logging.error('unknown child in struct: %s' % child.tag)
                return False
        return True

    def process(self, htmltree, jsontree, url):
        paths = []
        if self._xpath:
            proto = 'xpath'
            paths = self._xpath
            if htmltree is None:
                return None
        elif self._jpath:
            proto = 'jpath'
            paths = self._jpath
            if jsontree is None:
                return None
        else:
            return {}
        for path in paths:
            result = []
            if proto == "jpath":
                trees = jsonpath(jsontree, path)
            else:
                trees = htmltree.xpath(path)
            if not trees:
                continue
            for tree in trees:
                sub_result = {}
                for node in self._subnodes:
                    if proto == "jpath":
                        data = node.process(None, tree, url)
                    else:
                        data = node.process(tree, None, url)
                    if not data:
                        continue
                    for key, value in data.items():
                        if key not in sub_result:
                            sub_result[key] = value
                if sub_result:
                    result.append(sub_result)
            return {self._target: result}

    def show_info(self):
        logging.debug('struct')
        for xpath in self._xpath:
            logging.debug('xpath: %s' % xpath)
        for jpath in self._jpath:
            logging.debug('jpath: %s' % jpath)
        for node in self._subnodes:
            node.show_info()


class DictNode(NodeItem):
    def __init__(self, target, attr):
        NodeItem.__init__(self, target, attr)
        self._xpath = []
        self._jpath = []
        self._subnodes = []

    def _load_from_elem(self, elem):
        if not self._attr.get('key', None):
            raise Exception('node must has key attribute')
        children = elem.getchildren()
        if not children:
            return False
        while children[0].tag == 'jpath':
            self._jpath.append(children.pop(0).text)
        while children[0].tag == 'xpath':
            self._xpath.append(children.pop(0).text)
        for child in children:
            target = child.get('target', None)
            if not target:
                raise Exception('node must has target attribute tag:' + child.tag)
            if child.tag == 'match':
                match = MatchNode(target, child.attrib)
                if not match.load_from_elem(child):
                    return False
                self._subnodes.append(match)
            elif child.tag == 'struct':
                struct = StructNode(target, child.attrib)
                if not struct.load_from_elem(child):
                    logging.error('struct call struct load_from_elem error')
                    return False
                self._subnodes.append(struct)
            else:
                logging.error('unknown child in struct: %s' % child.tag)
                return False
        return True

    def process(self, htmltree, jsontree, url):
        if not jsontree:
            return None
        dest_key = self._attr.get('key', None)
        for path in self._jpath:
            result = []
            trees = jsonpath(jsontree, path)
            if not trees:
                continue
            trees = trees[0]
            for dict_key, tree in trees.items():
                sub_result = {}
                for node in self._subnodes:
                    data = node.process(htmltree, tree, url)
                    if not data:
                        continue
                    for key, value in data.items():
                        if key not in sub_result:
                            sub_result[key] = value
                if sub_result:
                    sub_result[dest_key] = dict_key
                if sub_result:
                    result.append(sub_result)
            return {self._target: result}

    def show_info(self):
        logging.debug('dict')
        for jpath in self._jpath:
            logging.debug('jpath: %s' % jpath)
        for node in self._subnodes:
            node.show_info()


class RawNode(NodeItem):
    def __init__(self, target, attr):
        NodeItem.__init__(self, target, attr)
        self._rules = []

    def _load_from_elem(self, elem):
        children = elem.getchildren()
        if not children:
            return False
        for child in children:
            if child.tag not in rule_map:
                raise Exception('unknown rule name: %s' % child.tag)
            self._rules.append(rule_map[child.tag](child.text, child.attrib))
        return True

    def process(self, tree, jsontree, url):
        if tree is None:
            return None
        data = [tree]
        for rule in self._rules:
            data = rule.process(data)
        data = self._conv_data_list(data)
        if not data:
            return None
        return data

    def show_info(self):
        logging.debug('raw')
        for rule in self._rules:
            logging.debug(type(rule))


node_map = {'match': MatchNode,
            'struct': StructNode,
            'dict': DictNode,
            'raw': RawNode}


class TemplateParser(object):
    def __init__(self, template_path):
        self._nodes = []
        self._rawnodes = []
        self._url_pattern = ''
        self._encoding = None
        self._template_path = template_path
        self._url = None

    def init_template(self):
        logging.info("initing file: %s" % self._template_path)
        tree = etree.parse(self._template_path)
        url_pattern_elem = tree.find('url_pattern')
        if url_pattern_elem is None:
            raise Exception("url_pattern is missed, template_path: %s" % self._template_path)
        self._url_pattern = url_pattern_elem.text

        encoding_elem = tree.find('encoding')
        if encoding_elem is not None:
            self._encoding = encoding_elem.text
        else:
            self._encoding = 'utf8'

        children = tree.getroot().getchildren()
        for elem in children:
            if elem.tag not in node_map:
                continue
            target = elem.get('target')
            if not target:
                logging.error('target is missed')
                return False
            node = node_map[elem.tag](target, elem.attrib)
            if node.load_from_elem(elem):
                if elem.tag == "raw":
                    self._rawnodes.append(node)
                else:
                    self._nodes.append(node)
            else:
                return False
        return True

    def parse(self, url, html, is_xml=False):
        pattern = re.compile(self._url_pattern)
        if not pattern.match(url):
            return None
        logging.info("template %s matched for url %s" % (
            os.path.basename(self._template_path), url))
        if self._encoding:
            html = html.decode(self._encoding, 'ignore')
        json_html = None
        json_tree = None
        html_tree = None
        try:
            if self._rawnodes:
                json_html = html
                for node in self._rawnodes:
                    json_html = node.process(json_html, None, url)
                if not json_html:
                    logging.warning('templates parse rawnodes error')
        except:
            logging.exception('failed parse, template: %s', self._template_path)
            return None
        try:
            if not json_html and html.find("<html") == -1 and html.find("<xml") == -1:
                json_tree = json.loads(html)
            elif json_html:
                json_tree = json.loads(json_html)
            if html.find("<html") != -1 or html.find("<xml") != -1:
                html_tree = etree.XML(html) if is_xml else etree.HTML(html)
        except:
            logging.exception('failed to parse html for url: %s', url)
            return None
        result = {}
        try:
            for node in self._nodes:
                data = node.process(html_tree, json_tree, url)
                if not data:
                    continue
                for key, value in data.items():
                    if key not in result:
                        result[key] = value
            if not result:
                logging.warning('templates parse result length 0')
                return None
        except:
            logging.exception('failed parse, template: %s', self._template_path)
            raise
        return result

    def show_info(self):
        for node in self._nodes:
            node.show_info()


class Selector:
    def __init__(self):
        self._template_parser_list = []

    def load_templates(self, dir_path):
        files = os.listdir(dir_path)
        for f in files:
            if not f.endswith('xml'):
                continue
            template_path = os.path.join(dir_path, f)
            template_parser = TemplateParser(template_path)
            try:
                template_parser.init_template()
            except:
                logging.exception('failed to init template, %s', template_path)
                raise
            # template_parser.show_info()
            self._template_parser_list.append(template_parser)

    def load_template_file(self, file_path):
        template_parser = TemplateParser(file_path)
        try:
            template_parser.init_template()
        except:
            logging.exception('failed to init template, %s', file_path)
            raise
        template_parser.show_info()
        self._template_parser_list.append(template_parser)

    def parse(self, url, html, is_xml=False):
        if not html or not url:
            return None
        result_data = {}
        for parser in self._template_parser_list:
            data = parser.parse(url, html, is_xml)
            if data and (len(data) > len(result_data)):
                result_data = data
        return result_data

    def parse_from_url(self, url):
        html = urlopen(url).read()
        return self.parse(url, html)
