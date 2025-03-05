from __future__ import annotations as _annotations

import json
import os
from dotenv import load_dotenv

import gradio as gr
from httpx import AsyncClient

from openai import AsyncOpenAI

# Import the agent and its dependency class
from agents.agents import simple_agent, PydanticAIDeps

# pydantic-ai Tools for streaming
from pydantic_ai.messages import ToolCallPart, ToolReturnPart


# Create and configure your Supabase client however you do in your project.

from supabase import Client
load_dotenv()
supabase_url = os.getenv("SUPABASE_URL")
supabase_key = os.getenv("SUPABASE_SERVICE_KEY")



supabase_client = Client(supabase_url, supabase_key)
openai_client = AsyncOpenAI(api_key=os.getenv("OPENAI_API"))



# Create the agent dependency instance
# Adjust the constructor if your PydanticAIDeps takes additional args/kwargs
deps = PydanticAIDeps(supabase=supabase_client, openai_client = openai_client)

# If you like, define a mapping of tool name => descriptive text for display
TOOL_TO_DISPLAY_NAME = {
    'retrieve_relevant_chunks': 'Retrieve Relevant Chunks',
    'list_documentation_pages': 'List Documentation Pages',
    'get_page_content': 'Get Page Content',
}


async def stream_from_agent(prompt: str, chatbot: list[dict], past_messages: list):
    """
    Sends the user's prompt to your RAG agent, streams back the response,
    and yields partial updates to the Gradio UI.
    """
    # Append user message to the conversation
    chatbot.append({'role': 'user', 'content': prompt})
    # Immediately yield an empty textbox (disabling input) so the UI doesn't block
    yield gr.Textbox(interactive=False, value=''), chatbot, gr.skip()

    # Run your custom agent in "stream" mode so you can yield partial tokens.
    async with simple_agent.run_stream(
        prompt, deps=deps, message_history=past_messages
    ) as result:
        for message in result.new_messages():
            # Check if the message is a request to call a tool or a return from a tool
            for part in message.parts:
                if isinstance(part, ToolCallPart):
                    if isinstance(part.args, str):
                        call_args = part.args
                    elif hasattr(part.args, 'args_json'):
                        call_args = part.args.args_json
                    elif hasattr(part.args, 'args_dict'):
                        call_args = json.dumps(part.args.args_dict)
                    else:
                        call_args = str(part.args)
                        
                    metadata = {
                        'title': f'🛠️ Using {TOOL_TO_DISPLAY_NAME.get(part.tool_name, part.tool_name)}',
                    }
                    if part.tool_call_id is not None:
                        metadata['id'] = part.tool_call_id

                    gr_message = {
                        'role': 'assistant',
                        'content': f'Parameters: {call_args}',
                        'metadata': metadata,
                    }
                    chatbot.append(gr_message)

                elif isinstance(part, ToolReturnPart):
                    # If the tool returned, display that returned content
                    for gr_message in chatbot:
                        if (
                            gr_message.get('metadata', {}).get('id', '')
                            == part.tool_call_id
                        ):
                            gr_message['content'] += f'\nOutput: {json.dumps(part.content)}'

            # Yield updated conversation each time we have new tool info
            yield gr.skip(), chatbot, gr.skip()

        # Once all tool calls have finished, stream the final assistant text response
        chatbot.append({'role': 'assistant', 'content': ''})
        async for token_text in result.stream_text():
            chatbot[-1]['content'] = token_text
            yield gr.skip(), chatbot, gr.skip()

        # Update past messages to include the entire conversation so far
        past_messages = result.all_messages()

        # Re-enable the user prompt
        yield gr.Textbox(interactive=True), gr.skip(), past_messages


async def handle_retry(chatbot, past_messages: list, retry_data: gr.RetryData):
    """
    Allows the user to retry from a given point in the conversation.
    """
    new_history = chatbot[: retry_data.index]
    previous_prompt = chatbot[retry_data.index]['content']
    past_messages = past_messages[: retry_data.index]

    async for update in stream_from_agent(previous_prompt, new_history, past_messages):
        yield update


def undo(chatbot, past_messages: list, undo_data: gr.UndoData):
    """
    Lets the user undo to a certain point in the conversation.
    """
    new_history = chatbot[: undo_data.index]
    past_messages = past_messages[: undo_data.index]
    return chatbot[undo_data.index]['content'], new_history, past_messages


def select_data(message: gr.SelectData) -> str:
    return message.value['text']


with gr.Blocks() as demo:
    gr.HTML(
        """
<div style="display: flex; justify-content: center; align-items: center; gap: 2rem; padding: 1rem; width: 100%">
    <img src="https://ai.pydantic.dev/img/logo-white.svg" style="max-width: 200px; height: auto">
    <div>
        <h1 style="margin: 0 0 1rem 0">Documentation RAG Assistant</h1>
        <h3 style="margin: 0 0 0.5rem 0">
            Ask questions about your documentation. 
        </h3>
    </div>
</div>
"""
    )

    past_messages = gr.State([])
    chatbot = gr.Chatbot(
        label='RAG Agent',
        type='messages',
        avatar_images=(None, 'https://ai.pydantic.dev/img/logo-white.svg'),
        examples=[
            {'text': 'What does the documentation say about the usage of the agent?'},
            {'text': 'How do I retrieve relevant chunks?'},
        ],
    )

    with gr.Row():
        prompt = gr.Textbox(
            lines=1,
            show_label=False,
            placeholder='Ask a question about the docs...',
        )

    generation = prompt.submit(
        stream_from_agent,
        inputs=[prompt, chatbot, past_messages],
        outputs=[prompt, chatbot, past_messages],
    )
    chatbot.example_select(select_data, None, [prompt])
    chatbot.retry(handle_retry, [chatbot, past_messages], [prompt, chatbot, past_messages])
    chatbot.undo(undo, [chatbot, past_messages], [prompt, chatbot, past_messages])

if __name__ == '__main__':
    demo.launch()
