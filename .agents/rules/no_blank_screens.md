# No Blank Screens Policy

CRITICAL INSTRUCTION: You must ensure that the React application NEVER results in a blank screen after your changes.
- Always verify that all hooks (e.g., `useState`, `useEffect`) and components (e.g., icons, UI elements) are properly imported at the top of the file before using them.
- `npm run build` may succeed even if there is a runtime `ReferenceError` (like `useEffect is not defined`). You must manually verify imports or run a strict linter to catch these.
- A blank screen indicates a fatal crash in the root component (like `AppShell`). Exercise extreme caution when modifying layout files.
