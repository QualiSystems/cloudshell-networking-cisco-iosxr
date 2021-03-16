#!/usr/bin/python
# -*- coding: utf-8 -*-

from cloudshell.networking.cisco.iosxr.flows.cisco_iosxr_add_vlan_flow import CiscoIOSXRAddVlanFlow
from cloudshell.networking.cisco.iosxr.flows.cisco_iosxr_remove_vlan_flow import CiscoIOSXRRemoveVlanFlow
from cloudshell.networking.cisco.runners.cisco_connectivity_runner import CiscoConnectivityRunner


class CiscoIOSXRConnectivityRunner(CiscoConnectivityRunner):
    @property
    def add_vlan_flow(self):
        return CiscoIOSXRAddVlanFlow(self.cli_handler, self._logger)

    @property
    def remove_vlan_flow(self):
        return CiscoIOSXRRemoveVlanFlow(self.cli_handler, self._logger)
