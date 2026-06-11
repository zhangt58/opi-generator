PV_VAL = "pv0"
PV_SEVR = "pvSev0"


class Rule:

    def __init__(self, prop_id, name=None, out_exp='false'):
        """ Base class for rules.

            If no `name` is provided the Rule class name is used.
        Args:
            prop_id: Widget property to set
            pv: Controlling PV
            name (optional): Rule Name as displayed in CSS OPIEditor
        """
        self._prop_id = prop_id
        self._name = type(self).__name__ if name is None else name
        self._out_exp = out_exp
        self._extra_pvs = []

    def get_prop_id(self):
        return self._prop_id

    def get_name(self):
        return self._name

    def get_out_exp(self):
        return self._out_exp

    def add_pv(self, pv_name: str, trigger: bool = True):
        """Add a PV, as a trigger of the rule or not.
        # return self to support widget.add_rule(
            <rule-class>.add_pv(xxx))
        """
        self._extra_pvs.append((pv_name, trigger))
        return self


class RawRule(Rule):

    def __init__(self, prop_id, rule_xml, name=None, out_exp='false'):
        """ Construct a rule using logic specified in the rule

            `rule_xml` argument must be correctly formatted XML wrapped in
            a `rule_body` tag:
                <rule_body>
                  <exp ..."><value></value></exp>'
                  <pv_name...>
                </rule_body>
        """
        super(RawRule, self).__init__(prop_id, name, out_exp)
        self._raw_xml = rule_xml


class BetweenRule(Rule):

    def __init__(self,
                 prop_id,
                 pv,
                 min_val,
                 max_val,
                 min_equals=True,
                 max_equals=True,
                 name=None,
                 out_exp='false'):
        """ Construct an rule setting the specified boolean property
                - True if min_val <= pv <= max_val
                - False otherwise

            If min_equals is false the lower limit is replaced by '<'
            If max_equals is false the upper limit is replaced by '<'

        Args:
            prop_id: Widget property to set
            pv: Controlling PV
            min_val: Lower bound
            max_val: Upper bound
            min_equals: True if range is inclusive at lower end
            max_equals: True if range is inclusive at upper end
            name (optional): Rule Name as displayed in CSS OPIEditor
        """
        super(BetweenRule, self).__init__(prop_id, name, out_exp)
        self._pv = pv
        self._min = min_val
        self._max = max_val
        self._min_equals = min_equals
        self._max_equals = max_equals


class GreaterThanRule(Rule):

    def __init__(self,
                 prop_id,
                 pv,
                 threshold,
                 name=None,
                 val=True,
                 false_val=False,
                 sevr_options=None,
                 out_exp='false'):
        """ Construct an rule setting the specified boolean property.

            In the created rule the sevr_options are tested before the
            val_options.
            e.g.:

            widget.rules = []
            opts = [(-1, colors.INVALID), (1, colors.MAJOR), (2, colors.MINOR)]
            widget.rules.append(
                rules.GreaterThanRule('on_color', pv_name, 0.5,
                    val=colors.GREEN,
                    false_val=colors.RED,
                    sevr_options=opts)

            In the created rule the sevr_options are tested before the
            val_options:
                if pvSev0 == -1:
                    col = colors.INVALID
                elseif pvSev0 == 1:
                    col = colors.MAJOR
                elseif pvSev0 == 2:
                    col = colors.MINOR
                elseif pv0 > 0.5:
                    col = colors.RED
                else:
                    col = colors.GREEN


        Args:
            prop_id: Widget property to set
            pv: Controlling PV
            threshold: Threshold value
            name (optional): Rule Name as displayed in CSS OPIEditor
            val (optional): PV value to set if pv > threshold, default TRUE
            false_val (optional):
                PV value to set if pv <= threshold, default FALSE
            sevr_options (optional):
                List of tuples (int, widget value) applied to PV severity
        """
        super(GreaterThanRule, self).__init__(prop_id, name, out_exp)
        self._pv = pv
        self._threshold = threshold
        self._true_val = val
        self._false_val = false_val
        self._sevr_options = sevr_options


class SelectionRule(Rule):

    def __init__(self,
                 prop_id,
                 pv,
                 name=None,
                 val_options=None,
                 sevr_options=None,
                 else_val=None,
                 out_exp='false',
                 auto_fill_val=True):
        # if auto_fill_val is True, expand bool_exp with "pv0" or "pvSev0" with val_options,
        # otherwise, only put val_options.
        # e.g., in the case of out_exp = "true", set a tuple of ("true", "pv0/pvSev0/pvStr0")
        # as a val option is usually wanted.
        """ Simple selection rule setting specified property to one of a
            number of possible values based on the pv value, e.g.:

            widget.rules = []
            opts = [(-1, colors.INVALID), (1, colors.MAJOR), (2, colors.MINOR)]
            val_opts = [(10, colors.RED), (20, colors.BLUE)]
            widget.add_rule(
                rules.SelectionRule('on_color', pv_name,
                    val_options=val_opts,
                    sevr_options=opts,
                    else_val=colors.GREEN)

            In the created rule the sevr_options are tested before the
            val_options:
                if pvSev0 == -1:
                    col = colors.INVALID
                elseif pvSev0 == 1:
                    col = colors.MAJOR
                elseif pvSev0 == 2:
                    col = colors.MINOR
                elseif pv0 == 10:
                    col = colors.RED
                elseif pv0 == 20:
                    col = colours.BLUE
                else:
                    col = colours.GREEN

        Args:
            prop_id: Widget property to set
            pv: Controlling PV
            name (optional): Rule Name as displayed in CSS OPIEditor
            val_options (optional):
                List of tuples (value, widget value) applied to PV value
            sevr_options (optional):
                List of tuples (value, widget value) applied to PV severity
            else_val (optional): widget value to use as an else clause
        """
        super(SelectionRule, self).__init__(prop_id, name, out_exp)
        self._pv = pv
        self._else = else_val
        self._sevr_options = sevr_options
        self._val_options = val_options
        if out_exp == "true":
            self._auto_fill_val = False
        else:
            self._auto_fill_val = auto_fill_val


    def get_auto_fill_val(self):
        return self._auto_fill_val
