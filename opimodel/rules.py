
PV_VAL = "pv0"
PV_SEVR = "pvSev0"


class Rule(object):

    def __init__(self, prop_id, name=None):
        """ Base class for rules.

            If no `name` is provided the Rule class name is used.
        Args:
            prop_id: Widget property to set
            pv: Controlling PV
            name (optional): Rule Name as displayed in CSS OPIEditor
        """
        self._prop_id = prop_id
        self._name = type(self).__name__ if name is None else name

    def get_prop_id(self):
        return self._prop_id

    def get_name(self):
        return self._name


class BetweenRule(Rule):

    def __init__(self, prop_id, pv, min_val, max_val,
             min_equals=True, max_equals=True, name=None):
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
        super(BetweenRule, self).__init__(prop_id, name)
        self._pv = pv
        self._min = min_val
        self._max = max_val
        self._min_equals = min_equals
        self._max_equals = max_equals


class GreaterThanRule(Rule):

    def __init__(self, prop_id, pv, threshold, name=None,
                 val=True, false_val=False, sevr_options=None):
        """ Construct an rule setting the specified boolean property
                - True if pv > threshold
                - False otherwise

        Args:
            prop_id: Widget property to set
            pv: Controlling PV
            threshold: Threshold value
            name (optional): Rule Name as displayed in CSS OPIEditor
            val (optional): PV value to set if pv > threshold, default TRUE
            false_val (optional): PV value to set if pv <= threshold, default FALSE
            sevr_options (optional): List of tuples (int, widget value) applied to PV severity
        """
        super(GreaterThanRule, self).__init__(prop_id, name)
        self._pv = pv
        self._threshold = threshold
        self._true_val = val
        self._false_val = false_val
        self._sevr_options = sevr_options


class SelectionRule(Rule):

    def __init__(self, prop_id, pv, options=None, var=PV_VAL, name=None,
                 sevr_options=None, val_options=None, else_val=None):
        """ Simple selection rule setting specified property to one of a
            number of possible values based on the pv value, e.g.:

            widget.rules = []
            options = [(-1, colors.INVALID), (1, colors.MAJOR), (2, colors.MINOR)]
            widget.rules.append(
                rules.SelectionRule('on_color', pv_name, options, var=PV_SEVR))

            Note: the var,options API will be deprecated. Use sevr_options and
            val_options instead:

            widget.rules.append(
                rules.SelectionRule('on_color', pv_name, sevr_options=options)

            In the created rule the sevr_options are tested before the
            val_options

        Args:
            prop_id: Widget property to set
            pv: Controlling PV
            name (optional): Rule Name as displayed in CSS OPIEditor
            options [deprecated]: List of tuples (value, widget value)
            var [deprecated]: Variable to use (pv0 for value, pvSev0 for alarm severity)
            val_options (optional): List of tuples (value, widget value) applied to PV value
            sevr_options (optional): List of tuples (value, widget value) applied to PV severity
            else_value (optional): widget value to use as an else clause
        """
        super(SelectionRule, self).__init__(prop_id, name)
        self._pv = pv
        self._else = else_val
        # support deprecated options,var API
        if options is not None:
            if var == PV_VAL:
                self._val_options = options
                self._sevr_options = None
            else:
                self._val_options = None
                self._sevr_options = options
        else:
            self._sevr_options = sevr_options
            self._val_options = val_options
