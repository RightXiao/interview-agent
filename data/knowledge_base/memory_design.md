# Memory Design

Short-term memory stores recent conversation turns. It helps the system maintain local context during a session.

Long-term memory stores stable user information, such as target role, preferred tech stack, weak points, learning goals, and recent topics.

This project saves memory in local JSON files. That keeps the first version simple and easy to inspect.

Interview talking point: separate short-term context from long-term user profile, and update long-term memory only when the signal is clear.

