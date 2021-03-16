#!/usr/bin/python
# -*- coding: utf-8 -*-

from cloudshell.devices.flows.action_flows import RemoveVlanFlow
from cloudshell.networking.cisco.iosxr.command_actions.cisco_iosxr_add_remove_vlan_actions import \
    CiscoIOSXRAddRemoveVlanActions
from cloudshell.networking.cisco.iosxr.command_actions.cisco_iosxr_iface_actions import IOSXRIFaceActions


class CiscoIOSXRRemoveVlanFlow(RemoveVlanFlow):
    def __init__(self, cli_handler, logger):
        super(CiscoIOSXRRemoveVlanFlow, self).__init__(cli_handler, logger)

    def execute_flow(self, vlan_range, port_name, port_mode, action_map=None, error_map=None):
        """ Remove configuration of VLANs on multiple ports or port-channels

        :param vlan_range: VLAN or VLAN range
        :param port_name: full port name
        :param port_mode: mode which will be configured on port. Possible Values are trunk and access
        :param action_map:
        :param error_map:
        :return:
        """

        self._logger.info("Remove Vlan {} configuration started".format(vlan_range))
        with self._cli_handler.get_cli_service(self._cli_handler.config_mode) as config_session:
            iface_action = IOSXRIFaceActions(config_session, self._logger)
            vlan_actions = CiscoIOSXRAddRemoveVlanActions(config_session, self._logger)
            port_name = iface_action.get_port_name(port_name)
            if port_name and "-" not in vlan_range:
                port_name += ".{0}".format(vlan_range)
            else:
                raise Exception(self.__class__.__name__, "Vlan range is not supported for IOS XR devices")

            vlan_actions.clean_vlan_sub_interface(port_name)
            current_config = iface_action.get_current_interface_config(port_name)
            if vlan_actions.verify_interface_configured(vlan_range, current_config):
                raise Exception(self.__class__.__name__, "[FAIL] VLAN(s) {} removing failed".format(vlan_range))

        self._logger.info("VLAN(s) {} removing completed successfully".format(vlan_range))
        return "[ OK ] VLAN(s) {} removing completed successfully".format(vlan_range)
