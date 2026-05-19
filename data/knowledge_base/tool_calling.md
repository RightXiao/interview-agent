# Tool Calling

Tool calling allows an agent to use deterministic code for tasks that should not be handled only by the language model. Examples include searching a knowledge base, reading memory, updating profile data, generating study plans, and exporting PDFs.

This project uses a tool registry so tools can be found and called by name. That makes the tool layer visible and easy to explain.

Interview talking point: tools give the agent reliable actions and connect the model to the outside world.

