import TaskItem from './TaskItem.jsx';

/**
 * TaskList renders the collection supplied by App.
 *
 * It has no local state: it either shows an empty message or maps every task
 * object to one TaskItem component. The action callbacks are passed through so
 * each TaskItem can report user actions back to App. busyTaskId identifies the
 * row whose API request is currently running.
 *
 * task.id is used as React's key. The stable key lets React match each TaskItem
 * with the same task after items are added, removed, or reordered.
 */
export default function TaskList({ tasks, busyTaskId, onComplete, onRename, onDelete }) {
  // An early return makes the empty collection a separate, simple UI state.
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
      {/* map converts each data object into one TaskItem component. */}
      {/* The database ID is a stable key; busyTaskId disables only one row. */}
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
