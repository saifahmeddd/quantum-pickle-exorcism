import TaskItem from './TaskItem.jsx';

export default function TaskList({ tasks, busyTaskId, onComplete, onRename, onDelete }) {
  if (tasks.length === 0) {
    return (
      <div className="empty-state">
        <h2>No tasks yet</h2>
        <p>Add your first task using the form above.</p>
      </div>
    );
  }

  return (
    <ul className="task-list">
      {tasks.map(task => (
        <TaskItem
          key={task.id}
          task={task}
          isBusy={busyTaskId === task.id}
          onComplete={onComplete}
          onRename={onRename}
          onDelete={onDelete}
        />
      ))}
    </ul>
  );
}
