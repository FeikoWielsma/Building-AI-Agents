from openai import OpenAI
import openai
import logging
import json
import os
from tools import tools_schema, available_functions

client = OpenAI()

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    datefmt='%H:%M:%S'
)
logger = logging.getLogger(__name__)

class Agent():
    def __init__(self, available_tools_dict):
        self.plan = False # checks if the agent has a plan
        self.system_prompt = "You are a useful assistant"
        self.available_tools_dict = available_tools_dict

    # Structured Plan-and-Execute Agent
    def run(self, user_prompt: str, tools: list):
        '''This functions is the orchestrator'''
        print(f"\n--- STEP 1 PLAN TASKS---")
        action_plan = self.__plan_tasks(user_prompt)
        print(f"\n--- STEP 2 EXECUTE TASKS ---")
        execution_results = self.__plan_tools(action_plan, tools)
        print(f"\n--- STEP 3 CREATE ANSWER ---")
        final_answer = self.__synthesize_answer(user_prompt, execution_results)
        return final_answer
    
    # The Reasoning 
    @staticmethod #function never needs to access data stored inside the class
    def call_llm(system_prompt: str, user_prompt: str,
                 model: str = "gpt-4.1-nano", 
                 temperature: float = 0.7,
                 json_output: bool = False):
        
        max_retries = 3
        attempts = 0

        while attempts < max_retries:
            try:
                response = client.responses.create(
                    model=model,
                    temperature=temperature,
                    input=[
                        {"role": "system", "content": system_prompt},
                        {"role": "user", "content": user_prompt},
                    ],
                )
                
                raw_text = response.output_text
                if not json_output:
                    return raw_text  # Return plain text if JSON isn't requested
                try:
                    return json.loads(raw_text)   # Attempt to parse JSON
                except json.JSONDecodeError as e: # Catch JSON errors
                    attempts += 1
                    logger.warning(f"Attempt {attempts} JSON creation failed: {e}. Retrying...")                    
            except Exception as e:  # Catch API errors (timeouts, 500s, rate limits)
                attempts += 1
                logger.error(f"Attempt {attempts} API call failed: {e}. Retrying...")
        # Fail gracefully after max retries
        raise RuntimeError(f"Failed to get a valid response after {max_retries} attempts.")


    # The Brain: We ask a LLM to plan
    def __plan_tasks(self, user_prompt: str)-> json:
        '''This plans the task the LLM will do'''
        planner_system_prompt = (
            "You are a sophisticated planner Agent. "
            "Your job is to break down complex user questions into sequential, simple tasks. "
            "Return a JSON object with a single key  "
            " - 'tasks': list[string] #which contains a list of strings."
        )
        
        action_plan = self.call_llm(planner_system_prompt, user_prompt, json_output=True)
        logger.info(f'The action plan is: {action_plan}')
        self.plan = True
        return action_plan
    
    # The Environment: this is where the work happens
    def __plan_tools(self, action_plan: list, tools: list) -> json:
        '''Calls the functions that are necessary to fullfill the tasks'''
        execution_results = []
        response = ""
        execution_system_prompt  = (
            "You are a sophisticated planner Agent. "
            "Your job is to find the correct given tools to the system to solve the given tasks."
            "The available tools and the task you will get from the user"
            "If no tools fit to Task write None"
            "Return a JSON object with a single key  "
            " - 'id: int #unique id to identify the task "
            " - 'task': {task}"
            " - 'function': string # name of the tool"
            " - 'properties: list # properties to execute the function"
            " - 'dependencies': list # id's if the needed results of other tasks"
        )
        for task in action_plan["tasks"]:
            logger.info(f"******************Execute Task: {task} *******************")
            user_prompt = (f"I have the following task to do: {task}"  
                           f"I can use the following tools: {tools} to solve the taks "
                            "Tell me the correct tool to use for a given task"
                           f"Here is the full list of tasks {action_plan}"
                           F"Here are the executions that are already done {execution_results} take the results of tasks have dependencies."
            )
           
            response = self.call_llm(execution_system_prompt ,user_prompt, json_output=True)
            kwargs = response["properties"]
            func_name = response["function"]
            # Execute the Tools we have available to solve the task
            if func_name in self.available_tools_dict:
                logger.info(f"Execute Function {func_name} with {kwargs}...")
                function_to_call = self.available_tools_dict[func_name]
                result = function_to_call(*kwargs) 
                response["result"] = result # Add Result to the task. 
                logger.info(f"Result of {func_name}: {result}")
            execution_results.append(response)
        logger.info(f"******************Execution Results: {task} *******************")
        logger.info(f'The execution result are: {execution_results}')
        return execution_results
    
    def __synthesize_answer(self, user_prompt, execution_results) -> str:
        synthesis_prompt = (
            "You are a helpful assistant. You have been given a user question"
            "and a set of execution results from various tools. "
            "Your goal is to provide a final, concise answer based on these results."
            "Check if the task of the user is fullfilled."
            "If not let him know that you don't have the tools to fullfill the tasks"
        )
        
        # We combine the history into a single 'context' string for the LLM
        context = f"User Question: {user_prompt}\nResults: {execution_results}"
        return self.call_llm(synthesis_prompt, context)


system_prompt = "You are a usefull assistant"
user_prompt = "What is the combine mass of Earth and jupiter"
# Try: 
#user_prompt = "Please book me a flight from Munich to London on 22.02.2026 and book my a hotel close to the city center with a gym."

if os.environ.get("OPENAI_API_KEY"):
    my_Agent = Agent(available_functions) # create Agent
    response = my_Agent.run(user_prompt, tools_schema)
    logger.info(f"Output: {response}.")
else:
    print("No OPENAI_API_KEY is set. You can find your API key at https://platform.openai.com/account/api-keys.")


