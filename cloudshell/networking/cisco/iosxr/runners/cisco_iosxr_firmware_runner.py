#!/usr/bin/python
# -*- coding: utf-8 -*-
from cloudshell.devices.networking_utils import UrlParser
from cloudshell.networking.cisco.iosxr.flows.cisco_iosxr_load_firmware_flow import CiscoIOSXRLoadFirmwareFlow
from cloudshell.networking.cisco.runners.cisco_firmware_runner import CiscoFirmwareRunner


class CiscoIOSXRFirmwareRunner(CiscoFirmwareRunner):
    def __init__(self, logger, cli_handler, features_to_install):
        super(CiscoIOSXRFirmwareRunner, self).__init__(logger, cli_handler)
        self._features_to_install = features_to_install

    @property
    def load_firmware_flow(self):
        return CiscoIOSXRLoadFirmwareFlow(self.cli_handler, self._logger, packages_to_install=self._features_to_install)

    def load_firmware(self, path, vrf_management_name=None):
        """Update firmware version on device by loading provided image, performs following steps:

            1. Copy bin file from remote tftp server.
            2. Clear in run config boot system section.
            3. Set downloaded bin file as boot file and then reboot device.
            4. Check if firmware was successfully installed.

        :param path: full path to firmware file on ftp/tftp location
        :param vrf_management_name: VRF Name
        :return: status / exception
        """

        url = UrlParser.parse_url(path)
        required_keys = [UrlParser.FILENAME, UrlParser.HOSTNAME, UrlParser.SCHEME]

        if not url or not all(key in url for key in required_keys):
            raise Exception(self.__class__.__name__, "Path is wrong or empty")

        return self.load_firmware_flow.execute_flow(path, vrf_management_name, self._timeout)