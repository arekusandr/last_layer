import unittest
from .llm import LastLayerSecurity


class TestScanPrompt(unittest.TestCase):
    @unittest.skip("Not implemented")
    def test_integration(self):
        # The line `from langchain_openai import OpenAI` is importing the `OpenAI` class from the
        # `langchain_openai` module. This allows the code to use the `OpenAI` class and its
        # functionalities within the current module or script.
        from langchain_contrib.llms.testing import FakeLLM

        secure_llm = LastLayerSecurity(
            llm=FakeLLM(verbose=True, sequenced_responses=["One", "Two", "Three"])
        )
        response = secure_llm.invoke(
            "Summarize this message: my name is Bob Dylan. My SSN is 123-45-6789."
        )
        print(f"{response=}")
