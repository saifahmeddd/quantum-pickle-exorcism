import { useState } from 'react';

/**
 * TaskItem presents one task and its Complete, Edit, and Delete actions.
 *
 * The task object is read-only data supplied by TaskList. The component keeps
 * only temporary editing details in local state: whether the edit form is open
 * and the draft title being typed. Permanent task changes are requested through
 * callbacks, because App owns the task collection and communicates with the API.
 *
 * isBusy disables this row while its request is running. A successful rename
 * closes the edit form; a failed rename keeps it open so the draft is not lost.
 */
export default function TaskItem({ task, isBusy, onComplete, onRename, onDelete }) {
  const [isEditing, setIsEditing] = useState(false);
  const [draftTitle, setDraftTitle] = useState(task.title);

  // completed_at is null for pending tasks and a timestamp for completed tasks.
  // Boolean converts those two shapes into a simple true/false display value.
  const isCompleted = Boolean(task.completed_at);

  async function handleRename(event) {
    event.preventDefault();
    const cleanTitle = draftTitle.trim();

    // Close without an API call when the draft is empty or unchanged.
    if (!cleanTitle || cleanTitle === task.title) {
      setDraftTitle(task.title);
      setIsEditing(false);
      return;
    }

    // App returns a success boolean after the PATCH request finishes.
    const renamed = await onRename(task.id, cleanTitle);
    if (renamed) setIsEditing(false);
  }

  function cancelEditing() {
    // Discard the draft and restore the last title received from App.
    setDraftTitle(task.title);
    setIsEditing(false);
  }

  return (
    <li className={`task-item ${isCompleted ? 'completed' : ''}`}>
      <div className="task-content">
        <span className="status-dot" aria-hidden="true" />

        {/* Local isEditing state chooses the edit form or read-only task text. */}
        {isEditing ? (
          <form className="edit-form" onSubmit={handleRename}>
            <label className="sr-only" htmlFor={`edit-${task.id}`}>Edit title</label>
            <input
              id={`edit-${task.id}`}
              value={draftTitle}
              onChange={event => setDraftTitle(event.target.value)}
              maxLength={120}
              autoFocus
              disabled={isBusy}
            />
            <button className="small" disabled={isBusy || !draftTitle.trim()}>Save</button>
            <button className="small secondary" type="button" onClick={cancelEditing}>
              Cancel
            </button>
          </form>
        ) : (
          <div>
            <p className="task-title">{task.title}</p>
            <p className="task-date">
              Created {new Date(task.created_at).toLocaleString()}
            </p>
          </div>
        )}
      </div>

      {!isEditing && (
        <div className="task-actions">
          {/* Completed tasks no longer need a Complete button. */}
          {!isCompleted && (
            <button className="small" disabled={isBusy} onClick={() => onComplete(task.id)}>
              Complete
            </button>
          )}
          <button className="small secondary" disabled={isBusy} onClick={() => setIsEditing(true)}>
            Edit
          </button>
          <button className="small danger" disabled={isBusy} onClick={() => onDelete(task.id)}>
            Delete
          </button>
        </div>
      )}
    </li>
  );
}
