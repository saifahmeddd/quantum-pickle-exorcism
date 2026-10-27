import { useState } from 'react';

/**
 * TaskForm collects the title for one new task.
 *
 * The title is local state because it is an unfinished input value used only by
 * this form. The saved task collection remains in App. On submission, TaskForm
 * trims the title and calls onCreate. App dispatches the Redux create-task
 * thunk and returns true only when the backend successfully creates the task.
 *
 * isSubmitting disables the form during that request. The title is cleared
 * after success and kept after failure so the user can try again.
 */
export default function TaskForm({ isSubmitting, onCreate }) {
  const [title, setTitle] = useState('');

  async function handleSubmit(event) {
    // Keep the page from reloading when this HTML form is submitted.
    event.preventDefault();
    const cleanTitle = title.trim();

    // Do not send empty or whitespace-only titles to App.
    if (!cleanTitle) return;

    // The callback moves the event upward to App, which owns the task list.
    const created = await onCreate(cleanTitle);
    // Keep the user's input after failure, but clear it after a successful POST.
    if (created) setTitle('');
  }

  return (
    <form className="task-form" onSubmit={handleSubmit}>
      <label className="sr-only" htmlFor="new-task-title">New task title</label>
      <input
        id="new-task-title"
        value={title}
        onChange={event => setTitle(event.target.value)}
        placeholder="What needs to be done?"
        maxLength={120}
        disabled={isSubmitting}
      />
      {/* Button state is calculated from props and local input state. */}
      <button className="primary" disabled={isSubmitting || !title.trim()}>
        {isSubmitting ? 'Adding…' : 'Add task'}
      </button>
    </form>
  );
}
