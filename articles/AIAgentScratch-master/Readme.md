# AIAgentScratch

## AIAgent.py

`AIAgent.py` implements a structured Plan-and-Execute AI agent. This agent is designed to break down complex user questions into sequential, simple tasks. It then uses a set of available tools to execute these tasks and synthesizes a final, concise answer based on the results. The agent leverages the OpenAI API for its planning and synthesis capabilities.

### How it Works
1.  **Planning:** The agent first plans the tasks by breaking down the user's prompt into a list of actionable steps.
2.  **Tool Execution:** It then identifies and calls the appropriate tools from its `available_functions` to fulfill each task, handling dependencies between tasks.
3.  **Synthesis:** Finally, it synthesizes the results from the tool executions and the original user prompt to provide a comprehensive answer.

### Setup and Running

1.  **OpenAI API Key:**
    The agent requires an OpenAI API key to function. Set your API key as an environment variable named `OPENAI_API_KEY`. You can obtain your API key from [https://platform.openai.com/account/api-keys](https://platform.openai.com/account/api-keys).

    **For Windows:**
    ```cmd
    set OPENAI_API_KEY=your_api_key_here
    ```
    **For macOS/Linux:**
    ```bash
    export OPENAI_API_KEY=your_api_key_here
    ```
    Replace `your_api_key_here` with your actual OpenAI API key.

2.  **Run the Agent:**
    Once the API key is set, you can run the `AIAgent.py` script. The script will execute the agent with a predefined user prompt.

    ```bash
    python AIAgent.py
    ```

    The output, including the agent's internal planning and execution steps, will be logged to the console.
