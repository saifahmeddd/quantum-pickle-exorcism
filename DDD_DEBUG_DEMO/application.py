"""Application layer: DTOs, ports, and TODO use-case coordination."""

from dataclasses import dataclass  # DTOs contain data without business behavior.
from datetime import datetime  # Clock port returns a standard datetime.
from typing import Protocol  # Protocol defines dependency-inversion ports.

from domain import Task  # Application may depend inward on the domain.


@dataclass(frozen=True)
class CreateTaskDTO:
    """Input data required by the create-task use case."""

    title: str  # Primitive request data entering the application.


@dataclass(frozen=True)
class TaskDTO:
    """Primitive task data returned by application use cases."""

    id: str  # Public task identifier.
    title: str  # Public normalized title.
    created_at: str  # ISO string is safe for presentation output.

    @classmethod
    def from_entity(cls, task: Task) -> "TaskDTO":
        """Map the domain entity to data safe for an outer layer."""
        return cls(task.id, task.title.value, task.created_at.isoformat())


class TaskRepository(Protocol):
    """Port describing storage required by the application."""

    def save(self, task: Task) -> None: ...

    def get(self, task_id: str) -> Task | None: ...


class IdGenerator(Protocol):
    """Port for an external source of task identifiers."""

    def new_id(self) -> str: ...


class Clock(Protocol):
    """Port for an external source of current time."""

    def now(self) -> datetime: ...


class TaskNotFound(Exception):
    """Application error raised when the requested task is unavailable."""


class TaskService:
    """Application service coordinating create and get use cases."""

    def __init__(
        self,
        repository: TaskRepository,
        ids: IdGenerator,
        clock: Clock,
    ) -> None:
        self.repository = repository  # Inject storage through an application port.
        self.ids = ids  # Inject ID generation instead of constructing it here.
        self.clock = clock  # Inject time so the use case remains testable.

    def create(self, command: CreateTaskDTO) -> TaskDTO:
        """Coordinate creation without knowing presentation or storage details."""
        task_id = self.ids.new_id()  # Ask the injected infrastructure capability.
        now = self.clock.now()  # Ask the injected clock for the creation time.
        task = Task.create(task_id, command.title, now)  # Enter the domain.
        self.repository.save(task)  # Persist through the repository port.
        return TaskDTO.from_entity(task)  # Map domain output to an output DTO.

    def get(self, task_id: str) -> TaskDTO:
        """Return one stored task through the application output contract."""
        task = self.repository.get(task_id)  # Read through the injected port.
        if task is None:  # Application interprets an unavailable result.
            raise TaskNotFound("Task not found.")
        return TaskDTO.from_entity(task)  # Domain entity becomes output data.
