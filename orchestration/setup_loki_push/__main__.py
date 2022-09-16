from cloudshell.workflow.orchestration.sandbox import Sandbox
from cloudshell.workflow.orchestration.setup.default_setup_orchestrator import DefaultSetupWorkflow
from cloudshell.helpers.sandbox_reporter.reporter import SandboxReporter
from push_loki import push_to_loki_setup

sandbox = Sandbox()

reporter = SandboxReporter(api=sandbox.automation_api,
                           reservation_id=sandbox.id,
                           logger=sandbox.logger)

DefaultSetupWorkflow().register(sandbox)

reporter.warning("Beginning setup...")

try:
    sandbox.execute_setup()
except Exception as e:
    reporter.error(f"Caught error during setup. {type(e).__name__}: {str(e)}")
    raise
else:
    reporter.success("Setup complete!")
finally:
    push_to_loki_setup(api=sandbox.automation_api, sandbox_id=sandbox.id, reporter=reporter)
