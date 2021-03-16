#!/usr/bin/python
# -*- coding: utf-8 -*-

from cloudshell.devices.flows.action_flows import AddVlanFlow
from cloudshell.networking.cisco.iosxr.command_actions.cisco_iosxr_add_remove_vlan_actions import \
    CiscoIOSXRAddRemoveVlanActions
from cloudshell.networking.cisco.iosxr.command_actions.cisco_iosxr_iface_actions import IOSXRIFaceActions
from cloudshell.networking.cisco.iosxr.command_actions.cisco_iosxr_system_actions import CiscoIOSXRSystemActions


class CiscoIOSXRAddVlanFlow(AddVlanFlow):
    def __init__(self, cli_handler, logger):
        super(CiscoIOSXRAddVlanFlow, self).__init__(cli_handler, logger)

    def execute_flow(self, vlan_range, port_mode, port_name, qnq, c_tag):
        """ Configures VLANs on multiple ports or port-channels

        :param vlan_range: VLAN or VLAN range
        :param port_mode: mode which will be configured on port. Possible Values are trunk and access
        :param port_name: full port name
        :param qnq:
        :param c_tag:
        :return:
        """

        self._logger.info("Add VLAN(s) {} configuration started".format(vlan_range))

        with self._cli_handler.get_cli_service(self._cli_handler.config_mode) as config_session:
            iface_action = IOSXRIFaceActions(config_session, self._logger)
            vlan_actions = CiscoIOSXRAddRemoveVlanActions(config_session, self._logger)
            system_actions = CiscoIOSXRSystemActions(config_session, self._logger)
            port_name = iface_action.get_port_name(port_name)
            if port_name and "-" not in vlan_range:
                port_name += ".{0}".format(vlan_range)
            else:
                raise Exception(self.__class__.__name__, "Vlan range is not supported for IOS XR devices")

            current_config = iface_action.get_current_interface_config(port_name)
            if port_name in current_config:
                iface_action.enter_iface_config_mode(port_name)
                iface_action.clean_vlan_sub_iface_config(current_config)
            vlan_actions.set_vlan_to_interface(vlan_range, port_mode, port_name, qnq, c_tag)
            system_actions.commit()
            current_config = iface_action.get_current_interface_config(port_name)
            if port_name not in current_config:
                raise Exception(self.__class__.__name__, "[FAIL] VLAN(s) {} configuration failed".format(vlan_range))

        self._logger.info("VLAN(s) {} configuration completed successfully".format(vlan_range))
        return "[ OK ] VLAN(s) {} configuration completed successfully".format(vlan_range)
