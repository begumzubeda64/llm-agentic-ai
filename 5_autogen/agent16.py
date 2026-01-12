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
    You are a digital marketing guru. Your task is to generate innovative marketing strategies using Agentic AI or enhance existing campaigns.
    Your personal interests are in these sectors: E-commerce, Social Media.
    You are drawn to ideas that leverage the latest technology for engagement.
    You prefer strategies that promote brand loyalty rather than just one-time sales.
    You are resourceful, energetic, and enjoy exploring unconventional marketing avenues. 
    Your weaknesses: you sometimes overlook the importance of data analytics and can be too focused on creativity over strategy.
    You should communicate your marketing ideas clearly and persuasively, inspiring others to take action.
    """

    CHANCES_THAT_I_BOUNCE_IDEA_OFF_ANOTHER = 0.5

    def __init__(self, name) -> None:
        super().__init__(name)
        model_client = OpenAIChatCompletionClient(model="gpt-4o-mini", temperature=0.7)
        self._delegate = AssistantAgent(name, model_client=model_client, system_message=self.system_message)

    @message_handler
    async def handle_message(self, message: messages.Message, ctx: MessageContext) -> messages.Message:
        print(f"{self.id.type}: Received message")
        text_message = TextMessage(content=message.content, source="user")
        response = await self._delegate.on_messages([text_message], ctx.cancellation_token)
        idea = response.chat_message.content
        if random.random() < self.CHANCES_THAT_I_BOUNCE_IDEA_OFF_ANOTHER:
            recipient = messages.find_recipient()
            message = f"Here is my marketing strategy idea. It may not be your specialty, but please refine it and improve it. {idea}"
            response = await self.send_message(messages.Message(content=message), recipient)
            idea = response.content
        return messages.Message(content=idea)