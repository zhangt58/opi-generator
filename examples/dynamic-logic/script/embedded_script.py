# flake8: noqa
"""Script that will be embedded into the XML .opi and .bob files."""

from org.csstudio.opibuilder.scriptUtil import PVUtil

# Gets the value of the first PV
pv_value = PVUtil.getDouble(pvs[0])

widget.setPropertyValue("x", pv_value * 10 + 55)
widget.setPropertyValue("width", pv_value * 10 + 55)
widget.setPropertyValue("height", -pv_value * 10 + 55)
