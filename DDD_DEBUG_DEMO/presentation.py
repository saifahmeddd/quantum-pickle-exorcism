"""Presentation layer and executable composition root for the four-file demo."""

from dataclasses import asdict  # Converts output DTOs to response dictionaries.

from application import CreateTaskDTO, TaskDTO, TaskService  # Use application API.
from infrastructure import FixedClock, InMemoryTaskRepository, SequentialIdGenerator


def validate_create_request(request: object) -> str:
    """Validate only the incoming request shape, not domain business rules."""
    if not isinstance(request, dict) or set(request) != {"title"}:
        raise ValueError("Request must contain only a title field.")
    if not isinstance(request["title"], str):
        raise ValueError("Request title must be text.")
    return request["title"]  # Return transport data after shape validation.


def task_view(task: TaskDTO) -> dict:
    """Convert an application output DTO into a client response."""
    return asdict(task)  # Presentation creates a JSON-ready dictionary.


def create_task_controller(request: object, service: TaskService) -> dict:
    """Map a create request to the create-task application use case."""
    title = validate_create_request(request)  # Validate presentation input.
    command = CreateTaskDTO(title=title)  # Create application input DTO.
    created_task = service.create(command)  # Call the application use case.
    return task_view(created_task)  # Map application output to response data.


def get_task_controller(task_id: str, service: TaskService) -> dict:
    """Map a get request to the get-task application use case."""
    found_task = service.get(task_id)  # Ask application for output DTO.
    return task_view(found_task)  # Convert DTO to response data.


def main() -> None:
    """Wire dependencies and simulate one create request followed by one get."""
    repository = InMemoryTaskRepository()  # Choose concrete storage at outer edge.
    ids = SequentialIdGenerator()  # Choose concrete ID provider at outer edge.
    clock = FixedClock()  # Choose concrete clock at outer edge.
    service = TaskService(repository, ids, clock)  # Dependency injection happens.

    create_request = {"title": "  Learn DDD with a debugger  "}  # Client input.
    create_response = create_task_controller(create_request, service)  # POST flow.
    print("CREATE RESPONSE:", create_response)  # Simulated response to client.

    get_request_id = create_response["id"]  # Client selects the created resource.
    get_response = get_task_controller(get_request_id, service)  # GET flow.
    print("GET RESPONSE:", get_response)  # Simulated response to client.


if __name__ == "__main__":
    main()  # Start the demonstration when this file is executed.
