import { Conversation } from '../types/chat';

export const INITIAL_CONVERSATIONS: Conversation[] = [
  {
    id: 'conv-react-19',
    title: 'React 19 & Compiler Optimization Guide',
    folderId: 'folder-tech',
    modelId: 'neurix',
    isPinned: true,
    isArchived: false,
    createdAt: '2026-08-04T10:15:00Z',
    updatedAt: '2026-08-05T11:20:00Z',
    messages: [
      {
        id: 'msg-101',
        conversationId: 'conv-react-19',
        role: 'user',
        content: 'Explain how React 19 handles automatic memoization and server actions compared to React 18. Provide a complete code example with TypeScript.',
        timestamp: '10:15 AM',
      },
      {
        id: 'msg-102',
        conversationId: 'conv-react-19',
        role: 'assistant',
        modelId: 'neurix',
        timestamp: '10:16 AM',
        reasoning: {
          thinkingTimeSeconds: 2.4,
          steps: [
            {
              id: 'step-1',
              title: 'Analyzing React 19 memoization mechanics',
              content: 'Inspecting React Compiler (Forget) output semantics for JSX element caching and dependency array elimination.',
            },
            {
              id: 'step-2',
              title: 'Comparing Server Actions & useActionState',
              content: 'Evaluating form pending states, optimistic updates via useOptimistic, and direct async mutation handlers.',
            },
          ],
        },
        citations: [
          {
            id: 'c-1',
            title: 'React 19 Release Notes - React Official Blog',
            url: 'https://react.dev/blog/2024/04/25/react-19',
            snippet: 'React 19 introduces action hooks, automatic memoization via the compiler, and native asset loading.',
            domain: 'react.dev',
          },
          {
            id: 'c-2',
            title: 'Understanding React Compiler Memoization Strategy',
            url: 'https://react.dev/learn/react-compiler',
            snippet: 'The React Compiler automatically memoizes values and functions created inside components.',
            domain: 'react.dev',
          },
        ],
        content: `### React 19 Automatic Memoization & Server Actions

React 19 fundamentally shifts how we approach performance optimization. Previously, developers manually wrapped components in \`useMemo\`, \`useCallback\`, and \`React.memo\`.

#### Key Improvements:
1. **Zero-Boilerplate Memoization**: The React Compiler automatically determines component re-render dependencies at build time.
2. **Form Actions & \`useActionState\`**: Form handling natively manages pending transitions, error handling, and optimistic mutations without extra loading state boilerplate.

---

### Interactive React 19 Code Example

Here is a clean implementation demonstrating **Form Actions** with optimistic state updates:

\`\`\`tsx
import React, { useActionState, useOptimistic, useTransition } from 'react';

interface Todo {
  id: string;
  text: string;
  completed: boolean;
}

export function TodoApp({ initialTodos }: { initialTodos: Todo[] }) {
  const [todos, setTodos] = React.useState<Todo[]>(initialTodos);

  // React 19 Optimistic UI Hook
  const [optimisticTodos, addOptimisticTodo] = useOptimistic(
    todos,
    (state, newText: string) => [
      ...state,
      { id: crypto.randomUUID(), text: newText, completed: false }
    ]
  );

  // Server Action implementation
  async function submitTodoAction(previousState: null, formData: FormData) {
    const title = formData.get('title') as string;
    if (!title.trim()) return null;

    // Optimistically update UI instantly
    addOptimisticTodo(title);

    // Simulate Server Action Mutation
    await new Promise((res) => setTimeout(res, 800));
    setTodos((prev) => [...prev, { id: Date.now().toString(), text: title, completed: false }]);
    return null;
  }

  const [state, formAction, isPending] = useActionState(submitTodoAction, null);

  return (
    <div className="p-6 max-w-md mx-auto bg-slate-900 text-white rounded-xl shadow-xl border border-slate-800">
      <h2 className="text-xl font-bold mb-4 flex items-center gap-2">
        <span>⚡ React 19 Task Stream</span>
      </h2>

      <form action={formAction} className="flex gap-2 mb-6">
        <input
          name="title"
          placeholder="What needs to be done?"
          className="flex-1 bg-slate-800 border border-slate-700 rounded-lg px-3 py-2 text-sm focus:outline-none focus:border-emerald-500 transition-colors"
          required
        />
        <button
          type="submit"
          disabled={isPending}
          className="bg-emerald-600 hover:bg-emerald-500 text-white font-medium px-4 py-2 rounded-lg text-sm transition-all disabled:opacity-50"
        >
          {isPending ? 'Adding...' : 'Add'}
        </button>
      </form>

      <ul className="space-y-2">
        {optimisticTodos.map((todo) => (
          <li
            key={todo.id}
            className="flex items-center justify-between bg-slate-800/60 p-3 rounded-lg border border-slate-700/50"
          >
            <span>{todo.text}</span>
            <span className="text-xs px-2 py-0.5 rounded bg-emerald-500/10 text-emerald-400 border border-emerald-500/20">
              Synced
            </span>
          </li>
        ))}
      </ul>
    </div>
  );
}
\`\`\`

#### Sequence Flow Diagram

\`\`\`mermaid
sequenceDiagram
    autonumber
    actor User
    participant Component as TodoApp UI
    participant Hook as useOptimistic
    participant Server as Server Action

    User->>Component: Submit new Todo form
    Component->>Hook: addOptimisticTodo(title)
    Hook-->>User: Immediate UI Update (Lag-free)
    Component->>Server: Execute Async Mutation
    Server-->>Component: Mutation Succeeded
    Component->>Hook: Reconcile Final Server State
\`\`\`

> **Pro Tip**: In React 19, you no longer need \`useCallback\` when passing functions to child components if the React Compiler is enabled in your \`vite.config.ts\`.`,
      },
    ],
  },
  {
    id: 'conv-logix-math',
    title: 'Logix — Mathematical Proof & LaTeX',
    folderId: null,
    modelId: 'logix',
    isPinned: false,
    isArchived: false,
    createdAt: '2026-08-05T08:30:00Z',
    updatedAt: '2026-08-05T09:00:00Z',
    messages: [
      {
        id: 'msg-201',
        conversationId: 'conv-logix-math',
        role: 'user',
        content: 'Derive the Gaussian Integral $\\int_{-\\infty}^{\\infty} e^{-x^2} dx = \\sqrt{\\pi}$ using polar coordinates and double integrals.',
        timestamp: '8:30 AM',
      },
      {
        id: 'msg-202',
        conversationId: 'conv-logix-math',
        role: 'assistant',
        modelId: 'logix',
        timestamp: '8:31 AM',
        reasoning: {
          thinkingTimeSeconds: 4.8,
          steps: [
            {
              id: 's-1',
              title: 'Evaluating Gaussian Integral strategy',
              content: 'Direct anti-derivative $e^{-x^2}$ is non-elementary. Must square the integral $I^2$ and transform into 2D Cartesian plane $(x, y)$.',
            },
            {
              id: 's-2',
              title: 'Coordinate Transformation to Polar Domain',
              content: 'Apply substitution $x = r \\cos\\theta$, $y = r \\sin\\theta$. Jacobian element $dx \\, dy = r \\, dr \\, d\\theta$. Range $r \\in [0, \\infty)$, $\\theta \\in [0, 2\\pi]$.',
            },
          ],
        },
        content: `### Mathematical Derivation: The Gaussian Integral

Let $I = \\int_{-\\infty}^{\\infty} e^{-x^2} dx$. Since the integration variable is a dummy variable, we can write:

$$ I^2 = \\left( \\int_{-\\infty}^{\\infty} e^{-x^2} dx \\right) \\left( \\int_{-\\infty}^{\\infty} e^{-y^2} dy \\right) = \\int_{-\\infty}^{\\infty} \\int_{-\\infty}^{\\infty} e^{-(x^2 + y^2)} dx dy $$

---

#### 1. Polar Coordinate Transformation

Using polar coordinates where $x^2 + y^2 = r^2$ and the area element $dx dy = r dr d\\theta$:

$$ I^2 = \\int_{0}^{2\\pi} d\\theta \\int_{0}^{\\infty} e^{-r^2} r dr $$

#### 2. Evaluating the Integrals

The angular integral evaluates directly:
$$ \\int_{0}^{2\\pi} d\\theta = 2\\pi $$

For the radial integral, substitute $u = r^2 \\implies du = 2r dr$:

$$ \\int_{0}^{\\infty} e^{-r^2} r dr = \\frac{1}{2} \\int_{0}^{\\infty} e^{-u} du = \\frac{1}{2} [-e^{-u}]_{0}^{\\infty} = \\frac{1}{2} (0 - (-1)) = \\frac{1}{2} $$

#### 3. Combining Results

$$ I^2 = 2\\pi \\cdot \\frac{1}{2} = \\pi $$

Taking the positive square root (since $e^{-x^2} > 0$ everywhere):

$$ I = \\sqrt{\\pi} $$

$$\\bbox[10px,border:2px solid #10A37F]{\\int_{-\\infty}^{\\infty} e^{-x^2} dx = \\sqrt{\\pi}}$$`,
      },
    ],
  },
];
