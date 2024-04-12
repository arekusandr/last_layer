import logging
from typing import Any, Callable, List

import last_layer

from langchain_core.language_models.llms import BaseLLM

logger = logging.getLogger(__name__)


def default_handler(text, risk: last_layer.RiskModel):
    if risk.passed:
        return
    logger.warning(f"Security risk: {risk} detected in text: {text}")


class LastLayerSecurity(BaseLLM):
    llm: BaseLLM
    handle_prompt_risk: Callable[str, last_layer.RiskModel] = default_handler
    handle_response_risk: Callable[str, last_layer.RiskModel] = default_handler
    ignore_opts: list[last_layer.Threat] = []

    @property
    def _llm_type(self) -> str:
        return "LastLayerSecurity"

    def _generate(
        self,
        prompts: List[str],
        **kwargs: Any,
    ) -> Any:
        """Run the LLM on the given prompts."""

        for prompt in prompts:
            risk = last_layer.scan_prompt(prompt)
            self.handle_prompt_risk(prompt, risk)
        result = self.llm._generate(prompts, **kwargs)

        for top_gen in result.generations:
            for gen in top_gen:
                risk = last_layer.scan_llm(gen.text)
                self.handle_response_risk(gen.text, risk)
        return result
