# dags/temporal_widget_dag.py
from __future__ import annotations

from datetime import datetime, timedelta
from typing import Any

from airflow.decorators import dag, task
from airflow.exceptions import AirflowException
from airflow.models.baseoperator import BaseOperator
from airflow.triggers.base import BaseTrigger, TriggerEvent
from airflow.utils.context import Context

from temporalio.client import Client


class TemporalWorkflowTrigger(BaseTrigger):
    def __init__(
        self,
        temporal_address: str,
        namespace: str,
        workflow_id: str,
        poll_interval_seconds: int = 5,
    ) -> None:
        super().__init__()
        self.temporal_address = temporal_address
        self.namespace = namespace
        self.workflow_id = workflow_id
        self.poll_interval_seconds = poll_interval_seconds

    def serialize(self) -> tuple[str, dict[str, Any]]:
        return (
            "dags.temporal_widget_dag.TemporalWorkflowTrigger",
            {
                "temporal_address": self.temporal_address,
                "namespace": self.namespace,
                "workflow_id": self.workflow_id,
                "poll_interval_seconds": self.poll_interval_seconds,
            },
        )

    async def run(self):
        import asyncio

        client = await Client.connect(self.temporal_address, namespace=self.namespace)
        handle = client.get_workflow_handle(self.workflow_id)

        while True:
            try:
                result = await handle.result()
                yield TriggerEvent(
                    {
                        "status": "success",
                        "workflow_id": self.workflow_id,
                        "result": result,
                    }
                )
                return
            except Exception as exc:
                text = str(exc)
                if "not found" in text.lower():
                    yield TriggerEvent(
                        {
                            "status": "error",
                            "workflow_id": self.workflow_id,
                            "message": text,
                        }
                    )
                    return

                await asyncio.sleep(self.poll_interval_seconds)


class TemporalWorkflowDeferrableOperator(BaseOperator):
    def __init__(
        self,
        *,
        temporal_address: str,
        namespace: str,
        task_queue: str,
        workflow_name: str,
        workflow_id: str,
        workflow_arg: dict[str, Any],
        poll_interval_seconds: int = 5,
        **kwargs: Any,
    ) -> None:
        super().__init__(**kwargs)
        self.temporal_address = temporal_address
        self.namespace = namespace
        self.task_queue = task_queue
        self.workflow_name = workflow_name
        self.workflow_id = workflow_id
        self.workflow_arg = workflow_arg
        self.poll_interval_seconds = poll_interval_seconds

    def execute(self, context: Context) -> None:
        import asyncio

        asyncio.run(self._start_workflow())

        self.defer(
            trigger=TemporalWorkflowTrigger(
                temporal_address=self.temporal_address,
                namespace=self.namespace,
                workflow_id=self.workflow_id,
                poll_interval_seconds=self.poll_interval_seconds,
            ),
            method_name="execute_complete",
            timeout=timedelta(hours=2),
        )

    async def _start_workflow(self) -> None:
        client = await Client.connect(self.temporal_address, namespace=self.namespace)
        await client.start_workflow(
            self.workflow_name,
            self.workflow_arg,
            id=self.workflow_id,
            task_queue=self.task_queue,
        )

    def execute_complete(
        self,
        context: Context,
        event: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        if not event:
            raise AirflowException("Temporal trigger returned no event")

        if event["status"] != "success":
            raise AirflowException(
                f"Temporal workflow {event.get('workflow_id')} failed: {event.get('message')}"
            )

        return event


@dag(
    start_date=datetime(2026, 1, 1),
    schedule=None,
    catchup=False,
    tags=["temporal", "deferrable"],
)
def temporal_widget_dag():
    @task
    def build_input() -> dict[str, Any]:
        return {
            "name": "airflow-widget",
            "description": "triggered by airflow",
            "authorization": None,
        }

    payload = build_input()

    TemporalWorkflowDeferrableOperator(
        task_id="run_temporal_workflow",
        temporal_address="temporal.example.com:7233",
        namespace="default",
        task_queue="widget-api-task-queue",
        workflow_name="WidgetApiWorkflow",
        workflow_id="airflow-widget-workflow-{{ ts_nodash }}",
        workflow_arg=payload,
        poll_interval_seconds=5,
    )


dag_obj = temporal_widget_dag()
