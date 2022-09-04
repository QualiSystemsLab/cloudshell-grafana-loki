# Cloudshell Loki-Grafana Centralized Logging 
This repo documents a sample implementation of cloudshell centralized logging with the Grafana / Loki / Promtail stack.
As cloudshell outputs JSON logs, these can be ingested into any centralized logging tool, not just Elastic stack.
Having logs in central location allows to search logs from multiple servers related to the same sandbox.

### Sample Grafana Dashboard
![Loki](images/sample_error_dashboard.png)

## Solution Architecture
Grafana provides dashboard UI, Loki is the backend logging aggregator, Promtail agent installed on all Quali components.
These components are analagous to elastic stack: 
- Kibana -> Grafana
- Loki -> Elastic
- Promtail -> FluentD / Filebeat

#### Generic Architecture
![Loki](images/loki-architecture.png)

#### Cloudshell Integration Architecture
![Cloudshell Loki Architecture](images/cloudshell-loki-architecture.drawio.png)

## Setup and Usage
1. Configure cloudshell JSON logs by following along with [Quali help article](https://help.quali.com/Online%20Help/0.0/Portal/Content/IG/CentralLog/central-logging-overview.htm?tocpath=Installation%20and%20Configuration%7CCloudShell%20Suite%7CCentral%20Logging%20Configuration%7C_____0)
2. Set up Grafana Server (see [Grafana help article](https://grafana.com/docs/grafana/latest/setup-grafana/installation/))
3. Set up Loki Server. This can be done with [local binary install](https://grafana.com/docs/loki/latest/installation/local/) or [docker installation](https://grafana.com/docs/loki/latest/installation/docker/)
4. Install Promtail agent on Quali components by downloading and adding the Promtail binary file to each server. See [Grafana help article](https://grafana.com/docs/loki/latest/clients/promtail/installation/) and get correct binary from grafana [github release page](https://github.com/grafana/loki/releases)
5. Configure Loki Server config yaml in same directory as binary. 
   - See [sample Loki config](loki-promtail/loki-windows-amd64/loki-local-config.yaml) and run Loki exe.
   - Run [sample bat file](loki-promtail/loki-windows-amd64/run_loki.bat) to run exe
   - See [Grafana help](https://grafana.com/docs/loki/latest/configuration/) for reference.
6. Configure Promtail config yaml to scrape the target logs and run agent. 
   - See [sample Promtail config](loki-promtail/promtail-windows-amd64/promtail-local-config.yaml)
   - Run [sample bat file](loki-promtail/promtail-windows-amd64/run_promtail.bat) to run service
7. Configure Loki as data source in Grafana. See [Grafana help](https://grafana.com/docs/grafana/latest/datasources/loki/)
8. Customize dashboards
9. Add cloudshell Loki service to cloudshell, which gives option to optionally present loki data from sandbox via Loki API calls

## Customizing LogQL Samples
Loki / Grafana uses LogQL syntax which can allow to target specific keywords / fields / files. Queries can be very flexible and customized to user needs.

sample filter to pull "dispro" logs of a target sandbox ID:

`{job="qualiserver"} | json | category="DistributedProvisioning.Execution" |= "b83d649f-319b-4545-bf56-39b65b30668a"`

Pull sandbox setup via wildcard filter:

`{filename=~".*b83d649f-319b-4545-bf56-39b65b30668a.*Setup.*",job="sandboxlogs"}`


## References
- [Grafana Loki High Level Intro](https://youtu.be/1obKa6UhlkY)
- [Install blog](https://reachmnadeem.wordpress.com/2020/12/30/log-scrapping-made-easy-with-grafana-loki-in-windows/)
- [LogQL Syntax](https://grafana.com/docs/loki/latest/logql/log_queries/)
