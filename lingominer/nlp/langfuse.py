from langfuse import Langfuse
from langfuse.decorators import langfuse_context, observe
from langfuse.model import ChatPromptClient

langfuse = Langfuse()