#!/usr/bin/python
# -*- coding: utf-8 -*-

import re

from cloudshell.cli.command_template.command_template_executor import CommandTemplateExecutor
from cloudshell.networking.cisco.command_actions.iface_actions import IFaceActions
from cloudshell.networking.cisco.command_templates import iface as iface_command_template
from cloudshell.networking.cisco.command_templates import configuration


class IOSXRIFaceActions(IFaceActions):
    def __init__(self, cli_service, logger):
        """ Add remove vlan

            :param cli_service: config mode cli_service
            :type cli_service: CliService
            :param logger:
            :type logger: Logger
            :return:
            """
        super(IOSXRIFaceActions, self).__init__(cli_service, logger)
        self._cli_service = cli_service
        self._logger = logger

    def get_current_interface_config(self, port_name, action_map=None, error_map=None):
        """Retrieve current interface configuration

        :param port_name:
        :param action_map: actions will be taken during executing commands, i.e. handles yes/no prompts
        :param error_map: errors will be raised during executing commands, i.e. handles Invalid Commands errors
        :return: str
        """

        return CommandTemplateExecutor(self._cli_service,
                                       iface_command_template.SHOW_RUNNING,
                                       action_map=action_map,
                                       error_map=error_map).execute_command(port_name=port_name)

    def clean_vlan_sub_iface_config(self, current_config, action_map=None, error_map=None):
        """ Remove current switchport configuration from interface

        :param current_config: current interface configuration
        :param action_map: actions will be taken during executing commands, i.e. handles yes/no prompts
        :param error_map: errors will be raised during executing commands, i.e. handles Invalid Commands errors
        """

        self._logger.debug("Start cleaning interface switchport configuration")

        for line in current_config.splitlines():
            if line.strip(" ").startswith('encapsulation '):
                line_to_remove = line.strip(" ")
                CommandTemplateExecutor(self._cli_service,
                                        configuration.NO, action_map=action_map,
                                        error_map=error_map).execute_command(command=line_to_remove)

                self._logger.debug("Completed cleaning vlan sub interface configuration")
