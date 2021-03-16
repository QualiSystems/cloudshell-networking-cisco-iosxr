#!/usr/bin/python
# -*- coding: utf-8 -*-

import re

from cloudshell.devices.networking_utils import UrlParser
from cloudshell.networking.cisco.flows.cisco_load_firmware_flow import CiscoLoadFirmwareFlow
from cloudshell.networking.cisco.iosxr.command_actions.cisco_iosxr_system_actions import CiscoIOSXRAdminSystemActions


class CiscoIOSXRLoadFirmwareFlow(CiscoLoadFirmwareFlow):
    def __init__(self, cli_handler, logger, packages_to_install):
        super(CiscoIOSXRLoadFirmwareFlow, self).__init__(cli_handler, logger)
        self._packages_to_add = []
        self._result_dict = {}
        self._sync = None
        self._is_old_iosxr = False
        self._cmd_admin_prefix = None
        if not packages_to_install or packages_to_install == "*" or packages_to_install.lower() == "all":
            self._packages_to_add = []
        else:
            self._packages_to_add = packages_to_install.lower().split(" ")

    def execute_flow(self, path, vrf, timeout):
        """Load a firmware onto the device

        :param path: The path to the firmware file, including the firmware file name
        :param vrf: Virtual Routing and Forwarding Name
        :param timeout:
        :return:
        """

        success = False

        full_path_dict = UrlParser().parse_url(path)
        firmware_file_name = full_path_dict.get(UrlParser.FILENAME)
        password = full_path_dict.get(UrlParser.PASSWORD)
        remote_path = path.replace("{}".format(firmware_file_name), "").rstrip("/")
        if vrf and vrf not in remote_path:
            remote_path = remote_path.replace("{}".format(full_path_dict.get(UrlParser.HOSTNAME)),
                                              "{};{}".format(full_path_dict.get(UrlParser.HOSTNAME), vrf))

        with self._cli_handler.get_cli_service(self._cli_handler.enable_mode) as enable_session:
            admin_actions = CiscoIOSXRAdminSystemActions(enable_session, self._logger)
            try:
                admin_actions.show_install_repository()
                remote_path = remote_path.replace(":{}".format(password), "")
            except:
                self._sync = ""
                self._is_old_iosxr = True
                self._cmd_admin_prefix = ""

        output = self._install_add_source(admin_actions=admin_actions, remote_path=remote_path,
                                          firmware_file_name=firmware_file_name, password=password)
        pkgs_for_install = self._filter_packages_for_install(admin_actions=admin_actions, output=output)

        if not pkgs_for_install:
            self._logger.info(admin_actions.prepare_output(self._result_dict))
            raise Exception("Failed to load firmware: No new packages available to be installed (activated).")

        activate_output = admin_actions.install_activate(pkgs_for_install, admin=self._cmd_admin_prefix)
        if re.search(r"install operation \S+ continue asynchronously", activate_output,
                     re.IGNORECASE) or not self._is_old_iosxr:
            operation_id = self._get_operation_id(activate_output)
            admin_actions.show_install_request(operation_id)
            admin_actions.retrieve_install_log(operation_id)

        commit_output = admin_actions.install_commit(admin=self._cmd_admin_prefix)
        if not self._is_old_iosxr:
            operation_id = self._get_operation_id(commit_output)
            admin_actions.show_install_request(operation_id)
            admin_actions.retrieve_install_log(operation_id)

        active_pkgs = admin_actions.show_install_active()
        for pkg in pkgs_for_install:
            package_name = re.sub("^.*:|.x86_64$", "", pkg)
            if package_name not in active_pkgs:
                self._result_dict[package_name] = "Failed to install package, please see logs for details."
            else:
                success = True
                self._result_dict[package_name] = "Package was successfully installed!"
        if not success:
            self._logger.error("Failed to load firmware.")
            raise Exception("Failed to load firmware. Please check logs for details.")
        self._logger.info(admin_actions.prepare_output(self._result_dict))
        return admin_actions.prepare_output(self._result_dict)

    def _install_add_source(self, admin_actions, remote_path, firmware_file_name, password):
        error_map = {
            "{}/{}\S*\s*could not be found".format(remote_path, firmware_file_name): "{} file not found".format(
                firmware_file_name)}
        action_map = {"[Pp]assword:": lambda session, logger: session.send_line(password, logger)}
        if self._is_old_iosxr:
            file_extension = None
            file_extension_match = re.search("\.[a-z]{3}$", firmware_file_name, re.IGNORECASE)
            if file_extension_match:
                file_extension = file_extension_match.group().lstrip(".")
            output = admin_actions.install_add_source(path=remote_path, file_extension=file_extension,
                                                      file_name=firmware_file_name, admin=self._cmd_admin_prefix,
                                                      sync=self._sync, action_map=action_map, error_map=error_map)
        else:
            output = admin_actions.install_add_source(path=remote_path, file_name=firmware_file_name,
                                                      action_map=action_map, error_map=error_map)
            operation_id = self._get_operation_id(output)
            admin_actions.show_install_request(operation_id)
        return output

    def _filter_packages_for_install(self, admin_actions, output):
        pkgs_for_install = []
        available_packages = []
        if self._is_old_iosxr:
            if not output or "no new packages available to be activated" in output.lower():
                raise Exception("Failed to load firmware: no new packages available to be installed (activated)")
            pkgs_for_install = self._get_legacy_packages_for_install(output)
        else:
            operation_id = self._get_operation_id(output)
            log = admin_actions.retrieve_install_log(operation_id)
            for line in re.finditer("\s\s+(\S+\d+(\S+\d*)+)", log, re.MULTILINE):
                available_packages.append(line.group().strip(" \n\t\r"))

            if not available_packages:
                raise Exception("Failed to load firmware: no new packages available for installation (activation)")
            else:
                for pkg in self._get_packages_for_install(available_packages):
                    if pkg not in admin_actions.show_install_active():
                        pkgs_for_install.append(pkg)
                    else:
                        self._result_dict[pkg] = "Package is already installed, skipping."
        return pkgs_for_install

    def _get_operation_id(self, output):
        operation_id_match = re.search("Install operation (\d+)", output, re.IGNORECASE + re.MULTILINE)
        if operation_id_match:
            return operation_id_match.group(1)

    def _get_packages_for_install(self, available_pkgs):
        pkgs_for_install = []
        if self._packages_to_add:
            for pkg in self._packages_to_add:
                if pkg in available_pkgs:
                    pkgs_for_install.append(pkg)
                else:
                    self._result_dict[pkg] = "Package not found, skipping."
        else:
            pkgs_for_install.extend(available_pkgs)
        return pkgs_for_install

    def _get_legacy_packages_for_install(self, output):
        _pkgs_to_add = []
        available_pkgs_re_iter = re.finditer("(?P<type>Info|warning): *(?P<message>\S+\d+(.\d+)+)$", output,
                                             re.MULTILINE + re.IGNORECASE) or []
        for item in available_pkgs_re_iter:
            match_dict = item.groupdict()

            package_name = re.sub("^.*:", "", match_dict.get("message").lower())
            if re.search("\Wpie\W", package_name):
                continue
            if match_dict.get("type").lower() == "warning":
                package_name = re.sub("^.*:", "", match_dict.get("message"))
                if self._packages_to_add and any(
                        [package_name for pkg in self._packages_to_add if package_name in pkg]):
                    self._result_dict[package_name] = "Package is already installed, skipping."
                else:
                    self._result_dict[package_name] = "Package is already installed, skipping."
                continue
            if match_dict.get("type").lower() == "info":
                if not self._packages_to_add:
                    if match_dict.get("message").lower() not in _pkgs_to_add:
                        _pkgs_to_add.append(match_dict.get("message"))
                else:
                    for package in self._packages_to_add:
                        if package.lower() in package_name.lower():
                            if match_dict.get("message").lower() not in _pkgs_to_add:
                                _pkgs_to_add.append(match_dict.get("message"))
        return _pkgs_to_add
