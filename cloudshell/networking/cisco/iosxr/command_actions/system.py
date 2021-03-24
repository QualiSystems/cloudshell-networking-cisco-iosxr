import re
import time
from collections import OrderedDict

from cloudshell.cli.command_template.command_template_executor import (
    CommandTemplateExecutor,
)
from cloudshell.cli.session.session_exceptions import SessionException
from cloudshell.networking.cisco.command_actions.system_actions import SystemActions
from cloudshell.shell.flows.utils.networking_utils import UrlParser

import cloudshell.networking.cisco.iosxr.command_templates.system as sys_template


class CiscoIOSXRSystemActions(SystemActions):
    SUCCESS_COPY_PATTERN = (
        f"{SystemActions.SUCCESS_COPY_PATTERN}|[Uu]pdated [Cc]ommit [Dd]atabase"
    )

    @staticmethod
    def prepare_action_map(source_file, destination_file):
        action_map = OrderedDict()
        url = UrlParser.parse_url(destination_file)
        dst_file_name = url.get(UrlParser.FILENAME)
        source_file_name = UrlParser.parse_url(source_file).get(UrlParser.FILENAME)
        action_map[
            r"[\[\(].*{}[\)\]]".format(dst_file_name)
        ] = lambda session, logger: session.send_line("", logger)

        action_map[
            r"[\[\(]{}[\)\]]".format(source_file_name)
        ] = lambda session, logger: session.send_line("", logger)

        host = url.get(UrlParser.HOSTNAME)
        password = url.get(UrlParser.PASSWORD)
        username = url.get(UrlParser.USERNAME)

        if username:
            action_map[r"[Uu]ser(name)?"] = lambda session, logger: session.send_line(
                username, logger
            )
        if password:
            action_map[r"[Pp]assword"] = lambda session, logger: session.send_line(
                password, logger
            )
        if host:
            action_map[
                r"(?!/){}(?!/)\D*\s*$".format(host)
            ] = lambda session, logger: session.send_line("", logger)

        return action_map

    def load(self, source_file, vrf=None, action_map=None, error_map=None):
        load_cmd = CommandTemplateExecutor(
            self._cli_service,
            sys_template.LOAD,
            action_map=action_map,
            error_map=error_map,
        )
        if vrf:
            load_result = load_cmd.execute_command(source_file=source_file, vrf=vrf)
        else:
            load_result = load_cmd.execute_command(source_file=source_file)

        match_success = re.search(
            r"[\[\(][1-9][0-9]*[\)\]].*bytes|^([1-9][0-9]*)+"
            r"\s*bytes\s*(parsed|process+ed)",
            load_result,
            re.IGNORECASE | re.MULTILINE,
        )
        if not match_success:
            error_str = "Failed to restore configuration, please check logs"
            match_error = re.search(
                r" Can't assign requested address|[Ee]rror:.*\n|%.*$",
                load_result,
                re.IGNORECASE | re.MULTILINE,
            )

            if match_error:
                error_str = "load error: " + match_error.group()

            raise Exception("validate_load_success", error_str)

        return load_result

    def replace_config(self, action_map=None, error_map=None):
        commit_result = CommandTemplateExecutor(
            self._cli_service,
            sys_template.COMMIT_REPlACE,
            action_map=action_map,
            error_map=error_map,
        ).execute_command()

        error_match_commit = re.search(r"(ERROR|[Ee]rror).*\n", commit_result)

        if error_match_commit:
            error_str = error_match_commit.group()
            raise Exception(
                "validate_replace_config_success", "load error: " + error_str
            )
        return commit_result

    def commit(self, action_map=None, error_map=None):
        CommandTemplateExecutor(
            self._cli_service,
            sys_template.COMMIT,
            action_map=action_map,
            error_map=error_map,
        ).execute_command()


class CiscoIOSXRAdminSystemActions(object):
    SHOW_REQUEST_MAX_RETRY = 10
    RESTART_TIMEOUT = 600
    SHOW_REQUEST_TIMEOUT = 30
    INSTALL_COMMIT_TIMEOUT = 20
    INSTALL_ADD_SOURCE_TIMEOUT = 3000

    def __init__(self, cli_service, logger):
        self._cli_service = cli_service
        self._logger = logger

    def install_add_source(
        self,
        path,
        file_name,
        file_extension=None,
        admin=None,
        sync=None,
        action_map=None,
        error_map=None,
    ):
        return CommandTemplateExecutor(
            self._cli_service,
            sys_template.INSTALL_ADD_SRC,
            action_map=action_map,
            error_map=error_map,
            timeout=self.INSTALL_ADD_SOURCE_TIMEOUT,
        ).execute_command(
            path=path,
            file_extension=file_extension,
            file_name=file_name,
            admin=admin,
            sync=sync,
        )

    def install_activate(
        self, feature_names, admin=None, action_map=None, error_map=None
    ):
        return CommandTemplateExecutor(
            self._cli_service,
            sys_template.INSTALL_ACTIVATE,
            action_map=action_map,
            error_map=error_map,
        ).execute_command(feature_names=" ".join(feature_names), admin=admin)

    def show_install_repository(self, action_map=None, error_map=None):
        return CommandTemplateExecutor(
            self._cli_service,
            sys_template.SHOW_INSTALL_REPO,
            action_map=action_map,
            error_map=error_map,
        ).execute_command()

    def install_commit(self, admin=None, timeout=0, action_map=None, error_map=None):
        result = ""
        if not timeout:
            timeout = self.RESTART_TIMEOUT
        try:
            result = CommandTemplateExecutor(
                self._cli_service,
                sys_template.INSTALL_COMMIT,
                action_map=action_map,
                error_map=error_map,
            ).execute_command(admin=admin)
            time.sleep(self.INSTALL_COMMIT_TIMEOUT)
        except SessionException:
            self._cli_service.reconnect(timeout)
        return result

    def show_install_active(self, action_map=None, error_map=None):
        return CommandTemplateExecutor(
            self._cli_service,
            sys_template.SHOW_INSTALL_ACTIVE,
            action_map=action_map,
            error_map=error_map,
        ).execute_command()

    def show_install_commit(self, action_map=None, error_map=None):
        return CommandTemplateExecutor(
            self._cli_service,
            sys_template.SHOW_INSTALL_COMMIT,
            action_map=action_map,
            error_map=error_map,
        ).execute_command()

    def retrieve_install_log(self, operation_id, action_map=None, error_map=None):
        return CommandTemplateExecutor(
            self._cli_service,
            sys_template.SHOW_INSTALL_LOG,
            action_map=action_map,
            error_map=error_map,
        ).execute_command(operation_id=operation_id)

    def show_install_request(self, operation_id, action_map=None, error_map=None):
        retry = 0
        result = ""
        while (
            re.search(
                r"operation {} is \d+% complete".format(operation_id),
                result,
                re.IGNORECASE,
            )
            or retry < self.SHOW_REQUEST_MAX_RETRY
        ):
            try:
                result = CommandTemplateExecutor(
                    self._cli_service,
                    sys_template.SHOW_INSTALL_REQUEST,
                    action_map=action_map,
                    error_map=error_map,
                ).execute_command()
                if re.search(
                    r"No install operation in progress", result, re.IGNORECASE
                ):
                    return True
            except Exception:
                self._cli_service.reconnect(self.RESTART_TIMEOUT)

            if not re.search(
                r"operation {} is \d+% complete".format(operation_id),
                result,
                re.IGNORECASE,
            ):
                retry += 1

            time.sleep(self.SHOW_REQUEST_TIMEOUT)

    def prepare_output(self, result_dict):
        return "\n".join(
            ["{}: {}".format(key, value) for key, value in result_dict.items()]
        )
