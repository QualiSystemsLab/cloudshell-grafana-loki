from cloudshell.workflow.orchestration.sandbox import Sandbox
from cloudshell.workflow.orchestration.teardown.default_teardown_orchestrator import DefaultTeardownWorkflow
from cloudshell.helpers.sandbox_reporter.reporter import SandboxReporter
from push_loki import push_loki_teardown

sandbox = Sandbox()
reporter = SandboxReporter(api=sandbox.automation_api,
                           reservation_id=sandbox.id,
                           logger=sandbox.logger)

DefaultTeardownWorkflow().register(sandbox)

reporter.warning("Beginning teardown...")
try:
    sandbox.execute_teardown()
except Exception as e:
    reporter.error(f"Caught error during teardown. {type(e).__name__}: {str(e)}")
    raise
else:
    reporter.success("Teardown complete!")
finally:
    reporter.warning("Pushing Loki Teardown Logs..")
    push_loki_teardown(api=sandbox.automation_api, sandbox_id=sandbox.id)
