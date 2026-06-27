import time
from openai import OpenAI
from app.core.config import PROMPT_TEMPLATE
from app.rag.rag_utils import load_docs, build_index
from app.evaluation.metrics import LLMCallRecord, calculate_cost


class RAGBase:

    def __init__(
        self,
        index,
        llm_client,
        prompt_template=PROMPT_TEMPLATE,
        model="gpt-4o-mini",
    ):
        self.index = index
        self.llm_client = llm_client
        self.prompt_template = prompt_template
        self.model = model


    def search(self, query, num_results=5):
        boost_dict = {}

        return self.index.search(
            query,
            num_results=num_results,
            boost_dict=boost_dict
        )


    def build_context(self, search_results):
        context = ""
        doc_template = """
                            Page title: {title}
                            Text: {text}
                        """.strip()

        for doc in search_results:
            context = context + doc_template.format(title=doc["metadata"]["page_title"],
                                                      text=doc["text"])

        return context


    def build_prompt(self, query, search_results):
        context = self.build_context(search_results)
        return self.prompt_template.format(
            question=query, context=context
        )


    def llm(self, prompt):

        response = self.llm_client.responses.create(
            model=self.model,
            input=[{'role': 'user', 'content': prompt}]
        )

        return response.output_text


    def rag(self, query):
        search_results = self.search(query)
        prompt = self.build_prompt(query, search_results)
        answer = self.llm(prompt)
        return answer


class RAGWithMetrics(RAGBase):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.last_call: LLMCallRecord | None = None

    def llm(self, prompt):
        start_time = time.time()
        response = self._call_llm(prompt)
        response_time = time.time() - start_time
        self._log_response(prompt, response, response_time)
        return response.output_text

    def _call_llm(self, prompt):
        response = self.llm_client.responses.create(
            model=self.model,
            input=[{'role': 'user', 'content': prompt}]
        )
        return response

    def _log_response(self, prompt, response, response_time):
        usage = response.usage
        cost = calculate_cost(self.model, usage)

        call_record = LLMCallRecord(
            model=self.model,
            prompt=prompt,
            answer=response.output_text,
            prompt_tokens=usage.input_tokens,
            completion_tokens=usage.output_tokens,
            total_tokens=usage.total_tokens,
            response_time=response_time,
            cost=cost,
        )

        print(call_record)
        self.last_call = call_record


if __name__ == '__main__':
    docs = load_docs()
    index = build_index(docs)
    openai_client = OpenAI()

    assistant = RAGBase(index=index, llm_client=openai_client)

    question = "What is a pod?"
    response = assistant.rag(question)
    print(response)