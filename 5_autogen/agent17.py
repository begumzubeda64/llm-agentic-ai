from autogen_core import MessageContext, RoutedAgent, message_handler
from autogen_agentchat.agents import AssistantAgent
from autogen_agentchat.messages import TextMessage
from autogen_ext.models.openai import OpenAIChatCompletionClient
import messages
import random
from dotenv import load_dotenv

load_dotenv(override=True)

class Agent(RoutedAgent):

    system_message = """
    You are a tech-savvy entrepreneur focused on the fashion industry. Your task is to devise innovative fashion solutions using Agentic AI or to enhance existing concepts. 
    Your personal interests lie in e-commerce and personalized styling solutions. 
    You are keen on concepts that leverage technology for sustainability and consumer engagement.
    You are less inclined toward ideas that do not push for a creative change in the shopping experience. 
    You possess a vibrant personality, are sociable, and have a knack for visual aesthetics. However, you can be overwhelmed by choices, leading to indecisiveness at times. 
    You should share your fashion ideas in a stylish, engaging manner that resonates with potential investors and consumers alike.
    """

    CHANCES_THAT_I_BOUNCE_IDEA_OFF_ANOTHER = 0.4

    def __init__(self, name) -> None:
        super().__init__(name)
        model_client = OpenAIChatCompletionClient(model="gpt-4o-mini", temperature=0.75)
        self._delegate = AssistantAgent(name, model_client=model_client, system_message=self.system_message)

    @message_handler
    async def handle_message(self, message: messages.Message, ctx: MessageContext) -> messages.Message:
        print(f"{self.id.type}: Received message")
        text_message = TextMessage(content=message.content, source="user")
        response = await self._delegate.on_messages([text_message], ctx.cancellation_token)
        idea = response.chat_message.content
        if random.random() < self.CHANCES_THAT_I_BOUNCE_IDEA_OFF_ANOTHER:
            recipient = messages.find_recipient()
            message = f"I’m excited to share my fashion innovation idea! It might not be your usual area, but I’d love your feedback: {idea}"
            response = await self.send_message(messages.Message(content=message), recipient)
            idea = response.content
        return messages.Message(content=idea)