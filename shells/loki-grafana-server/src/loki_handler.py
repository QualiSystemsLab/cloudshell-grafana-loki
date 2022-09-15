import json

from typing import List, Dict

import time
import requests

InputLogValues = List[List[str]]
LogStreams = List[dict]
OutputLogData = List[dict]


class LokiHandlerException(Exception):
    pass


class LokiHandler:
    def __init__(self, host, port=3100, is_https=False):
        protocol = "https" if is_https else "http"
        self._base_url = f"{protocol}://{host}:{port}"

    @staticmethod
    def _validate_response(response: requests.Response):
        if not response.ok:
            raise LokiHandlerException(f"Failed Loki Request. Status: {response.status_code}, Message: {response.text}")

    @staticmethod
    def _get_epoch_nanoseconds():
        epoch_time = str((time.time_ns()))
        return epoch_time

    @staticmethod
    def _process_lines(log_lines: List[str]) -> InputLogValues:
        epoch_time = LokiHandler._get_epoch_nanoseconds()
        return [[epoch_time, log_line] for log_line in log_lines]

    @staticmethod
    def _process_dicts(log_dicts: List[Dict]) -> InputLogValues:
        epoch_time = LokiHandler._get_epoch_nanoseconds()
        return [[epoch_time, json.dumps(log_dict)] for log_dict in log_dicts]

    def health_check(self):
        url = f"{self._base_url}/ready"
        response = requests.get(url)
        self._validate_response(response)

    def _push_logs(self, stream_labels: dict, log_values: InputLogValues):
        url = f"{self._base_url}/loki/api/v1/push"
        headers = {'Content-type': 'application/json'}
        body = {
            "streams": [
                {
                    "stream": stream_labels,
                    "values": log_values
                }
            ]
        }
        response = requests.post(url, headers=headers, json=body)
        self._validate_response(response)

    def push_message_lines(self, stream_labels: dict, log_lines: List[str]):
        log_values = self._process_lines(log_lines)
        self._push_logs(stream_labels, log_values)

    def push_message_dicts(self, stream_labels: dict, log_dicts: List[Dict]):
        log_values = self._process_dicts(log_dicts)
        self._push_logs(stream_labels, log_values)

    def _query_range(self, query: str, start_nano: int = None, end_nano: int = None) -> LogStreams:
        """ not passing start and end_nano defaults from one hour ago to now """
        url = f"{self._base_url}/loki/api/v1/query_range"
        params = {
            "query": query
        }

        if start_nano:
            params["start"] = start_nano

        if end_nano:
            params["end"] = end_nano

        response = requests.get(url, params=params)
        self._validate_response(response)

        streams = response.json()["data"]["result"]
        return streams

    @staticmethod
    def _extract_data_from_stream(streams: LogStreams) -> OutputLogData:
        """ this helper assumes only one stream in result streams """
        target_data = next((x["values"] for x in streams), None)
        if not target_data:
            return []
        return [json.loads(x[1]) for x in target_data]

    @staticmethod
    def _build_job_query_with_filter(job_name: str, filter_str: str):
        """
        sample query filtering job on string contains{job="qualiserver"} |= "ERROR"'
        """
        query = f'{{job="{job_name}"}}'
        if filter_str:
            query += f' |= "{filter_str}"'
        return query

    def query_job(self, job_name: str, contains: str = None, start_nano: int = None, end_nano: int = None) -> OutputLogData:
        query = self._build_job_query_with_filter(job_name, contains)
        streams = self._query_range(query, start_nano, end_nano)
        return self._extract_data_from_stream(streams)


if __name__ == "__main__":
    STREAM_LABELS = {"Job": "Test Job", "App": "Test App"}
    MESSAGES = ["message 1", "message 2", "message 3"]
    LOG_DICTS = [
        {
            "id": 6,
            "message": "message 3",
            "source": "test script"
        },
        {
            "id": 5,
            "message": "message 2",
            "source": "test script"
        },
        {
            "id": 4,
            "message": "message 1",
            "source": "test script"
        }
    ]
    loki = LokiHandler("localhost")
    loki.health_check()
    # loki.push_message_lines(STREAM_LABELS, MESSAGES)
    # loki.push_message_dicts(STREAM_LABELS, LOG_DICTS)
    SANDBOX_ID = "c4894a77-e485-4984-8e5e-212a62c0658b"
    data = loki.query_job(job_name="TeamServerLog", contains_str="")
    pass
