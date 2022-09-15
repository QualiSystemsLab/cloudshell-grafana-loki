import json

from cloudshell.api.cloudshell_api import SandboxDataKeyValue
from cloudshell.shell.core.resource_driver_interface import ResourceDriverInterface
from cloudshell.shell.core.driver_context import InitCommandContext, ResourceCommandContext, AutoLoadResource, \
    AutoLoadAttribute, AutoLoadDetails, CancellationContext
from data_model import *  # run 'shellfoundry generate' to generate data model classes
from loki_handler import LokiHandler
from datetime import datetime
from cloudshell.sandbox_rest.sandbox_api import SandboxRestApiSession
from cloudshell.shell.core.session.cloudshell_session import CloudShellSessionContext

SB_DATA_SETUP_KEY = "Loki Setup ID"


class LokiGrafanaServerDriver(ResourceDriverInterface):

    def __init__(self):
        """
        ctor must be without arguments, it is created with reflection at run time
        """
        pass

    def initialize(self, context):
        """
        Initialize the driver session, this function is called everytime a new instance of the driver is created
        This is a good place to load and cache the driver configuration, initiate sessions etc.
        :param InitCommandContext context: the context the command runs on
        """
        pass

    def cleanup(self):
        """
        Destroy the driver session, this function is called everytime a driver instance is destroyed
        This is a good place to close any open sessions, finish writing to log files
        """
        pass

    # <editor-fold desc="Discovery">

    def get_inventory(self, context):
        """
        Discovers the resource structure and attributes.
        :param AutoLoadCommandContext context: the context the command runs on
        :return Attribute and sub-resource information for the Shell resource you can return an AutoLoadDetails object
        :rtype: AutoLoadDetails
        """
        # See below some example code demonstrating how to return the resource structure and attributes
        # In real life, this code will be preceded by SNMP/other calls to the resource details and will not be static
        # run 'shellfoundry generate' in order to create classes that represent your data model

        '''
        resource = LokiGrafanaServer.create_from_context(context)
        resource.vendor = 'specify the shell vendor'
        resource.model = 'specify the shell model'

        port1 = ResourcePort('Port 1')
        port1.ipv4_address = '192.168.10.7'
        resource.add_sub_resource('1', port1)

        return resource.create_autoload_details()
        '''
        return AutoLoadDetails([], [])

    # </editor-fold>

    # <editor-fold desc="Orchestration Save and Restore Standard">
    def orchestration_save(self, context, cancellation_context, mode, custom_params):
        """
        Saves the Shell state and returns a description of the saved artifacts and information
        This command is intended for API use only by sandbox orchestration scripts to implement
        a save and restore workflow
        :param ResourceCommandContext context: the context object containing resource and reservation info
        :param CancellationContext cancellation_context: Object to signal a request for cancellation. Must be enabled in drivermetadata.xml as well
        :param str mode: Snapshot save mode, can be one of two values 'shallow' (default) or 'deep'
        :param str custom_params: Set of custom parameters for the save operation
        :return: SavedResults serialized as JSON
        :rtype: OrchestrationSaveResult
        """

        # See below an example implementation, here we use jsonpickle for serialization,
        # to use this sample, you'll need to add jsonpickle to your requirements.txt file
        # The JSON schema is defined at:
        # https://github.com/QualiSystems/sandbox_orchestration_standard/blob/master/save%20%26%20restore/saved_artifact_info.schema.json
        # You can find more information and examples examples in the spec document at
        # https://github.com/QualiSystems/sandbox_orchestration_standard/blob/master/save%20%26%20restore/save%20%26%20restore%20standard.md
        '''
              # By convention, all dates should be UTC
              created_date = datetime.datetime.utcnow()
  
              # This can be any unique identifier which can later be used to retrieve the artifact
              # such as filepath etc.
  
              # By convention, all dates should be UTC
              created_date = datetime.datetime.utcnow()
  
              # This can be any unique identifier which can later be used to retrieve the artifact
              # such as filepath etc.
              identifier = created_date.strftime('%y_%m_%d %H_%M_%S_%f')
  
              orchestration_saved_artifact = OrchestrationSavedArtifact('REPLACE_WITH_ARTIFACT_TYPE', identifier)
  
              saved_artifacts_info = OrchestrationSavedArtifactInfo(
                  resource_name="some_resource",
                  created_date=created_date,
                  restore_rules=OrchestrationRestoreRules(requires_same_resource=True),
                  saved_artifact=orchestration_saved_artifact)
  
              return OrchestrationSaveResult(saved_artifacts_info)
        '''
        pass

    def orchestration_restore(self, context, cancellation_context, saved_artifact_info, custom_params):
        """
        Restores a saved artifact previously saved by this Shell driver using the orchestration_save function
        :param ResourceCommandContext context: The context object for the command with resource and reservation info
        :param CancellationContext cancellation_context: Object to signal a request for cancellation. Must be enabled in drivermetadata.xml as well
        :param str saved_artifact_info: A JSON string representing the state to restore including saved artifacts and info
        :param str custom_params: Set of custom parameters for the restore operation
        :return: None
        """
        '''
        # The saved_details JSON will be defined according to the JSON Schema and is the same object returned via the
        # orchestration save function.
        # Example input:
        # {
        #     "saved_artifact": {
        #      "artifact_type": "REPLACE_WITH_ARTIFACT_TYPE",
        #      "identifier": "16_08_09 11_21_35_657000"
        #     },
        #     "resource_name": "some_resource",
        #     "restore_rules": {
        #      "requires_same_resource": true
        #     },
        #     "created_date": "2016-08-09T11:21:35.657000"
        #    }

        # The example code below just parses and prints the saved artifact identifier
        saved_details_object = json.loads(saved_details)
        return saved_details_object[u'saved_artifact'][u'identifier']
        '''
        pass

    # </editor-fold>
    @staticmethod
    def _get_loki_client(context: ResourceCommandContext) -> LokiHandler:
        resource = LokiGrafanaServer.create_from_context(context)
        return LokiHandler(host=context.resource.address,
                           port=resource.loki_port,
                           is_https=True if resource.loki_https == "True" else False)

    @staticmethod
    def _get_sandbox_rest_client(context: ResourceCommandContext) -> SandboxRestApiSession:
        resource = LokiGrafanaServer.create_from_context(context)
        return SandboxRestApiSession(host=resource.sandbox_api_ip,
                                     token=context.connectivity.admin_auth_token,
                                     port=resource.sandbox_api_port,
                                     use_https=True if resource.sandbox_api_https == "True" else False)

    @staticmethod
    def _get_utc_time_str():
        return str(datetime.utcnow())

    @staticmethod
    def _get_loki_setup_labels(sandbox_id: str):
        return {
            "sandbox_id": sandbox_id,
            "job": "Cloudshell Loki Pusher",
            "orch_stage": "setup"
        }

    @staticmethod
    def _get_loki_teardown_labels(sandbox_id: str):
        return {
            "sandbox_id": sandbox_id,
            "job": "Cloudshell Loki Pusher",
            "orch_stage": "post-setup"
        }

    def push_setup_activity(self, context, sandbox_id):
        """
        :param ResourceCommandContext context:
        :param str sandbox_id:
        :return:
        """
        api = CloudShellSessionContext(context).get_api()
        sandbox_api = self._get_sandbox_rest_client(context)
        loki_handler = self._get_loki_client(context)
        stream_labels = self._get_loki_setup_labels(sandbox_id)
        activity = sandbox_api.get_sandbox_activity(sandbox_id)
        events = activity["events"]
        if not events:
            return
        # save last event id, so teardown knows where to pick up
        last_event_id = str(events[-1]["id"])

        loki_handler.push_message_dicts(stream_labels, events)

        sb_data = [SandboxDataKeyValue(SB_DATA_SETUP_KEY, last_event_id)]
        api.SetSandboxData(reservationId=sandbox_id,
                           sandboxDataKeyValues=sb_data)
        return f"'{len(events)}' SETUP events pushed to Loki Server"

    def push_teardown_activity(self, context, sandbox_id):
        """
        :param ResourceCommandContext context:
        :param str sandbox_id:
        :return:
        """
        api = CloudShellSessionContext(context).get_api()
        sandbox_api = self._get_sandbox_rest_client(context)
        loki_handler = self._get_loki_client(context)
        stream_labels = self._get_loki_teardown_labels(sandbox_id)
        sb_data = api.GetSandboxData(sandbox_id).SandboxDataKeyValues
        setup_id = next((x.Value for x in sb_data if x.Key == SB_DATA_SETUP_KEY), None)
        if setup_id:
            starting_id = int(setup_id) + 2
            activity = sandbox_api.get_sandbox_activity(sandbox_id, from_event_id=starting_id)
        else:
            activity = sandbox_api.get_sandbox_activity(sandbox_id)
        events = activity["events"]
        if not events:
            return
        loki_handler.push_message_dicts(stream_labels, events)
        return f"'{len(events)}' POST-SETUP events pushed to Loki Server"

    def get_sandbox_dispro_logs(self, context):
        """
        :param ResourceCommandContext context:
        :return:
        """
        sb_id = context.reservation.reservation_id
        resource = LokiGrafanaServer.create_from_context(context)
        loki_handler = self._get_loki_client(context)

        data = loki_handler.query_job(job_name=resource.promtail_dispro_job,
                                      contains=sb_id)
        return json.dumps(list(reversed(data)), indent=4)

    def get_team_server_logs(self, context, error_filter):
        """
        :param context:
        :param str error_filter:
        :return:
        """
        resource = LokiGrafanaServer.create_from_context(context)
        loki_handler = self._get_loki_client(context)
        data = loki_handler.query_job(job_name=resource.promtail_teamserver_job)
        if error_filter.lower() == "true":
            data = [x for x in data if x["level"] in ["FATAL", "ERROR"]]
        return json.dumps(list(reversed(data)), indent=4)

    def health_check(self, context):
        resource = LokiGrafanaServer.create_from_context(context)
        loki_handler = self._get_loki_client(context)
        loki_handler.health_check()
        api = CloudShellSessionContext(context).get_api()
        msg = "Loki Server is Online"
        api.SetResourceLiveStatus(resourceFullName=resource.name,
                                  liveStatusName="Online",
                                  additionalInfo=msg)
        return msg
