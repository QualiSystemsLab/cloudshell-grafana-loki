from cloudshell.api.cloudshell_api import CloudShellAPISession, InputNameValue
from cloudshell.helpers.sandbox_reporter.reporter import SandboxReporter

LOKI_SERVER_MODEL = "Loki Grafana Server"


class LokiPushException(Exception):
    pass


def push_to_loki_teardown(api: CloudShellAPISession, sandbox_id: str, reporter: SandboxReporter):
    """
    Search DB and trigger command on Loki Server
    Loki resource does not have to be reserved in sandbox
    """
    loki_search = api.FindResources(resourceModel=LOKI_SERVER_MODEL).Resources
    if not loki_search:
        raise ValueError(f"No Loki server of model {LOKI_SERVER_MODEL} found")
    if len(loki_search) > 1:
        raise ValueError("Script strategy supports only single Loki Server in DB")

    loki_server = loki_search[0]

    reporter.warning("Pushing Loki Teardown Logs..")
    try:
        api.ExecuteCommand(reservationId=sandbox_id,
                           targetName=loki_server.Name,
                           targetType="Resource",
                           commandName="push_teardown_activity",
                           commandInputs=[InputNameValue("sandbox_id", sandbox_id)],
                           printOutput=True)
    except Exception as e:
        err_msg = f"Failed to push sandbox events to Loki. {type(e).__name__}: {str(e)}"
        reporter.error(err_msg)
        api.SetReservationLiveStatus(reservationId=sandbox_id,
                                     liveStatusName="Error",
                                     additionalInfo=err_msg)
        raise LokiPushException(err_msg)
    reporter.success("Loki Events Pushed")
