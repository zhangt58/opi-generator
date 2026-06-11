import lxml.etree as et

from opigen import rules, colors


class OpiRule:

    def __init__(self, text_renderer, color_renderer):
        self._color = color_renderer
        self._text = text_renderer

    def render(self, widget_node, tag_name, rule_list):
        if rule_list:
            rules_node = et.SubElement(widget_node, tag_name)
            for rule_model in rule_list:
                self._render_one(rules_node, rule_model)

    def _render_one(self, rules_node, rule_model):
        self.rule_node = et.SubElement(rules_node, 'rule')
        self.rule_node.set('prop_id', rule_model.get_prop_id())
        self.rule_node.set('name', rule_model.get_name())
        self.rule_node.set('out_exp', rule_model.get_out_exp())
        if isinstance(rule_model, rules.BetweenRule):
            self._render_between(rule_model)
        elif isinstance(rule_model, rules.GreaterThanRule):
            self._render_greater_than(rule_model)
        elif isinstance(rule_model, rules.SelectionRule):
            self._render_selection(rule_model)
        elif isinstance(rule_model, rules.RawRule):
            self._render_raw(rule_model)

    def _render_raw(self, rule_model):
        raw_block = et.fromstring(rule_model._raw_xml)

        for child in raw_block.getchildren():
            self.rule_node.append(child)

    def _render_between(self, rule_model):
        """ Write the between rule:
                true iff a < p < b
            as
                true if p > a && p < b
                false otherwise

            The inequalities are replaced by p >= a and p <= b respectively if
            min_equals or max_equals are True
        """
        min_rule = 'pv0 {} {}'.format(">=" if rule_model._min_equals else ">",
                                      rule_model._min)
        max_rule = 'pv0 {} {}'.format("<=" if rule_model._max_equals else "<",
                                      rule_model._max)

        pv_node = et.SubElement(self.rule_node, 'pv')
        pv_node.set('trig', 'true')
        pv_node.text = rule_model._pv

        self._render_value('{} && {}'.format(min_rule, max_rule), 'true')
        self._render_value('true', 'false')

    def _render_greater_than(self, rule_model):
        pv_node = et.SubElement(self.rule_node, 'pv')
        pv_node.set('trig', 'true')
        pv_node.text = rule_model._pv

        if rule_model._sevr_options is not None:
            for (pv_val, prop_val) in rule_model._sevr_options:
                self._render_value('{} == {}'.format(rules.PV_SEVR, pv_val),
                                   prop_val)

        self._render_value(
            '{} > {}'.format(rules.PV_VAL, rule_model._threshold),
            rule_model._true_val)
        self._render_value('true', rule_model._false_val)

    def _render_selection(self, rule_model):

        pv_node = et.SubElement(self.rule_node, 'pv_name')
        # pv_node.set('trig', 'true')
        pv_node.text = rule_model._pv

        # extra PVs
        for i_pv, i_trig in rule_model._extra_pvs:
            _extra_pv_node = et.SubElement(self.rule_node, 'pv_name')
            _extra_pv_node.text = i_pv
            if not i_trig:
                _extra_pv_node.set('trigger', 'false')
        #
        auto_fill_val = rule_model.get_auto_fill_val()

        if rule_model._sevr_options is not None:
            for (pv_val, prop_val) in rule_model._sevr_options:
                if auto_fill_val:
                    self._render_value(
                        '{} == {}'.format(rules.PV_SEVR, pv_val), prop_val)
                else:
                    self._render_value(f'{pv_val}', prop_val)

        if rule_model._val_options is not None:
            for (pv_val, prop_val) in rule_model._val_options:
                if auto_fill_val:
                    self._render_value('{} == {}'.format(rules.PV_VAL, pv_val),
                                       prop_val)
                else:
                    self._render_value(f'{pv_val}', prop_val)

        if rule_model._else is not None:
            self._render_value('true', rule_model._else)

    def _render_value(self, expression, prop_val):
        exp_node = et.SubElement(self.rule_node, 'exp')
        exp_node.set('bool_exp', expression)
        out_exp = self.rule_node.attrib['out_exp']
        if out_exp == 'true':
            value_key = 'expression'
        else:
            value_key = 'value'
        if isinstance(prop_val, colors.Color):
            self._color.render(exp_node, value_key, prop_val)
        else:
            self._text.render(exp_node, value_key, prop_val)
