"""Cron tool for scheduling reminders and tasks."""

from typing import Any

from nanobot.agent.tools.base import Tool
from nanobot.cron.service import CronService
from nanobot.cron.types import CronSchedule


class CronTool(Tool):
    """Tool to schedule reminders and recurring tasks."""

    def __init__(self, cron_service: CronService):
        self._cron = cron_service
        self._channel = ""
        self._chat_id = ""

    def set_context(self, channel: str, chat_id: str) -> None:
        """Set the current session context for delivery."""
        self._channel = channel
        self._chat_id = chat_id

    @property
    def name(self) -> str:
        return "cron"

    @property
    def description(self) -> str:
        return "Schedule reminders and recurring tasks. Actions: add, list, remove, update."

    @property
    def parameters(self) -> dict[str, Any]:
        return {
            "type": "object",
            "properties": {
                "action": {
                    "type": "string",
                    "enum": ["add", "list", "remove", "update"],
                    "description": "Action to perform",
                },
                "job_id": {"type": "string", "description": "Job ID (for remove/update)"},
                "message": {"type": "string", "description": "Task message (for add/update)"},
                "every_seconds": {
                    "type": "integer",
                    "description": "Interval in seconds (for recurring tasks)",
                },
                "cron_expr": {
                    "type": "string",
                    "description": "Cron expression like '0 9 * * *' (for scheduled tasks)",
                },
                "tz": {
                    "type": "string",
                    "description": "IANA timezone for cron expressions (e.g. 'America/Vancouver')",
                },
                "at": {
                    "type": "string",
                    "description": "ISO datetime for one-time execution (e.g. '2026-02-12T10:30:00')",
                },
                "deliver": {
                    "type": "boolean",
                    "description": "Whether to deliver the result to user (for add/update)",
                },
                "enabled": {
                    "type": "boolean",
                    "description": "Enable or disable the job (for update)",
                },
                "name": {"type": "string", "description": "Job name (for add/update)"},
            },
            "required": ["action"],
        }

    async def execute(
        self,
        action: str,
        message: str = "",
        every_seconds: int | None = None,
        cron_expr: str | None = None,
        tz: str | None = None,
        at: str | None = None,
        job_id: str | None = None,
        deliver: bool | None = None,
        enabled: bool | None = None,
        name: str | None = None,
        **kwargs: Any,
    ) -> str:
        if action == "add":
            return self._add_job(name, message, every_seconds, cron_expr, tz, at, deliver)
        elif action == "list":
            return self._list_jobs()
        elif action == "remove":
            return self._remove_job(job_id)
        elif action == "update":
            return self._update_job(
                job_id, name=name, message=message or None,
                deliver=deliver, enabled=enabled,
                every_seconds=every_seconds, cron_expr=cron_expr, tz=tz, at=at,
            )
        return f"Unknown action: {action}"

    def _build_schedule(
        self,
        every_seconds: int | None,
        cron_expr: str | None,
        tz: str | None,
        at: str | None,
    ) -> tuple[CronSchedule | None, bool, str | None]:
        """Build a CronSchedule. Returns (schedule, delete_after, error)."""
        if tz and not cron_expr:
            return None, False, "Error: tz can only be used with cron_expr"
        if tz:
            from zoneinfo import ZoneInfo
            try:
                ZoneInfo(tz)
            except (KeyError, Exception):
                return None, False, f"Error: unknown timezone '{tz}'"

        if every_seconds:
            return CronSchedule(kind="every", every_ms=every_seconds * 1000), False, None
        elif cron_expr:
            return CronSchedule(kind="cron", expr=cron_expr, tz=tz), False, None
        elif at:
            from datetime import datetime
            dt = datetime.fromisoformat(at)
            at_ms = int(dt.timestamp() * 1000)
            return CronSchedule(kind="at", at_ms=at_ms), True, None
        return None, False, None

    def _add_job(
        self,
        name: str | None,
        message: str,
        every_seconds: int | None,
        cron_expr: str | None,
        tz: str | None,
        at: str | None,
        deliver: bool | None,
    ) -> str:
        if not message:
            return "Error: message is required for add"
        if not self._channel or not self._chat_id:
            return "Error: no session context (channel/chat_id)"

        schedule, delete_after, err = self._build_schedule(every_seconds, cron_expr, tz, at)
        if err:
            return err
        if not schedule:
            return "Error: either every_seconds, cron_expr, or at is required"

        job = self._cron.add_job(
            name=name or message[:30],
            schedule=schedule,
            message=message,
            deliver=deliver if deliver is not None else True,
            channel=self._channel,
            to=self._chat_id,
            delete_after_run=delete_after,
        )
        return f"Created job '{job.name}' (id: {job.id})"

    def _list_jobs(self) -> str:
        jobs = self._cron.list_jobs()
        if not jobs:
            return "No scheduled jobs."
        lines = []
        for j in jobs:
            parts = [f"id: {j.id}", j.schedule.kind]
            if j.schedule.expr:
                parts.append(f"expr: {j.schedule.expr}")
            if j.schedule.every_ms:
                parts.append(f"every: {j.schedule.every_ms // 1000}s")
            parts.append(f"deliver: {j.payload.deliver}")
            lines.append(f"- {j.name} ({', '.join(parts)})")
        return "Scheduled jobs:\n" + "\n".join(lines)

    def _remove_job(self, job_id: str | None) -> str:
        if not job_id:
            return "Error: job_id is required for remove"
        if self._cron.remove_job(job_id):
            return f"Removed job {job_id}"
        return f"Job {job_id} not found"

    def _update_job(
        self,
        job_id: str | None,
        *,
        name: str | None,
        message: str | None,
        deliver: bool | None,
        enabled: bool | None,
        every_seconds: int | None,
        cron_expr: str | None,
        tz: str | None,
        at: str | None,
    ) -> str:
        if not job_id:
            return "Error: job_id is required for update"

        schedule = None
        if every_seconds or cron_expr or at:
            schedule, _, err = self._build_schedule(every_seconds, cron_expr, tz, at)
            if err:
                return err

        job = self._cron.update_job(
            job_id,
            name=name,
            message=message,
            deliver=deliver,
            enabled=enabled,
            schedule=schedule,
        )
        if not job:
            return f"Job {job_id} not found"
        return f"Updated job '{job.name}' (id: {job.id})"
